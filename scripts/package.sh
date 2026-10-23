#!/usr/bin/env bash
set -euo pipefail

root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
dist="$root/dist"
work=$(mktemp -d)
trap 'rm -rf -- "$work"' EXIT
mkdir -p "$dist" "$work/bundle"

fetch() {
    local name=$1 expected=$2
    curl --fail --location --retry 3 --connect-timeout 15 --max-time 180 \
        "https://dev.yorhel.nl/download/$name" --output "$work/$name"
    printf '%s  %s\n' "$expected" "$work/$name" | sha256sum --check --status
}

fetch ncdu-2.9.1-linux-x86_64.tar.gz \
    0c6c84b3f763c33baa051c8327f0e736f46f33a8cc061bb951d24517a8c5d73e
fetch ncdu-2.9.1.tar.gz \
    bfd1094e1400ee89cfd59200eab940f025ccdc0c238067105c984a3c4857bf7e

tar -xzf "$work/ncdu-2.9.1-linux-x86_64.tar.gz" -C "$work/bundle" ncdu
chmod 755 "$work/bundle/ncdu"
cmp "$root/ncdu" "$work/bundle/ncdu"
(cd "$root" && sha256sum --check SHA256SUMS)

cp "$work/bundle/ncdu" "$dist/ncdu-linux-amd64"
cp "$root/LICENSE" "$root/UPSTREAM.md" "$work/bundle/"
tar --sort=name --mtime='UTC 2025-08-21' --owner=0 --group=0 --numeric-owner \
    -C "$work/bundle" -cf - LICENSE UPSTREAM.md ncdu | gzip -n > "$dist/ncdu-linux-amd64.tar.gz"
cp "$work/ncdu-2.9.1.tar.gz" "$dist/ncdu-2.9.1-source.tar.gz"
(
    cd "$dist"
    sha256sum ncdu-linux-amd64 ncdu-linux-amd64.tar.gz ncdu-2.9.1-source.tar.gz > SHA256SUMS
)
printf 'Verified release assets: %s\n' "$dist"
