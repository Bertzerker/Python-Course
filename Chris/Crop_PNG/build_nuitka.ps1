# build_nuitka.ps1
# One-file EXE build for Bulk Cropper (PySide6)
# Usage (PowerShell):  .\build_nuitka.ps1

$ErrorActionPreference = 'Stop'

# Optional: create/activate venv
# python -m venv .venv
# .\.venv\Scripts\Activate.ps1

python -m pip install -U pip
python -m pip install -U nuitka ordered-set zstandard
python -m pip install -U PySide6 Pillow

# Build
python -m nuitka bulk_cropper_with_preview.py `
  --onefile `
  --enable-plugin=pyside6 `
  --windows-disable-console `
  --assume-yes-for-downloads `
  --output-filename=BulkCropper.exe `
  --company-name="Your Company" `
  --product-name="Bulk Cropper" `
  --file-version=1.1.0 `
  --product-version=1.1.0
#  --windows-icon-from-ico=app.ico   # (uncomment if you have an icon)
#  --onefile-tempdir-spec=%TEMP%\BulkCropper `  # optional faster start
#  --nofollow-imports  # optional: if your imports are strict
