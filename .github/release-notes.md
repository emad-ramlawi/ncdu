The unmodified official **ncdu 2.9.1** static executables for Linux:

- **ncdu-linux-amd64** for x86_64.
- **ncdu-linux-arm64** for AArch64.
- **ncdu-linux-armv7** for 32-bit ARMv7-A with VFPv3 (not ARMv6).

All builds pass scanning, JSON export/import and browsing, configuration, and
normal interactive terminal tests. ARM64 is tested on a native runner; ARMv7 is tested with QEMU.
The amd64 and ARM64 builds also pass Rocky Linux 10 and Red Hat UBI 10 tests.

**ARMv7 limitation:** browsing saved binary exports (`-O`) triggers an unaligned
store and SIGBUS under QEMU; this is explicitly marked `XFAIL` in testing.
Use JSON exports (`-o scan.json`) on ARMv7. Native ARMv7 hardware is unverified.

Download the executable for your architecture, rename it to `ncdu`, and run:

```sh
chmod +x ncdu
./ncdu /var
```

No ncdu package or shared libraries need to be installed. Normal ncdu
permissions and terminal requirements apply.

Assets include SHA256 checksums, an optional tar.gz bundle with the license
and provenance, and the unchanged corresponding upstream source archive.
See the repository README and UPSTREAM.md for attribution and details.
