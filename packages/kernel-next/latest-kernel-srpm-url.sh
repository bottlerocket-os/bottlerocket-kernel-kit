#!/bin/sh
series=kernel7.2
# shellcheck disable=SC2016
cmd='
set -e
dnf install -q -y --releasever=latest yum-utils >/dev/null 2>&1
latest_version() {
  dnf repoquery -q --releasever=latest --forcearch="$1" --latest-limit=1 \
    --queryformat "%{version}-%{release}\n" "$2" | grep . | sort -V | tail -1
}
aarch64=$(latest_version aarch64 ${SERIES}-64k)
x86_64=$(latest_version x86_64 ${SERIES})
if [ -z "${aarch64}" ] || [ "${aarch64}" != "${x86_64}" ]; then
  echo "error: ${SERIES}-64k (aarch64) is \"${aarch64}\", ${SERIES} (x86_64) is \"${x86_64}\"" >&2
  exit 1
fi
dnf download -q --releasever=latest --forcearch=x86_64 --source --url "${SERIES}-${x86_64}"
'
docker run --rm -e SERIES="${series}" public.ecr.aws/amazonlinux/amazonlinux:2027 sh -c "${cmd}" \
    | grep '^http' \
    | xargs --max-args=1 --no-run-if-empty realpath --canonicalize-missing --relative-to=. \
    | sed 's_:/_://_'
