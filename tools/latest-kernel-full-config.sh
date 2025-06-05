#!/usr/bin/env bash

set -e -o pipefail

#
# Common error handling
#

# Cleanup all tmp files/directories
cleanup() {
    rm -rf "$tmpdir"
}

trap cleanup INT EXIT

bail() {
    if [[ $# -gt 0 ]]; then
        >&2 echo "Error: $*"
    fi
    exit 1
}

# Function to display usage information
usage() {
    cat << EOF
Usage: $(basename "$0") -r RPM_FILE

Extract kernel configurations from an RPM, merge with Bottlerocket's, and write out to a file, per architecture (x86_64 and aarch64).
Run from the top-level bottlerocket-kernel-kit directory with the following parameters:
    -r RPM_FILE    Path to RPM file
    -h             Display this help message

Dependencies:
    - docker
    - rpm2cpio
    - cpio
    - tar
    - tq
EOF
}

usage_error() {
    >&2 usage
    bail "$1"
}

check_dependencies() {
    hash rpm2cpio || usage_error "DEPENDENCY ERROR: Please install rpm2cpio somewhere in your PATH"
    hash cpio || usage_error "DEPENDENCY ERROR: Please install cpio somewhere in your PATH"
    hash tar || usage_error "DEPENDENCY ERROR: Please install tar somewhere in your PATH"
    hash docker || usage_error "DEPENDENCY ERROR: Please install docker somewhere in your PATH"
    hash tq || usage_error "DEPENDENCY ERROR: Please cargo install tomlq somewhere in your PATH"
}

# Get the SDK version from workspace Twoliter.toml and Twoliter.override, if provided.
# Assumes running in the top level of the project and `tq` on $PATH.
resolve_bottlerocket_sdk() {
    # Inspect Twoliter.lock file for [sdk] section source
    source="$(tq -r ".sdk.source" -f Twoliter.lock)"
    version="$(tq -r ".sdk.version" -f Twoliter.lock)"
    _name="$(tq -r ".sdk.name" -f Twoliter.lock)"
    # Trim from last slash, e.g. public.ecr.aws/bottlerocket/bottlerocket-sdk:v0.61.0 -> public.ecr.aws/bottlerocket
    _registry="${source%/*}"

    # Check Twoliter.override to get the registry. For simplicity, assume overrides are only against named project named bottlerocket-sdk
    registry="$(tq -r ".bottlerocket.bottlerocket-sdk.registry" -f Twoliter.override 2>/dev/null || echo "$_registry")"
    name="$(tq -r ".bottlerocket.bottlerocket-sdk.name" -f Twoliter.override 2>/dev/null || echo "$_name")"

    # Form the final SDK
    echo "${registry}/${name}:v${version}"
}

# expect $pwd to be packages/kernel-${kver}
merge_kernel_configs() {
    rpm_file=$1
    sdk_image=$2
    kernel_path=$PWD


    tmpdir=$(mktemp -d)
    cp "${rpm_file}" "${tmpdir}/kernel-source.rpm"

    docker run --rm \
        -v "${kernel_path}/":/kernel-package \
        -v "${tmpdir}":/work \
        -v "${kernel_path}/../../":/package \
        -u "$(id -u)":1000 \
        --name "kernel-${version}-inner-full" \
        "${sdk_image}" \
        "/package/tools/inner-full-config.sh"
}

################################################################################
# START MAIN CONTROL FLOW
################################################################################

# parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--rpm-file)
            shift; rpm_file="$1" ;;
        *)
            usage_error "Invalid option '$1'" ;;
    esac
    shift
done

# Verify all required parameters are provided
if [ -z "${rpm_file}" ]; then
    echo "Error: Missing required parameters"
    usage
    exit 1
fi

rpm_file=$(realpath "${rpm_file}")

# Check if the RPM file exists
if [ ! -f "${rpm_file}" ]; then
    bail "RPM file not found: ${rpm_file}"
fi

# Check dependencies
check_dependencies

# Get SDK image from Twoliter.lock and/or Twoliter.override
sdk_image=$(resolve_bottlerocket_sdk)

# Parse RPM file for kernel version (6.1, 6.12, etc.)
kver=$(rpm --query --nosignature --queryformat '%{VERSION}' "${rpm_file}" | sed 's/\.[^.]*$//')

# pushd into kernel dir
pushd packages || bail "Could not move into packages"
pushd kernel-"${kver}" || bail "Could not move into packages/kernel-${kver}"

# Merge configs
merge_kernel_configs "${rpm_file}" "${sdk_image}"

# Exit kernel-${kver}/ dir
popd  || bail "Could not move around - 'popd' failed."
# Exit packages/ dir
popd  || bail "Could not move around - 'popd' failed."
