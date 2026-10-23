# Portable ncdu for Linux amd64 and ARM

One executable: download the build for your Linux machine, name it `ncdu`, and run it. No ncdu
package, root access, compiler, Docker, or shared libraries are required on the
destination machine.

This is the **actual, unmodified ncdu 2.9.1**, distributed from the author's
official static build. It has ncdu's normal interface, options, scanning,
sorting, export/import, and deletion behavior. See [UPSTREAM.md](UPSTREAM.md)
for source links, version details, and checksums.

## Download and run

Download the single executable from [Releases](https://github.com/emad-ramlawi/ncdu/releases/latest):

| Architecture (`uname -m`) | Download |
| --- | --- |
| `x86_64` (amd64) | [ncdu-linux-amd64](https://github.com/emad-ramlawi/ncdu/releases/latest/download/ncdu-linux-amd64) |
| `aarch64` / `arm64` | [ncdu-linux-arm64](https://github.com/emad-ramlawi/ncdu/releases/latest/download/ncdu-linux-arm64) |
| `armv7l` (32-bit ARMv7 with VFPv3) | [ncdu-linux-armv7](https://github.com/emad-ramlawi/ncdu/releases/latest/download/ncdu-linux-armv7) |

For example, on ARM64:

```sh
curl -fL https://github.com/emad-ramlawi/ncdu/releases/latest/download/ncdu-linux-arm64 -o ncdu
chmod +x ncdu
./ncdu /var
```

On amd64:

```sh
curl -fL https://github.com/emad-ramlawi/ncdu/releases/latest/download/ncdu-linux-amd64 -o ncdu
chmod +x ncdu
./ncdu /var
```

You can also download the checked-in amd64 binary without waiting for a release:

```sh
curl -fL https://raw.githubusercontent.com/emad-ramlawi/ncdu/main/ncdu -o ncdu
curl -fL https://raw.githubusercontent.com/emad-ramlawi/ncdu/main/SHA256SUMS -o SHA256SUMS
sha256sum --ignore-missing -c SHA256SUMS
chmod +x ncdu
./ncdu --version
./ncdu /var
```

The ARM binaries are also checked in as `ncdu-linux-arm64` and
`ncdu-linux-armv7`. To verify release downloads, keep their original filenames,
download the release's `SHA256SUMS`, and run
`sha256sum --ignore-missing --check SHA256SUMS` before renaming the executable.

Copy to a server without internet access:

```sh
scp ncdu user@server:~/ncdu
ssh -t user@server './ncdu -x /'
```

Useful options:

```sh
./ncdu -x /                 # Stay on one filesystem
./ncdu -rr /var             # Disable deletion and shell spawning
./ncdu -t8 /data            # Scan with eight threads
./ncdu -o scan.json /data   # Export a scan
./ncdu -f scan.json         # Browse a saved scan
```

Press `?` for help and `q` to quit. Normal ncdu deletion is available with `d`;
use `-rr` when browsing should be read only. Scanning still uses the permissions
of the account running it. Use `sudo ./ncdu -x /` if you need access to protected
directories.

## Compatibility

Each binary is a static Linux ELF executable for its stated architecture. Its runtime libraries are
built in, so it avoids missing `libncurses`, `libzstd`, and glibc-version
problems. The amd64 and ARM64 builds target systems including RHEL and Rocky
Linux 10. The ARMv7 build needs ARMv7-A and VFPv3; it does not run on ARMv6
devices such as the original Raspberry Pi or Pi Zero. These are Linux binaries.

Automated smoke tests cover scanning, hard links, symlinks, Unicode filenames,
exclusions, parallel scans, JSON and compressed/binary exports, imports, and
the interactive interface. ARM64 runs on a native GitHub ARM64 runner; ARMv7
runs under QEMU user-mode emulation. The amd64 and ARM64 container matrix
includes Rocky Linux 10 and Red Hat UBI 10. UBI tests exercise Red Hat's RHEL 10 userspace; they do not
replace testing a full RHEL installation. Containers share the host kernel.

**ARMv7 limitation:** browsing a saved binary export (`-O`) with the official
ARMv7 executable triggers an unaligned memory store and SIGBUS in QEMU. This
case is explicitly reported as `XFAIL` in the emulated tests; other failures
still fail the workflow. Native ARMv7 behavior has not been verified. Use JSON
exports (`-o scan.json`, then `-f scan.json`) on ARMv7. Normal directory browsing,
JSON browsing, scanning, and compressed exports pass the emulated tests.

If an SSH terminal reports an unknown terminal type, try:

```sh
TERM=xterm-256color ./ncdu /var
```

An interactive terminal is needed for the browser (`ssh -t` allocates one).
To scan without a terminal, use `./ncdu -0 -o scan.json /var`.
If execution is denied from a filesystem mounted `noexec`, copy the executable
to a location where execution is allowed.

## Recreate the release package

On the packaging machine, install Bash, curl, GNU tar/coreutils, and Python 3
for verification, then run:

```sh
./scripts/package.sh
python3 scripts/smoke-test.py dist/ncdu-linux-amd64
```

This downloads the three official binaries and corresponding source archive, verifies
their pinned SHA256 checksums, checks that they match the checked-in binaries, and
creates the following in `dist/`:

- `ncdu-linux-amd64`, `ncdu-linux-arm64`, `ncdu-linux-armv7`: single executables.
- `ncdu-linux-<arch>.tar.gz`: executable named `ncdu`, license, and provenance.
- `ncdu-2.9.1-source.tar.gz`: unchanged upstream source archive.
- `SHA256SUMS`: checksums of the release assets.

This is a verified redistribution workflow; it does not compile a new ncdu
implementation. Changing versions requires reviewing the upstream downloads,
updating the pinned hashes in the script and provenance, replacing all three binaries,
and regenerating the root checksums.

Run the container tests with Docker on the development machine:

```sh
python3 scripts/smoke-test.py ncdu --image rockylinux/rockylinux:10
python3 scripts/smoke-test.py ncdu --image registry.access.redhat.com/ubi10/ubi-minimal:latest
```

On an ARM64 development machine:

```sh
python3 scripts/smoke-test.py ncdu-linux-arm64 --arch arm64
python3 scripts/smoke-test.py ncdu-linux-arm64 --arch arm64 --image rockylinux/rockylinux:10
```

To test ARMv7 on an amd64 machine, install QEMU on the development machine:

```sh
python3 scripts/smoke-test.py ncdu-linux-armv7 --arch armv7 --runner qemu-arm
```

QEMU is only needed for testing on another CPU architecture; destination ARM
machines run their matching executable directly.

## GitHub releases

Push a tag such as `v2.9.1-2` to run the release workflow. It verifies the
upstream downloads and checked-in binaries, runs the architecture-specific smoke tests and
container tests, then publishes all three executables, bundles, source,
and checksums to GitHub Releases. Normal pushes and pull requests run the same
checks without publishing. No additional GitHub secret is required.

ncdu is by [Yorhel](https://dev.yorhel.nl/ncdu), licensed under MIT. This
repository provides portable distribution and verification.
