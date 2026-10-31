#!/usr/bin/env bash

set -e -o pipefail

KERNEL_KIT_DIR="/bottlerocket-kernel-kit"
MICROCODE_DIR="${KERNEL_KIT_DIR}/packages/microcode"

# Usage information
usage() {
    cat <<EOF
Usage: $0

This script generates and validates full kernel configurations for all available
kernel versions in the Bottlerocket kernel kit.

IMPORTANT: This script is designed to run inside the Bottlerocket SDK container
and should typically be invoked via the Makefile target:

    make full-config

Running this script directly outside the SDK container will fail because it
requires the proper build environment and mounted paths.

The script will:
1. Discover all kernel-* packages with available RPMs
2. Extract and patch kernel sources
3. Merge Bottlerocket-specific configurations
4. Generate full configuration files
5. Validate that all required configs are present

EOF
}

# Common error handling
bail() {
    if [[ $# -gt 0 ]]; then
        >&2 echo "Error: $*"
    fi
    exit 1
}

# Get the config-full filename for a given kernel version and architecture
get_kernel_config_file_name() {
    local majorminor="$1"
    local arch="$2"
    if [[ "${majorminor}" == "6.18" ]]; then
        echo "config-full-bottlerocket-${arch}-on-$(uname -m)"
    else
        echo "config-full-bottlerocket-${arch}"
    fi
}

# Fetch the sources of the configured kernels
fetch_sources() {
    # Use the tools available in the Bottlerocket SDK (curl, grep , sed) since
    # the running container is configured with the caller's UID which prevents
    # from installing tools at /home/builder/
    for kernel_dir in "${KERNEL_KIT_DIR}/packages"/kernel-*; do
        pushd "${kernel_dir}" || bail "Unable to enter kernel directory '${kernel_dir}'"
        # Skip packages that declare no external 'url =' sources (e.g.
        # kernel-6.18-shared-configs)
        if grep -q 'url =' "Cargo.toml"; then
            grep 'url =' "Cargo.toml" | while IFS= read -r url; do
                url=$(echo "${url#*\"}" | cut -d '"' -f 1)
                echo "Fetching: ${url}"
                curl -LOs "${url}"
            done
        fi
        popd || bail "Could not exit kernel directory '${kernel_dir}'"
    done
}

# Resolve where a kernel package's base config-bottlerocket{,-<arch>} fragments
# live. They may be shipped by a shared package
# (kernel-<majorminor>-shared-configs) and installed into the build sysroot
# rather than duplicated in the kernel package.
resolve_base_config_dir() {
    local kernel_path="$1" majorminor="$2"
    local shared_dir="${KERNEL_KIT_DIR}/packages/kernel-${majorminor}-shared-configs"
    if [[ ! -f "${kernel_path}/config-bottlerocket" && -d "${shared_dir}" ]]; then
        echo "${shared_dir}"
    else
        echo "${kernel_path}"
    fi
}

# Generate merged kernel configs for each architecture.
generate_kernel_configs() {
    local version="$1"
    local kernel_path="$2"
    local microcode_file="$3"
    local majorminor="$4"
    # The base config-bottlerocket{,-${arch}} fragments may be provided by a
    # shared package (kernel-${majorminor}-shared-configs) rather than living in
    # the kernel package itself. Fall back to that package when they are absent.
    local base_cfg_dir
    base_cfg_dir=$(resolve_base_config_dir "${kernel_path}" "${majorminor}")
    for arch in "x86_64" "aarch64"; do
        br_cfg="${base_cfg_dir}/config-bottlerocket"
        br_cfg_arch="${base_cfg_dir}/config-bottlerocket-${arch}"
        microcode_cfg="${MICROCODE_DIR}/${microcode_file}"
        config_filename=$(get_kernel_config_file_name "${majorminor}" "${arch}")

        pushd "linux-${version}" || bail "Could not move into linux-${version}"

        if [ "${arch}" = "aarch64" ]; then
            karch="arm64"
            script_args=("../config-${arch}" "${br_cfg}" "${br_cfg_arch}")
        elif [ "${arch}" = "x86_64" ]; then
            karch="x86"
            if [[ -n "${microcode_file}" ]]; then
                script_args=("../config-${arch}" "${microcode_cfg}" "${br_cfg}" "${br_cfg_arch}")
            else
                script_args=("../config-${arch}" "${br_cfg}" "${br_cfg_arch}")
            fi
        fi

        # Packages with an extra config overlay (e.g. kernel-6.18-microvm's
        # config-microvm) merge it last, matching that package spec's %prep.
        if [[ -f "${kernel_path}/config-microvm" ]]; then
            script_args+=("${kernel_path}/config-microvm")
        fi

        ARCH=${karch} \
            CROSS_COMPILE=/usr/bin/${arch}-bottlerocket-linux-gnu- \
            KCONFIG_CONFIG=bottlerocket_${arch}_defconfig \
            ./scripts/kconfig/merge_config.sh "${script_args[@]}"

        mv -f "bottlerocket_${arch}_defconfig" "${kernel_path}/${config_filename}" || bail "Failed to create ${config_filename}"
        popd || bail "Could not move around - 'popd' failed in merge_config loop. Lets stop before we break anything further."
    done
}

# Function to merge kernel configurations for a specific kernel version
merge_kernel_configs() {
    local version="$1"
    local majorminor="$2"
    local tmpdir="$3"
    local kernel_package_dir="$4"

    readarray -t br_patches < <(find "${kernel_package_dir}" -maxdepth 1 -name "*.patch")

    if [[ "${majorminor}" == "6.18" ]]; then
        spec_file="kernel6.18.spec"
        microcode_file="config-microcode-6-18"
    elif [[ "${majorminor}" == "6.12" ]]; then
        spec_file="kernel6.12.spec"
        microcode_file="config-microcode-6-12"
    else
        spec_file="kernel.spec"
        microcode_file="config-microcode"
    fi

    # The microvm flavor embeds no CPU microcode (a guest cannot apply it), so it
    # skips the microcode config fragment entirely. An empty microcode_file tells
    # generate_kernel_configs to leave it out of the x86_64 merge.
    if [[ "$(basename "${kernel_package_dir}")" == *-microvm ]]; then
        microcode_file=""
    fi

    local kernel_path="${kernel_package_dir}"

    pushd "${tmpdir}" || bail "Unable to enter temporary directory"

    rpm2cpio kernel-source.rpm | cpio -iu {,./}linux-"${version}".tar{,.xz} {,./}config-x86_64 {,./}config-aarch64 {,./}"*.patch" {,./}"${spec_file}"

    # Upstream source is either xz compressed tarball or plain tarball
    if [ -f "./linux-${version}.tar" ]; then
        tar -xof linux-"${version}".tar
        rm linux-"${version}".tar
    else
        tar -xof linux-"${version}".tar.xz
        rm linux-"${version}".tar.xz
    fi

    # Find upstream patch ordering based on the upstream SRPM so we can apply in that order
    readarray -t patches < <(grep -P "^Patch\d+" "${spec_file}" | sort -n -k1.6 | grep -oP "^Patch\d+: \K.*\.patch$" "${spec_file}")

    # Enter the source directory extracted from the tarball and patch
    pushd "linux-${version}" || bail "Could not move into linux-${version}"

    # Patches from the upstream
    for patch in "${patches[@]}"; do
        patch -p1 <"../$patch"
    done

    # Patches from bottlerocket
    for patch in "${br_patches[@]}"; do
        echo "Applying bottlerocket patch ${patch}"
        patch -p1 <"$patch"
    done

    popd || bail "Could not move around - 'popd' back to /work failed. Lets stop before we break anything further."

    generate_kernel_configs "${version}" "${kernel_path}" "${microcode_file}" "${majorminor}"

    popd || bail "Could not return from temporary directory"
}

# Function to validate kernel configurations (similar to validate_config.sh)
validate_kernel_configs() {
    local version="$1"
    local majorminor="$2"
    local kernel_path="$3"
    local errors=0
    # The base config fragments may live in kernel-${majorminor}-shared-configs;
    # the generated config-full file always lives in the kernel package itself.
    local base_cfg_dir
    base_cfg_dir=$(resolve_base_config_dir "${kernel_path}" "${majorminor}")

    for arch in x86_64 aarch64; do
        echo "=== Validating kernel-${majorminor} ${arch} ==="

        # Check if files exist
        if [[ ! -f "${base_cfg_dir}/config-bottlerocket" ]]; then
            echo "❌ Missing config-bottlerocket"
            ((++errors))
            continue
        fi
        if [[ ! -f "${base_cfg_dir}/config-bottlerocket-${arch}" ]]; then
            echo "❌ Missing config-bottlerocket-${arch}"
            ((++errors))
            continue
        fi
        local config_filename
        config_filename=$(get_kernel_config_file_name "${majorminor}" "${arch}")
        if [[ ! -f "${kernel_path}/${config_filename}" ]]; then
            echo "❌ Missing ${config_filename}"
            ((++errors))
            continue
        fi

        # Extract config lines (ignoring comments by default to avoid issues with removed kernel options)
        local common_configs
        common_configs=$(grep "^CONFIG_" "${base_cfg_dir}/config-bottlerocket" | sort)
        local arch_configs
        arch_configs=$(grep "^CONFIG_" "${base_cfg_dir}/config-bottlerocket-${arch}" | sort)
        local full_configs
        full_configs=$(grep "^CONFIG_" "${kernel_path}/${config_filename}" | sort)

        # A config-microvm overlay may deliberately override or disable symbols
        # that the shared base (config-bottlerocket{,-${arch}}) pins. Exempt any
        # symbol the overlay touches from the base-subset check below; the
        # config-microvm overlay check further down separately verifies the overlay's
        # own values actually took effect.
        if [[ -f "${kernel_path}/config-microvm" ]]; then
            local overlay_syms
            overlay_syms=$(grep -oE "^CONFIG_[A-Za-z0-9_]+|^# CONFIG_[A-Za-z0-9_]+ is not set" "${kernel_path}/config-microvm" \
                | grep -oE "CONFIG_[A-Za-z0-9_]+" | sort -u)
            if [[ -n "${overlay_syms}" ]]; then
                local overlay_re
                overlay_re="^($(echo "${overlay_syms}" | paste -sd'|' -))="
                common_configs=$(echo "${common_configs}" | grep -vE "${overlay_re}" || true)
                arch_configs=$(echo "${arch_configs}" | grep -vE "${overlay_re}" || true)
            fi
        fi

        # Check common configs
        local missing_common
        missing_common=$(comm -23 <(echo "$common_configs") <(echo "$full_configs"))
        # Check arch-specific configs
        local missing_arch
        missing_arch=$(comm -23 <(echo "$arch_configs") <(echo "$full_configs"))

        if [[ -n "$missing_common" ]]; then
            echo "❌ Missing common configs:"
            echo "$missing_common"
            ((++errors))
        fi

        if [[ -n "$missing_arch" ]]; then
            echo "❌ Missing arch-specific configs:"
            echo "$missing_arch"
            ((++errors))
        fi

        # Check the config-microvm overlay (if present) actually took effect in
        # the generated config-full. Unlike the base fragments above, this is a
        # value-aware, arch-tolerant check: a setting may legitimately be absent
        # on an arch where its Kconfig dependencies are unmet, but if the symbol
        # IS present it must resolve to the value config-microvm asked for.
        # This is what catches a dead overlay line such as CONFIG_DM_CRYPT=y
        # silently resolving to =m, or a "# ... is not set" that didn't stick.
        local microvm_cfg="${kernel_path}/config-microvm"
        local microvm_bad=0
        if [[ -f "${microvm_cfg}" ]]; then
            local microvm_report
            if microvm_report=$(awk '
                FNR==NR {
                    if ($0 ~ /^CONFIG_[A-Za-z0-9_]+=/) {
                        eq = index($0, "="); sym = substr($0, 1, eq-1)
                        full[sym] = substr($0, eq+1); seen[sym] = 1
                    } else if ($0 ~ /^# CONFIG_[A-Za-z0-9_]+ is not set$/) {
                        full[$2] = "__NOTSET__"; seen[$2] = 1
                    }
                    next
                }
                /^CONFIG_[A-Za-z0-9_]+=/ {
                    eq = index($0, "="); sym = substr($0, 1, eq-1)
                    val = substr($0, eq+1)
                    if (!(sym in seen)) {
                        printf "  (skip) %s=%s — symbol absent from config-full (arch-specific / dependency unmet)\n", sym, val
                        next
                    }
                    if (full[sym] != val) {
                        printf "  ❌ %s: config-microvm wants =%s but config-full has %s\n", \
                            sym, val, (full[sym] == "__NOTSET__" ? "it disabled" : "=" full[sym])
                        bad++
                    }
                    next
                }
                /^# CONFIG_[A-Za-z0-9_]+ is not set$/ {
                    sym = $2
                    if (!(sym in seen)) next
                    if (full[sym] != "__NOTSET__") {
                        printf "  ❌ %s: config-microvm wants it disabled but config-full has =%s\n", sym, full[sym]
                        bad++
                    }
                }
                END { exit (bad > 0 ? 1 : 0) }
            ' "${kernel_path}/${config_filename}" "${microvm_cfg}"); then
                :
            else
                microvm_bad=1
            fi
            if [[ -n "${microvm_report}" ]]; then
                echo "--- config-microvm overlay check (${arch}) ---"
                echo "${microvm_report}"
            fi
            if ((microvm_bad)); then
                echo "❌ config-microvm settings did not take effect in ${config_filename}"
                ((++errors))
            fi
        fi

        if [[ -z "$missing_common" && -z "$missing_arch" ]] && ((microvm_bad == 0)); then
            echo "✅ All configs present for ${arch}"
        fi
    done

    # Overlay assignment lines (CONFIG_X=<val>, not the "is not set" form) must
    # resolve in at least one generated config-full. A symbol present in none of
    # the four (vanished to a typo, or a dependency broke after an SRPM bump) was
    # previously only (skip)ped in the per-arch overlay check and so went
    # unchecked; treat it as an error here. Absence stays legitimate for
    # "# ... is not set" lines and for assignments that land on at least one arch.
    local microvm_overlay="${kernel_path}/config-microvm"
    if [[ -f "${microvm_overlay}" ]]; then
        local all_full_syms overlay_sym
        all_full_syms=$(cat "${kernel_path}"/config-full-bottlerocket-*-on-* 2>/dev/null \
            | grep -oE "^CONFIG_[A-Za-z0-9_]+" | sort -u)
        while IFS= read -r overlay_sym; do
            [[ -z "${overlay_sym}" ]] && continue
            if ! grep -qxF "${overlay_sym}" <<<"${all_full_syms}"; then
                echo "❌ config-microvm sets ${overlay_sym} but it resolves in no config-full (typo or broken dependency?)"
                ((++errors))
            fi
        done < <(grep -oE "^CONFIG_[A-Za-z0-9_]+=" "${microvm_overlay}" | sed -E 's/=$//' | sort -u)
    fi

    if ((errors == 0)); then
        echo -e "\n🎉 All kernel config validations passed!"
    else
        echo -e "\n💥 Some kernel config validations failed!"
        bail "Kernel configuration validation failed"
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
    -h | --help)
        usage
        exit 0
        ;;
    *)
        echo "Unknown option: $1"
        usage
        exit 1
        ;;
    esac
    shift
done

# Ensure this script is run within the Bottlerocket SDK container
if [[ ! -d "${KERNEL_KIT_DIR}" ]]; then
    usage
    bail
fi

# Guarantee that at least the kernel sources provided by the kernels are available
# to generate the configuration.
fetch_sources

# Process kernels with available RPMs
found_any_rpm=0
for kernel_dir in "${KERNEL_KIT_DIR}/packages"/kernel-*; do
    if [[ ! -d "${kernel_dir}" ]]; then
        bail "No Kernel directory found for ${kernel_dir}"
    fi

    kernel_pkg=$(basename "${kernel_dir}")
    # Multiple RPMs can coexist. Use version sorting to select the latest RPM.
    rpm_file=$(find "${kernel_dir}" -name "kernel*.src.rpm" | sort -V | tail -1)

    if [[ -z "${rpm_file}" ]]; then
        echo "No RPM found for ${kernel_pkg}, skipping"
        continue
    fi

    found_any_rpm=$((found_any_rpm + 1))

    echo "Processing ${kernel_pkg}: $(basename "${rpm_file}")"

    tmpdir=$(mktemp -d)
    pushd "${tmpdir}" || bail "Unable to enter temporary directory"

    cp "${rpm_file}" kernel-source.rpm

    version="$(rpm --query --nosignature --queryformat '%{VERSION}' kernel-source.rpm)"
    majorminor=${version%.*}

    merge_kernel_configs "${version}" "${majorminor}" "${tmpdir}" "${kernel_dir}" || bail "Failed to merge kernel config for ${kernel_pkg}"

    echo "Validating ${kernel_pkg} configurations..."
    validate_kernel_configs "${version}" "${majorminor}" "${kernel_dir}" || bail "Validation failed for ${kernel_pkg}"

    popd || bail "Could not return from temporary directory"
done

# Check if we found any RPMs at all
if [ "${found_any_rpm}" -eq 0 ]; then
    bail "No kernel RPMs found in any directory"
fi
