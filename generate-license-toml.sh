#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:?Usage: $0 <version>}"
TARBALL="sources/Xray-core-${VERSION}-vendor.tar.bz2"
OUTPUT="sources/go-vendor-tools.toml"

if [ ! -f "$TARBALL" ]; then
    echo "ERROR: $TARBALL not found" >&2
    exit 1
fi

# License files and their SPDX expressions
declare -A LICENSES=(
    ["vendor/github.com/cloudflare/circl/LICENSE"]="BSD-3-Clause"
    ["vendor/github.com/ghodss/yaml/LICENSE"]="MIT"
    ["vendor/github.com/juju/ratelimit/LICENSE"]="LGPL-3.0-only"
    ["vendor/github.com/miekg/dns/COPYRIGHT"]="BSD-3-Clause"
    ["vendor/gopkg.in/yaml.v3/LICENSE"]="MIT AND Apache-2.0"
)

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

echo "Extracting license files from $TARBALL..."
for path in "${!LICENSES[@]}"; do
    tar -xf "$TARBALL" -C "$tmpdir" "$path" 2>/dev/null || {
        echo "WARNING: $path not found in tarball" >&2
    }
done

: > "$OUTPUT"
first=true
for path in $(printf '%s\n' "${!LICENSES[@]}" | sort); do
    expr="${LICENSES[$path]}"
    file="$tmpdir/$path"

    if [ ! -f "$file" ]; then
        echo "SKIPPING: $path (not found)" >&2
        continue
    fi

    hash=$(sha256sum "$file" | cut -d' ' -f1)

    if [ "$first" = true ]; then
        first=false
    else
        printf '\n' >> "$OUTPUT"
    fi

    cat >> "$OUTPUT" <<EOF
[[licensing.licenses]]
path = "$path"
sha256sum = "$hash"
expression = "$expr"
EOF
done

echo "Generated $OUTPUT:"
echo "---"
cat "$OUTPUT"
