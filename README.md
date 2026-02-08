# barcodecreator

This small utility generates a sequence of Code 128 barcodes and lays them out onto Avery label templates (PDF).

Usage
 - Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

 - Run the GUI and follow prompts to select start/end and template, then save a PDF:

```bash
python3 barcode_creator.py
```

Notes
 - Templates include `Avery 5160` and `Avery 6576` presets; verify printing scale (100%) with your printer.
 - To produce a standalone Windows executable, use `pyinstaller`:
 - To produce a standalone Windows executable, use `pyinstaller` on a Windows host (recommended):

```bash
pip install pyinstaller
pyinstaller --onefile --windowed barcode_creator.py
```

The resulting `dist/barcode_creator.exe` can be copied to a Windows machine.

Alternatively, helper scripts are provided:

- `build_windows.sh` — installs `pyinstaller` and runs the build (for WSL/Unix environments; building a true Windows .exe requires a Windows host or cross-build toolchain).
- `build_windows.bat` — Windows batch script to run the same build on Windows.

Run the appropriate script on your build host and find the executable in the `dist/` directory.

Continuous build (Windows)
 - A GitHub Actions workflow is included at `.github/workflows/build-windows.yml` that builds `barcode_creator.exe` on `windows-latest` and uploads it as an artifact named `barcode_creator-windows`.
 - Trigger it by pushing to `main` or via the Actions tab -> "Run workflow" (workflow_dispatch).

After a successful run, download the `barcode_creator-windows` artifact from the Actions run to get `barcode_creator.exe`.