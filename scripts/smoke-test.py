#!/usr/bin/env python3
"""Exercise the actual executable, optionally inside an unmodified Linux image."""

import argparse
import errno
import fcntl
import json
import os
from pathlib import Path
import pty
import select
import struct
import subprocess
import tempfile
import termios
import time


def check_elf(binary, arch):
    data = binary.read_bytes()
    elf_class, machine = {"amd64": (2, 62), "arm64": (2, 183), "armv7": (1, 40)}[arch]
    assert data[:6] == b"\x7fELF" + bytes((elf_class, 1)), "Unexpected ELF class or byte order"
    assert struct.unpack_from("<H", data, 18)[0] == machine, f"Expected {arch}"
    if elf_class == 2:
        offset = struct.unpack_from("<Q", data, 32)[0]
        size, count = struct.unpack_from("<HH", data, 54)
    else:
        offset = struct.unpack_from("<I", data, 28)[0]
        size, count = struct.unpack_from("<HH", data, 42)
    for index in range(count):
        kind = struct.unpack_from("<I", data, offset + index * size)[0]
        assert kind not in (2, 3), "Unexpected dynamic segment or interpreter"
    print(f"PASS: static Linux {arch} ELF, no interpreter or dynamic dependencies", flush=True)


def interactive(command, marker, known_armv7_bus_error=False):
    master, slave = pty.openpty()
    fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 30, 120, 0, 0))
    process = subprocess.Popen(command, stdin=slave, stdout=slave, stderr=slave)
    os.close(slave)
    output = bytearray()
    sent_quit = False
    deadline = time.monotonic() + 25
    try:
        while time.monotonic() < deadline:
            if select.select([master], [], [], 0.2)[0]:
                try:
                    chunk = os.read(master, 65536)
                except OSError as error:
                    if error.errno == errno.EIO:
                        break
                    raise
                if not chunk:
                    break
                output.extend(chunk)
                if not sent_quit and marker in output:
                    os.write(master, b"q")
                    sent_quit = True
            if process.poll() is not None:
                break
        if process.poll() is None:
            process.wait(timeout=3)
        if (known_armv7_bus_error and not sent_quit
                and process.returncode in (-7, 135)
                and b"target signal 7 (Bus error)" in output):
            print("XFAIL: official ARMv7 binary uses an unaligned store while browsing binary exports under QEMU; use JSON exports", flush=True)
            return False
        assert sent_quit, f"Browser did not display fixture: {bytes(output)!r}"
        assert process.returncode == 0, f"Browser exited {process.returncode}: {bytes(output)!r}"
        return True
    finally:
        if process.poll() is None:
            process.kill()
        process.wait()
        os.close(master)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("--arch", choices=("amd64", "arm64", "armv7"), default="amd64")
    execution = parser.add_mutually_exclusive_group()
    execution.add_argument("--image", help="Docker image to test without installing anything inside it")
    execution.add_argument("--runner", help="Emulator executable, e.g. qemu-arm or qemu-aarch64-static")
    args = parser.parse_args()
    binary = args.binary.resolve(strict=True)
    check_elf(binary, args.arch)
    with tempfile.TemporaryDirectory(prefix="ncdu-smoke-") as temporary:
        work = Path(temporary)
        fixture = work / "fixture"
        fixture.mkdir()
        (fixture / "hello.txt").write_bytes(b"a" * 12345)
        (fixture / "empty").touch()
        (fixture / "unicode-\u00e9.txt").write_bytes(b"unicode")
        (fixture / "excluded.tmp").write_bytes(b"exclude me")
        (fixture / "child").mkdir()
        (fixture / "child" / "nested.txt").write_bytes(b"nested")
        os.link(fixture / "hello.txt", fixture / "hardlink.txt")
        (fixture / "symlink.txt").symlink_to("hello.txt")
        base = "/work" if args.image else str(work)

        def command(options, tty=False, terminal="xterm-256color"):
            if args.image:
                return [
                    "docker", "run", "--rm", "--platform",
                    {"amd64": "linux/amd64", "arm64": "linux/arm64", "armv7": "linux/arm/v7"}[args.arch],
                    "--network", "none", "--read-only",
                    "--cap-drop=ALL", "--security-opt=no-new-privileges",
                    "--user", f"{os.getuid()}:{os.getgid()}",
                    "-v", f"{binary}:/ncdu:ro", "-v", f"{work}:/work:rw",
                    "-e", f"TERM={terminal}", "-e", "HOME=/work",
                    "-e", "XDG_CONFIG_HOME=/work/.config", "-e", "XDG_CONFIG_DIRS=/work/system-config",
                    *(["-it"] if tty else []), args.image, "/ncdu", *options,
                ]
            return ["env", f"TERM={terminal}", f"HOME={work}",
                    f"XDG_CONFIG_HOME={work}/.config", f"XDG_CONFIG_DIRS={work}/system-config",
                    *([args.runner] if args.runner else []), str(binary), *options]

        def run(*options):
            result = subprocess.run(
                command(["--ignore-config", *options]), capture_output=True,
                timeout=120 if args.image else 30
            )
            assert result.returncode == 0, (options, result.stdout, result.stderr)
            return result.stdout

        assert run("--version").strip() == b"ncdu 2.9.1"
        assert b"--one-file-system" in run("--help")
        run("-0", "-o", f"{base}/scan.json", f"{base}/fixture")
        scan = json.loads((work / "scan.json").read_bytes())
        entries = {item[0]["name"] if isinstance(item, list) else item["name"]: item for item in scan[3][1:]}
        assert entries["hello.txt"]["asize"] == 12345
        assert entries["empty"].get("asize", 0) == 0
        assert entries["unicode-\u00e9.txt"]["asize"] == 7
        assert entries["symlink.txt"]["asize"] == len("hello.txt")
        assert entries["child"][1]["name"] == "nested.txt"
        assert "hardlink.txt" in entries
        print("PASS: scan, sizes, hard links, symlinks, Unicode and nested paths", flush=True)

        run("-0", "-t4", "--exclude", "*.tmp", "-o", f"{base}/parallel.json", f"{base}/fixture")
        parallel = json.loads((work / "parallel.json").read_bytes())
        excluded = next(item for item in parallel[3][1:] if isinstance(item, dict) and item["name"] == "excluded.tmp")
        assert excluded.get("excluded") == "pattern"
        run("-0", "--quit-after-scan", "-f", f"{base}/scan.json")
        run("-0", "-c", "-o", f"{base}/scan.json.zst", f"{base}/fixture")
        assert (work / "scan.json.zst").read_bytes()[:4] == b"\x28\xb5\x2f\xfd"
        run("-0", "--quit-after-scan", "-f", f"{base}/scan.json.zst")
        run("-0", "-t4", "-O", f"{base}/scan.ncdu", f"{base}/fixture")
        assert (work / "scan.ncdu").stat().st_size > 0
        run("-0", "--quit-after-scan", "-f", f"{base}/scan.ncdu")
        print("PASS: parallel scan, exclusions, JSON, Zstandard and binary export/import", flush=True)

        for terminal in ("xterm-256color", "linux", "screen"):
            interactive(command(["--ignore-config", "-rr", f"{base}/fixture"], tty=True, terminal=terminal), b"hello.txt")
            print(f"PASS: interactive browser and q to quit (TERM={terminal})", flush=True)
        interactive(command(["--ignore-config", "-rr", "-f", f"{base}/scan.json"], tty=True), b"hello.txt")
        print("PASS: interactive browsing of JSON export", flush=True)
        if interactive(command(["--ignore-config", "-rr", "-f", f"{base}/scan.ncdu"], tty=True), b"hello.txt",
                       known_armv7_bus_error=args.arch == "armv7" and args.runner is not None):
            print("PASS: interactive browsing of binary export", flush=True)

        config = work / ".config" / "ncdu"
        config.mkdir(parents=True)
        (config / "config").write_text("--color=off\n--exclude=*.tmp\n")
        result = subprocess.run(command(["-0", "-o", f"{base}/config.json", f"{base}/fixture"]),
                                capture_output=True, timeout=30)
        assert result.returncode == 0, result.stderr
        configured = json.loads((work / "config.json").read_bytes())
        excluded = next(item for item in configured[3][1:] if isinstance(item, dict) and item["name"] == "excluded.tmp")
        assert excluded.get("excluded") == "pattern", "User configuration was not applied"
        interactive(command(["-rr", f"{base}/fixture"], tty=True), b"hello.txt")
        print("PASS: normal startup with a user configuration file", flush=True)

    print(f"Smoke tests completed ({args.arch}, {args.image or args.runner or 'host'}).", flush=True)


if __name__ == "__main__":
    main()
