#!/usr/bin/env bash

set -e -o pipefail

bail() {
    if [[ $# -gt 0 ]]; then
        >&2 echo "Error: $*"
    fi
    exit 1
}

pushd /work || bail "Unable to enter /work (bind mount to tmp dir)"

version="$(rpm --query --nosignature --queryformat '%{VERSION}' kernel-source.rpm)"
majorminor=${version%.*} # Trim after last '.', e.g. 6.1.132 -> 6.1
if [ "${majorminor}" == "6.12" ]; then
    # kernel 6.12 has a patch file that is not applied to the kernel sources, so
    # only pick up the 1000-series kernel patches for our purposes here.
    readarray -t br_patches < <(find /kernel-package -maxdepth 1 -name "10*.patch")
    spec_file="kernel6.12.spec"
    microcode_file="config-microcode-6-12"
else
    readarray -t br_patches < <(find /kernel-package -maxdepth 1 -name "*.patch")
    spec_file="kernel.spec"
    microcode_file="config-microcode"
fi

kernel_path=/kernel-package

rpm2cpio kernel-source.rpm | cpio -iu {,./}linux-"${version}".tar{,.xz} {,./}config-x86_64 {,./}config-aarch64 {,./}"*.patch" {,./}"${spec_file}"

# Upstream source is either xz compressed tarball or plain tarball
if [ -f "./linux-${version}.tar" ]; then
    tar -xof linux-"${version}".tar; rm linux-"${version}".tar
else
    tar -xof linux-"${version}".tar.xz; rm linux-"${version}".tar.xz
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

for arch in "x86_64" "aarch64"; do

    export CROSS_COMPILE=/usr/bin/${arch}-bottlerocket-linux-gnu-
    export KCONFIG_CONFIG=bottlerocket_${arch}_defconfig

    br_cfg="${kernel_path}/config-bottlerocket"
    microcode_cfg="/package/packages/microcode/${microcode_file}"

    pushd "linux-${version}" || bail "Could not move into linux-${version}"

    if [ "${arch}" = "aarch64" ]; then
        karch="arm64"
        script_args=("../config-${arch}" "${br_cfg}")
    elif [ "${arch}" = "x86_64" ]; then
        karch="x86"
        script_args=("../config-${arch}" "${microcode_cfg}" "${br_cfg}")
    fi

    ARCH=${karch} ./scripts/kconfig/merge_config.sh "${script_args[@]}"
    mv -f "bottlerocket_${arch}_defconfig" "${kernel_path}/config-full-bottlerocket-${arch}" || bail "Failed to create config-full-bottlerocket-${arch}"
    popd || bail "Could not move around - 'popd' failed in merge_config loop. Lets stop before we break anything further."
done
