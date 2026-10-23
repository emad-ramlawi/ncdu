#!/usr/bin/env bash
set -euo pipefail

root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
dist="$root/dist"
work=$(mktemp -d)
trap 'rm -rf -- "$work"' EXIT
mkdir -p "$dist"

fetch() {
    local name=$1 expected=$2
    curl --fail --location --retry 3 --connect-timeout 15 --max-time 180 \
        "https://dev.yorhel.nl/download/$name" --output "$work/$name"
    printf '%s  %s\n' "$expected" "$work/$name" | sha256sum --check --status
}

fetch ncdu-2.9.1.tar.gz \
    bfd1094e1400ee89cfd59200eab940f025ccdc0c238067105c984a3c4857bf7e

(cd "$root" && sha256sum --check SHA256SUMS)

assets=()
while read -r arch upstream_arch checked_in expected; do
    archive="ncdu-2.9.1-linux-$upstream_arch.tar.gz"
    fetch "$archive" "$expected"
    bundle="$work/$arch"
    mkdir -p "$bundle"
    tar -xzf "$work/$archive" -C "$bundle" ncdu
    chmod 755 "$bundle/ncdu"
    cmp "$root/$checked_in" "$bundle/ncdu"
    cp "$bundle/ncdu" "$dist/ncdu-linux-$arch"
    cp "$root/LICENSE" "$root/UPSTREAM.md" "$bundle/"
    tar --sort=name --mtime='UTC 2025-08-21' --owner=0 --group=0 --numeric-owner \
        -C "$bundle" -cf - LICENSE UPSTREAM.md ncdu | gzip -n > "$dist/ncdu-linux-$arch.tar.gz"
    assets+=("ncdu-linux-$arch" "ncdu-linux-$arch.tar.gz")
done <<'ARCHITECTURES'
amd64 x86_64 ncdu 0c6c84b3f763c33baa051c8327f0e736f46f33a8cc061bb951d24517a8c5d73e
arm64 aarch64 ncdu-linux-arm64 5bf4a37e8b5e1ecc6863475dc800c6a0d73b9cd1452e37d744edd3df0b58dac0
armv7 arm ncdu-linux-armv7 209c0055411feb116e318f5a438b41e2314e944234b42c1396b1e77f6dc5d2a3
ARCHITECTURES

cp "$work/ncdu-2.9.1.tar.gz" "$dist/ncdu-2.9.1-source.tar.gz"
(
    cd "$dist"
    sha256sum "${assets[@]}" ncdu-2.9.1-source.tar.gz > SHA256SUMS
)
printf 'Verified release assets: %s\n' "$dist"
