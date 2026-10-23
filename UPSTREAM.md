# Upstream provenance

This repository redistributes the **unmodified official ncdu 2.9.1 Linux
x86_64 static executable**, written by Yorhel <projects@yorhel.nl> and released
under the MIT license. It is not a replacement implementation or a fork of
ncdu's behavior.

- Project: https://dev.yorhel.nl/ncdu
- Manual: https://dev.yorhel.nl/ncdu/man
- Checksums: https://dev.yorhel.nl/download#ncdu-2.9.1-linux-x86_64.tar.gz
- Binary archive: https://dev.yorhel.nl/download/ncdu-2.9.1-linux-x86_64.tar.gz
- Binary archive SHA256: `0c6c84b3f763c33baa051c8327f0e736f46f33a8cc061bb951d24517a8c5d73e`
- Corresponding source: https://dev.yorhel.nl/download/ncdu-2.9.1.tar.gz
- Source archive SHA256: `bfd1094e1400ee89cfd59200eab940f025ccdc0c238067105c984a3c4857bf7e`

The source release is currently 2.9.2; the official x86_64 static download
still points to 2.9.1. This package deliberately identifies itself as 2.9.1.
The upstream SHA256 values above were checked against the download page.
`scripts/package.sh` pins and verifies both archives before packaging them.

The executable statically links its runtime libraries, including terminal
handling and Zstandard support. No shared library loader or shared-library
dependencies are present. Common terminal descriptions are available in the
static build; an unusual TERM value may still need a matching system terminfo
entry. See the README for terminal troubleshooting.
