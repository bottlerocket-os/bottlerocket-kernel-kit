#!/usr/bin/env bash
set -e -o pipefail

bail() {
    if [[ $# -gt 0 ]]; then
        >&2 echo "Error: $*"
    fi
    exit 1
}

find_sdk() {
  grep -A5 '^\[sdk\]' Twoliter.lock | grep '^source' | cut -d'"' -f2
}

SCRIPT_PATH="$1"

if [[ -z "${SDK}" ]]; then
  echo "Retrieving SDK from Twoliter.lock"
  SDK="$(find_sdk)"
fi

echo "Using SDK: ${SDK} to run the provided script"

docker run --rm \
    -v "$(pwd):/bottlerocket-kernel-kit" \
    --user "$(id -u):$(id -g)" \
    "${SDK}" \
    bash "${SCRIPT_PATH}"

