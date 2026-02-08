@echo off
REM Build a Windows executable using PyInstaller
REM Run this on Windows (recommended).

python -m pip install --upgrade pip
python -m pip install pyinstaller

pyinstaller --onefile --windowed --name barcode_creator barcode_creator.py

echo Build finished. See the dist\ directory for barcode_creator.exe
