# Upstream provenance

This repository redistributes the **unmodified official ncdu 2.9.1 Linux
static executables for amd64, ARM64, and ARMv7**, written by Yorhel <projects@yorhel.nl> and released
under the MIT license. It is not a replacement implementation or a fork of
ncdu's behavior.

- Project: https://dev.yorhel.nl/ncdu
- Manual: https://dev.yorhel.nl/ncdu/man
- Checksums: https://dev.yorhel.nl/download#ncdu-2.9.1-linux-x86_64.tar.gz
- Binary archive: https://dev.yorhel.nl/download/ncdu-2.9.1-linux-x86_64.tar.gz
- Binary archive SHA256: `0c6c84b3f763c33baa051c8327f0e736f46f33a8cc061bb951d24517a8c5d73e`
- ARM64 archive: https://dev.yorhel.nl/download/ncdu-2.9.1-linux-aarch64.tar.gz
- ARM64 archive SHA256: `5bf4a37e8b5e1ecc6863475dc800c6a0d73b9cd1452e37d744edd3df0b58dac0`
- ARMv7 archive: https://dev.yorhel.nl/download/ncdu-2.9.1-linux-arm.tar.gz
- ARMv7 archive SHA256: `209c0055411feb116e318f5a438b41e2314e944234b42c1396b1e77f6dc5d2a3`
- Corresponding source: https://dev.yorhel.nl/download/ncdu-2.9.1.tar.gz
- Source archive SHA256: `bfd1094e1400ee89cfd59200eab940f025ccdc0c238067105c984a3c4857bf7e`

The source release is currently 2.9.2; the official static downloads
still point to 2.9.1. This package deliberately identifies itself as 2.9.1.
The upstream SHA256 values above were checked against the download page.
`scripts/package.sh` pins and verifies all four archives before packaging them.

The upstream 32-bit ARM executable uses ARMv7-A, Thumb-2 and VFPv3, as shown
by its ELF attributes. It is named `ncdu-linux-armv7` here to make that
requirement explicit; ARMv6 devices (such as the original Raspberry Pi and
Pi Zero) are not supported by this build. ARM64 is the AArch64 executable.

ARMv7 binary-export browsing has a known limitation under QEMU: the official
binary performs an unaligned `strd` store and receives SIGBUS. It is preserved
unchanged here. The test suite records that exact failure as `XFAIL` rather
than treating it as successful browsing. Use JSON export/import on ARMv7;
native ARMv7 hardware behavior has not been verified.

The executable statically links its runtime libraries, including terminal
handling and Zstandard support. No shared library loader or shared-library
dependencies are present. Common terminal descriptions are available in the
static build; an unusual TERM value may still need a matching system terminfo
entry. See the README for terminal troubleshooting.
