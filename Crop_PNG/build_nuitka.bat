@echo off
REM build_nuitka.bat
REM One-file EXE build for Bulk Cropper (PySide6)
REM Usage (Cmd):  build_nuitka.bat

REM Optional: create/activate venv
REM python -m venv .venv
REM call .\.venv\Scripts\activate.bat

python -m pip install -U pip
python -m pip install -U nuitka ordered-set zstandard
python -m pip install -U PySide6 Pillow

python -m nuitka bulk_cropper_with_preview.py ^
  --onefile ^
  --enable-plugin=pyside6 ^
  --windows-disable-console ^
  --assume-yes-for-downloads ^
  --output-filename=BulkCropper.exe ^
  --company-name="Your Company" ^
  --product-name="Bulk Cropper" ^
  --file-version=1.1.0 ^
  --product-version=1.1.0
REM  --windows-icon-from-ico=app.ico
REM  --onefile-tempdir-spec=%%TEMP%%\BulkCropper
REM  --nofollow-imports
