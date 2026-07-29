#!/usr/bin/env bash

# check that all `# headers` are formatted as a version, e.g. v1.2.3, with the
# exception of a single leading `# Unreleased` header for changes that have
# not yet been assigned a version.
# this should be sufficient to validate the CHANGELOG for our CI, provided that
# every new tag has a corresponding CHANGELOG update, as we always parse the
# CHANGELOG between two headers with a tagged version.
headers=$(grep -ne '^# ' CHANGELOG.md)
first_header=$(echo "${headers}" | head -n 1)
if [[ "${first_header}" == *':# Unreleased' ]]; then
  headers=$(echo "${headers}" | tail -n +2)
fi
if ! diff <(echo "${headers}") <(grep -ne '^# v[0-9]\+\.[0-9]\+\.[0-9]\+' CHANGELOG.md); then
  echo "CHANGELOG validation FAILED! Headers must match the regex '^# v[0-9]\+\.[0-9]\+\.[0-9]\+.', except for a single leading '# Unreleased' header."
  exit 1
fi

# check that all versions are unique
versions=$(grep -o '^# v[0-9]\+\.[0-9]\+\.[0-9]\+' CHANGELOG.md)
if [[ $(echo "${versions}" | sort | uniq -d | wc -l) -gt 0 ]]; then
  echo "CHANGELOG validation FAILED! Duplicate versions found."
  exit 1
fi

# check that versions are in descending order
# sort the versions and check the diff with current set of versions
if ! echo "${versions}" | sort -V -r | diff - <(echo "${versions}"); then
  echo "CHANGELOG validation FAILED! Versions must be in descending order."
  exit 1
fi

echo "CHANGELOG validation PASSED!"
