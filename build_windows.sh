#!/usr/bin/env bash
# Build a Windows executable using PyInstaller.
# NOTE: To build a true Windows .exe, run this on Windows (recommended) or on WSL/Windows.
# Building on Linux will produce a Linux binary unless you have a cross-compilation setup.

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$SCRIPT_DIR"

echo "Installing build-time dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install pyinstaller

echo "Running PyInstaller..."
pyinstaller --onefile --windowed --name barcode_creator barcode_creator.py

echo "Build finished. Output:" 
ls -la dist/

echo "If you need a Windows executable, run this script on Windows or use a Windows build host."
