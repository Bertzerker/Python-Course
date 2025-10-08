#!/usr/bin/env python3
"""
Qt6 Bulk Picture Cropping Tool

Features
- Choose input & output folders
- Enter exact crop dimensions (px)
- Choose cropping anchor (preserve area: TL/T/ TR / L / C / R / BL / B / BR)
- Supports JPG/JPEG and PNG
- Start button, progress bar, and log output
- Skips images smaller than requested crop (to truly "crop" rather than upscale)

Dependencies
    pip install PySide6 Pillow

Run
    python bulk_cropper.py
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from PIL import Image

from PySide6.QtCore import Qt, QObject, Signal, QThread
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QSpinBox,
    QComboBox,
    QCheckBox,
    QProgressBar,
    QTextEdit,
    QMessageBox,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
)

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png"}

ANCHORS = [
    ("Top-Left", ("left", "top")),
    ("Top", ("center", "top")),
    ("Top-Right", ("right", "top")),
    ("Left", ("left", "center")),
    ("Center", ("center", "center")),
    ("Right", ("right", "center")),
    ("Bottom-Left", ("left", "bottom")),
    ("Bottom", ("center", "bottom")),
    ("Bottom-Right", ("right", "bottom")),
]


@dataclass
class JobConfig:
    in_dir: Path
    out_dir: Path
    width: int
    height: int
    anchor_x: str
    anchor_y: str
    add_suffix: bool
    overwrite: bool


class CropWorker(QObject):
    progress = Signal(int, int)  # done, total
    message = Signal(str)
    finished = Signal(int, int)  # processed, skipped

    def __init__(self, config: JobConfig, files: List[Path]):
        super().__init__()
        self.config = config
        self.files = files
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def _compute_origin(self, W: int, H: int, w: int, h: int) -> Tuple[int, int]:
        # horizontal
        if self.config.anchor_x == "left":
            x0 = 0
        elif self.config.anchor_x == "center":
            x0 = (W - w) // 2
        elif self.config.anchor_x == "right":
            x0 = W - w
        else:
            x0 = max(0, (W - w) // 2)

        # vertical
        if self.config.anchor_y == "top":
            y0 = 0
        elif self.config.anchor_y == "center":
            y0 = (H - h) // 2
        elif self.config.anchor_y == "bottom":
            y0 = H - h
        else:
            y0 = max(0, (H - h) // 2)

        # clamp
        x0 = max(0, min(x0, max(0, W - w)))
        y0 = max(0, min(y0, max(0, H - h)))
        return x0, y0

    def run(self):
        processed = 0
        skipped = 0
        total = len(self.files)
        w = self.config.width
        h = self.config.height

        for idx, src in enumerate(self.files, start=1):
            if self._cancel:
                self.message.emit("Cancelled by user.")
                break

            try:
                with Image.open(src) as im:
                    im.load()
                    W, H = im.size
                    if w > W or h > H:
                        skipped += 1
                        self.message.emit(
                            f"SKIP: {src.name} — requested {w}x{h} larger than image {W}x{H}."
                        )
                    else:
                        x0, y0 = self._compute_origin(W, H, w, h)
                        crop_box = (x0, y0, x0 + w, y0 + h)
                        cropped = im.crop(crop_box)

                        # Preserve format & basic metadata if possible
                        format_ext = src.suffix.lower()
                        target_name = src.stem
                        if self.config.add_suffix:
                            target_name += f"_crop_{w}x{h}"
                        dst = self.config.out_dir / f"{target_name}{format_ext}"

                        if dst.exists() and not self.config.overwrite:
                            skipped += 1
                            self.message.emit(
                                f"SKIP: {dst.name} exists (overwrite disabled)."
                            )
                        else:
                            save_params = {}
                            if format_ext in (".jpg", ".jpeg"):
                                # Ensure mode compatible with JPEG
                                if cropped.mode in ("RGBA", "P"):
                                    cropped = cropped.convert("RGB")
                                save_params.update({"quality": 95, "optimize": True})
                            cropped.save(dst, **save_params)
                            processed += 1
                            self.message.emit(
                                f"OK: {src.name} -> {dst.relative_to(self.config.out_dir.parent)}"
                            )

            except Exception as e:
                skipped += 1
                self.message.emit(f"ERROR: {src.name} — {e}")

            self.progress.emit(idx, total)

        self.finished.emit(processed, skipped)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bulk Picture Cropper – Qt6")
        self.resize(760, 520)
        self._thread: QThread | None = None
        self._worker: CropWorker | None = None

        # --- Paths ---
        self.in_edit = QLineEdit()
        self.in_btn = QPushButton("Browse…")
        self.in_btn.clicked.connect(self.pick_input)

        self.out_edit = QLineEdit()
        self.out_btn = QPushButton("Browse…")
        self.out_btn.clicked.connect(self.pick_output)

        paths_box = QGroupBox("Folders")
        paths_layout = QGridLayout(paths_box)
        paths_layout.addWidget(QLabel("Input folder"), 0, 0)
        paths_layout.addWidget(self.in_edit, 0, 1)
        paths_layout.addWidget(self.in_btn, 0, 2)
        paths_layout.addWidget(QLabel("Output folder"), 1, 0)
        paths_layout.addWidget(self.out_edit, 1, 1)
        paths_layout.addWidget(self.out_btn, 1, 2)

        # --- Options ---
        self.w_spin = QSpinBox()
        self.w_spin.setRange(1, 20000)
        self.w_spin.setValue(1080)
        self.h_spin = QSpinBox()
        self.h_spin.setRange(1, 20000)
        self.h_spin.setValue(1080)

        self.anchor_combo = QComboBox()
        for label, (ax, ay) in ANCHORS:
            self.anchor_combo.addItem(label, userData=(ax, ay))
        self.anchor_combo.setCurrentIndex(4)  # Center

        self.suffix_check = QCheckBox("Add filename suffix (e.g. _crop_800x600)")
        self.suffix_check.setChecked(True)
        self.overwrite_check = QCheckBox("Overwrite if file exists")

        opts_box = QGroupBox("Crop Settings")
        opts_layout = QGridLayout(opts_box)
        opts_layout.addWidget(QLabel("Width (px)"), 0, 0)
        opts_layout.addWidget(self.w_spin, 0, 1)
        opts_layout.addWidget(QLabel("Height (px)"), 0, 2)
        opts_layout.addWidget(self.h_spin, 0, 3)
        opts_layout.addWidget(QLabel("Anchor"), 1, 0)
        opts_layout.addWidget(self.anchor_combo, 1, 1)
        opts_layout.addWidget(self.suffix_check, 2, 0, 1, 2)
        opts_layout.addWidget(self.overwrite_check, 2, 2, 1, 2)

        # --- Run ---
        self.start_btn = QPushButton("Start Cropping")
        self.start_btn.clicked.connect(self.start)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        run_box = QGroupBox("Run")
        run_layout = QGridLayout(run_box)
        run_layout.addWidget(self.start_btn, 0, 0)
        run_layout.addWidget(self.cancel_btn, 0, 1)
        run_layout.addWidget(self.progress, 1, 0, 1, 2)
        run_layout.addWidget(self.log, 2, 0, 1, 2)

        # --- Main layout ---
        root = QVBoxLayout(self)
        root.addWidget(paths_box)
        root.addWidget(opts_box)
        root.addWidget(run_box)

        # Menu action for quick help (optional)
        self._add_actions()

    def _add_actions(self):
        # Add a context menu action to clear log
        self.clear_log_action = QAction("Clear Log", self)
        self.clear_log_action.triggered.connect(lambda: self.log.clear())
        self.addAction(self.clear_log_action)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

    # --- UI callbacks ---
    def pick_input(self):
        path = QFileDialog.getExistingDirectory(self, "Select input folder")
        if path:
            self.in_edit.setText(path)

    def pick_output(self):
        path = QFileDialog.getExistingDirectory(self, "Select output folder")
        if path:
            self.out_edit.setText(path)

    def validate(self) -> Tuple[bool, str]:
        in_dir = Path(self.in_edit.text()).expanduser()
        out_dir = Path(self.out_edit.text()).expanduser()
        if not in_dir.is_dir():
            return False, "Please choose a valid input folder."
        if not out_dir.exists():
            try:
                out_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"Cannot create output folder: {e}"
        if not out_dir.is_dir():
            return False, "Output path is not a folder."

        return True, ""

    def gather_files(self, in_dir: Path) -> List[Path]:
        files: List[Path] = []
        for p in sorted(in_dir.iterdir()):
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS:
                files.append(p)
        return files

    def start(self):
        ok, msg = self.validate()
        if not ok:
            QMessageBox.warning(self, "Invalid settings", msg)
            return

        in_dir = Path(self.in_edit.text()).expanduser()
        out_dir = Path(self.out_edit.text()).expanduser()
        files = self.gather_files(in_dir)
        if not files:
            QMessageBox.information(self, "No images", "No JPG/PNG files found in the input folder.")
            return

        w = int(self.w_spin.value())
        h = int(self.h_spin.value())
        anchor_x, anchor_y = self.anchor_combo.currentData()

        cfg = JobConfig(
            in_dir=in_dir,
            out_dir=out_dir,
            width=w,
            height=h,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            add_suffix=self.suffix_check.isChecked(),
            overwrite=self.overwrite_check.isChecked(),
        )

        # Prepare UI
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress.setValue(0)
        self.log.append(f"Found {len(files)} images. Starting…")

        # Threading setup
        self._thread = QThread(self)
        self._worker = CropWorker(cfg, files)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self.on_progress)
        self._worker.message.connect(self.on_message)
        self._worker.finished.connect(self.on_finished)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def cancel(self):
        if self._worker is not None:
            self._worker.cancel()
        self.cancel_btn.setEnabled(False)

    def on_progress(self, done: int, total: int):
        pct = int((done / max(1, total)) * 100)
        self.progress.setValue(pct)

    def on_message(self, msg: str):
        self.log.append(msg)

    def on_finished(self, processed: int, skipped: int):
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress.setValue(100)
        self.log.append("")
        self.log.append(f"Done. Processed: {processed}, Skipped: {skipped}.")
        self._worker = None
        self._thread = None


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
