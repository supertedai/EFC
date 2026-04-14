#!/usr/bin/env python3
"""
Cross-platform entrypoint for EFC Nested Sampling setup.

Autodetects the operating system and dispatches to the right shell
script (bash on Linux/macOS, PowerShell on Windows).

Usage (same on all platforms):
    python setup.py

Or directly:
    Linux/macOS : ./setup_environment.sh
    Windows     : powershell -ExecutionPolicy Bypass -File .\setup_environment.ps1
"""
import os
import platform
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    system = platform.system()
    print(f"Detected OS: {system} ({platform.platform()})")

    if system in ("Linux", "Darwin"):
        script = HERE / "setup_environment.sh"
        if not script.exists():
            print(f"ERROR: {script} not found", file=sys.stderr)
            return 1
        # Ensure executable bit
        mode = script.stat().st_mode
        os.chmod(script, mode | 0o111)
        print(f"Running: {script}")
        return subprocess.call(["bash", str(script)], cwd=HERE)

    if system == "Windows":
        script = HERE / "setup_environment.ps1"
        if not script.exists():
            print(f"ERROR: {script} not found", file=sys.stderr)
            return 1
        print(f"Running: {script}")
        return subprocess.call(
            ["powershell", "-ExecutionPolicy", "Bypass",
             "-File", str(script)],
            cwd=HERE,
        )

    print(f"ERROR: Unsupported platform '{system}'. Supported: Linux, "
          f"macOS (Darwin), Windows.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
