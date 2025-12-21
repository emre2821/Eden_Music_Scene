"""Helper build script for environments missing the stdlib 'venv' module.

This script installs build dependencies into the current interpreter and
runs `python -m build --no-isolation` to avoid build's attempt to create
an isolated environment using `venv`.

Usage:
    python scripts/build_package.py
"""

import subprocess
import sys


def run(cmd, **kwargs):
    print("$", " ".join(cmd))
    subprocess.check_call(cmd, **kwargs)


def main():
    # Ensure pip and build tools are present
    run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "build", "wheel"])

    # Run build without isolation to avoid 'venv' dependency
    run([sys.executable, "-m", "build", "--no-isolation"])


if __name__ == "__main__":
    main()
