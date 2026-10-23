# Portable ncdu for Linux amd64

One executable: copy `ncdu` to a Linux x86_64 machine and run it. No ncdu
package, root access, compiler, Docker, or shared libraries are required on the
destination machine.

This is the **actual, unmodified ncdu 2.9.1**, distributed from the author's
official static build. It has ncdu's normal interface, options, scanning,
sorting, export/import, and deletion behavior. See [UPSTREAM.md](UPSTREAM.md)
for source links, version details, and checksums.

## Download and run

Download the single executable from [Releases](https://github.com/emad-ramlawi/ncdu/releases/latest):

```sh
curl -fL https://github.com/emad-ramlawi/ncdu/releases/latest/download/ncdu-linux-amd64 -o ncdu
chmod +x ncdu
./ncdu /var
```

You can also download the checked-in binary without waiting for a release:

```sh
curl -fL https://raw.githubusercontent.com/emad-ramlawi/ncdu/main/ncdu -o ncdu
curl -fL https://raw.githubusercontent.com/emad-ramlawi/ncdu/main/SHA256SUMS -o SHA256SUMS
sha256sum -c SHA256SUMS
chmod +x ncdu
./ncdu --version
./ncdu /var
```

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

The binary is an ELF64 x86_64 static executable. Its runtime libraries are
built in, so it avoids missing `libncurses`, `libzstd`, and glibc-version
problems. It targets Linux amd64, including RHEL and Rocky Linux 10; it is not
an ARM, macOS, or Windows binary.

Automated smoke tests cover scanning, hard links, symlinks, Unicode filenames,
exclusions, parallel scans, JSON and compressed/binary exports, imports, and
the interactive interface. The container matrix includes Rocky Linux 10 and
Red Hat UBI 10. UBI tests exercise Red Hat's RHEL 10 userspace; they do not
replace testing a full RHEL installation. Containers share the host kernel.

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

This downloads the official binary and corresponding source archive, verifies
their pinned SHA256 checksums, checks that the binary matches `./ncdu`, and
creates the following in `dist/`:

- `ncdu-linux-amd64`: the single executable.
- `ncdu-linux-amd64.tar.gz`: executable named `ncdu`, license, and provenance.
- `ncdu-2.9.1-source.tar.gz`: unchanged upstream source archive.
- `SHA256SUMS`: checksums of the release assets.

This is a verified redistribution workflow; it does not compile a new ncdu
implementation. Changing versions requires reviewing the upstream downloads,
updating the pinned hashes in the script and provenance, replacing `ncdu`,
and regenerating the root checksum.

Run the container tests with Docker on the development machine:

```sh
python3 scripts/smoke-test.py ncdu --image rockylinux/rockylinux:10
python3 scripts/smoke-test.py ncdu --image registry.access.redhat.com/ubi10/ubi-minimal:latest
```

## GitHub releases

Push a tag such as `v2.9.1-1` to run the release workflow. It verifies the
upstream downloads and checked-in binary, runs the smoke tests locally and in
both container images, then publishes the single executable, bundle, source,
and checksums to GitHub Releases. Normal pushes and pull requests run the same
checks without publishing. No additional GitHub secret is required.

ncdu is by [Yorhel](https://dev.yorhel.nl/ncdu), licensed under MIT. This
repository provides portable distribution and verification.
