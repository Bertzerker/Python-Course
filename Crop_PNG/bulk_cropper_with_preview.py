#!/usr/bin/env python3
"""
Qt6 Bulk Picture Cropping Tool with Live Preview

Features
- Choose input & output folders
- Enter exact crop dimensions (px)
- Choose cropping anchor (preserve area: TL/T/ TR / L / C / R / BL / B / BR)
- Optional: split each picture into two halves (vertical L/R or horizontal T/B) before cropping
  → When splitting, the anchor point is mirrored for the second half.
  → Optional: remove a center “book spine” gutter by N pixels before splitting.
- New: Live visual preview (auto-refresh) with colored overlays.
  - Green / Yellow = preserved areas
  - Red = discarded area
  - White text = crop size and anchor

Dependencies:
    pip install PySide6 Pillow

Run:
    python bulk_cropper_with_preview.py
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Iterable, Optional

from PIL import Image, ImageQt

from PySide6.QtCore import Qt, QObject, Signal, QThread, QTimer, QRectF, QSize
from PySide6.QtGui import QAction, QPixmap, QPainter, QColor, QFont, QPen
from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QSpinBox, QComboBox, QCheckBox, QProgressBar, QTextEdit,
    QMessageBox, QVBoxLayout, QGroupBox, QSizePolicy, QHBoxLayout
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

SPLIT_MODES = [
    ("Don't split", "none"),
    ("Vertical (Left/Right)", "vertical"),
    ("Horizontal (Top/Bottom)", "horizontal"),
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
    split_mode: str  # 'none' | 'vertical' | 'horizontal'
    center_trim: int  # pixels to remove at center (book spine)


class CropWorker(QObject):
    progress = Signal(int, int)
    message = Signal(str)
    finished = Signal(int, int)

    def __init__(self, config: JobConfig, files: List[Path]):
        super().__init__()
        self.config = config
        self.files = files
        self._cancel = False

    def cancel(self):
        self._cancel = True

    @staticmethod
    def _compute_origin(W: int, H: int, w: int, h: int, ax: str, ay: str) -> Tuple[int, int]:
        # Compute top-left of crop box based on anchor
        if ax == "left":
            x0 = 0
        elif ax == "center":
            x0 = (W - w) // 2
        elif ax == "right":
            x0 = W - w
        else:
            x0 = 0

        if ay == "top":
            y0 = 0
        elif ay == "center":
            y0 = (H - h) // 2
        elif ay == "bottom":
            y0 = H - h
        else:
            y0 = 0

        # Clamp
        x0 = max(0, min(x0, max(0, W - w)))
        y0 = max(0, min(y0, max(0, H - h)))
        return x0, y0

    def _iter_halves(self, im: Image.Image) -> Iterable[Tuple[str, Image.Image, str, str]]:
        """
        Yield (tag, image, anchor_x, anchor_y) for each half based on split mode.
        Respects center_trim (book spine gutter) when splitting.
        """
        mode = self.config.split_mode
        W, H = im.size
        ax, ay = self.config.anchor_x, self.config.anchor_y
        g = max(0, int(self.config.center_trim))

        if mode == "vertical":
            if g >= W:
                return
            left_end = (W - g) // 2
            right_start = W - left_end
            if left_end <= 0 or right_start >= W:
                return
            left_box = (0, 0, left_end, H)
            right_box = (right_start, 0, W, H)
            mirror_ax = {"left": "right", "right": "left"}.get(ax, ax)
            yield ("left", im.crop(left_box), ax, ay)
            yield ("right", im.crop(right_box), mirror_ax, ay)
        elif mode == "horizontal":
            if g >= H:
                return
            top_end = (H - g) // 2
            bottom_start = H - top_end
            if top_end <= 0 or bottom_start >= H:
                return
            top_box = (0, 0, W, top_end)
            bottom_box = (0, bottom_start, W, H)
            mirror_ay = {"top": "bottom", "bottom": "top"}.get(ay, ay)
            yield ("top", im.crop(top_box), ax, ay)
            yield ("bottom", im.crop(bottom_box), ax, mirror_ay)
        else:
            yield ("full", im, ax, ay)

    def run(self):
        processed = 0
        skipped = 0
        total = len(self.files)
        w = self.config.width
        h = self.config.height
        try:
            for idx, src in enumerate(self.files, start=1):
                if self._cancel:
                    self.message.emit("Cancelled by user.")
                    break
                try:
                    with Image.open(src) as im:
                        im.load()
                        for half_tag, sub_im, ax, ay in self._iter_halves(im):
                            W, H = sub_im.size
                            if w > W or h > H:
                                skipped += 1
                                self.message.emit(
                                    f"SKIP: {src.name} [{half_tag}] — requested {w}x{h} larger than image {W}x{H}."
                                )
                                continue
                            x0, y0 = self._compute_origin(W, H, w, h, ax, ay)
                            crop_box = (x0, y0, x0 + w, y0 + h)
                            cropped = sub_im.crop(crop_box)

                            # Output path & saving
                            format_ext = src.suffix.lower()
                            target_name = src.stem
                            if half_tag != "full":
                                target_name += f"_{half_tag}"
                            if self.config.add_suffix:
                                target_name += f"_crop_{w}x{h}"
                            dst = self.config.out_dir / f"{target_name}{format_ext}"
                            if dst.exists() and not self.config.overwrite:
                                skipped += 1
                                self.message.emit(f"SKIP: {dst.name} exists (overwrite disabled).")
                                continue
                            save_params = {}
                            if format_ext in (".jpg", ".jpeg"):
                                if cropped.mode in ("RGBA", "P"):
                                    cropped = cropped.convert("RGB")
                                save_params.update({"quality": 95, "optimize": True})
                            cropped.save(dst, **save_params)
                            processed += 1
                            self.message.emit(f"OK: {dst}")
                except Exception as e:
                    skipped += 1
                    self.message.emit(f"ERROR: {src.name} — {e}")
                self.progress.emit(idx, total)
        finally:
            self.finished.emit(processed, skipped)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bulk Picture Cropper – Qt6")
        self.resize(900, 760)

        self._thread: Optional[QThread] = None
        self._worker: Optional[CropWorker] = None

        # Debounce timer for preview
        self.preview_timer = QTimer(self)
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview)

        # --- Folders ---
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
        self.w_spin = QSpinBox(); self.w_spin.setRange(1, 20000); self.w_spin.setValue(1080)
        self.h_spin = QSpinBox(); self.h_spin.setRange(1, 20000); self.h_spin.setValue(1080)

        self.anchor_combo = QComboBox()
        for label, (ax, ay) in ANCHORS:
            self.anchor_combo.addItem(label, userData=(ax, ay))
        self.anchor_combo.setCurrentIndex(4)

        self.split_combo = QComboBox()
        for label, key in SPLIT_MODES:
            self.split_combo.addItem(label, userData=key)
        self.split_combo.setCurrentIndex(0)

        self.center_trim_spin = QSpinBox()
        self.center_trim_spin.setRange(0, 10000)
        self.center_trim_spin.setValue(0)
        self.center_trim_spin.setSingleStep(2)

        self.suffix_check = QCheckBox("Add filename suffix (e.g. _crop_800x600)"); self.suffix_check.setChecked(True)
        self.overwrite_check = QCheckBox("Overwrite if file exists")

        opts_box = QGroupBox("Crop Settings")
        opts_layout = QGridLayout(opts_box)
        opts_layout.addWidget(QLabel("Width (px)"), 0, 0);  opts_layout.addWidget(self.w_spin, 0, 1)
        opts_layout.addWidget(QLabel("Height (px)"), 0, 2); opts_layout.addWidget(self.h_spin, 0, 3)
        opts_layout.addWidget(QLabel("Anchor"), 1, 0);      opts_layout.addWidget(self.anchor_combo, 1, 1)
        opts_layout.addWidget(QLabel("Split mode"), 1, 2);  opts_layout.addWidget(self.split_combo, 1, 3)
        opts_layout.addWidget(QLabel("Middle crop (px)"), 2, 0); opts_layout.addWidget(self.center_trim_spin, 2, 1)
        opts_layout.addWidget(self.suffix_check, 3, 0, 1, 2)
        opts_layout.addWidget(self.overwrite_check, 3, 2, 1, 2)

        # Enable/disable center trim control based on split mode
        def _toggle_center_trim():
            enable = self.split_combo.currentData() in ("vertical", "horizontal")
            self.center_trim_spin.setEnabled(enable)
        self.split_combo.currentIndexChanged.connect(_toggle_center_trim)
        _toggle_center_trim()

        # --- Preview ---
        self.preview_label = QLabel("Preview will appear here")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview_label.setMinimumHeight(320)

        # --- Run ---
        self.start_btn = QPushButton("Start Cropping")
        self.cancel_btn = QPushButton("Cancel"); self.cancel_btn.setEnabled(False)
        self.progress = QProgressBar(); self.progress.setRange(0, 100)
        self.log = QTextEdit(); self.log.setReadOnly(True)

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
        root.addWidget(self.preview_label)
        root.addWidget(run_box)

        # Actions
        self.start_btn.clicked.connect(self.start)
        self.cancel_btn.clicked.connect(self.cancel)
        self._add_actions()

        # Live preview triggers
        self.w_spin.valueChanged.connect(self.schedule_preview)
        self.h_spin.valueChanged.connect(self.schedule_preview)
        self.anchor_combo.currentIndexChanged.connect(self.schedule_preview)
        self.split_combo.currentIndexChanged.connect(self.schedule_preview)
        self.center_trim_spin.valueChanged.connect(self.schedule_preview)
        self.in_edit.textChanged.connect(self.schedule_preview)

    # ------------- Preview logic -------------
    def schedule_preview(self):
        # Debounce: wait 250 ms after last change
        self.preview_timer.start(250)

    def _load_first_image(self) -> Optional[Image.Image]:
        folder = Path(self.in_edit.text().strip())
        if not folder.is_dir():
            return None
        for p in sorted(folder.iterdir()):
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS:
                try:
                    im = Image.open(p)
                    im.load()
                    return im
                except Exception:
                    continue
        return None

    def _calc_crop_rect(self, W: int, H: int, w: int, h: int, ax: str, ay: str) -> QRectF:
        x0 = {"left": 0, "center": (W - w) // 2, "right": W - w}.get(ax, 0)
        y0 = {"top": 0, "center": (H - h) // 2, "bottom": H - h}.get(ay, 0)
        x0 = max(0, min(x0, max(0, W - w)))
        y0 = max(0, min(y0, max(0, H - h)))
        return QRectF(float(x0), float(y0), float(w), float(h))

    def update_preview(self):
        im = self._load_first_image()
        if im is None:
            self.preview_label.setText("Select an input folder with at least one JPG/PNG image.")
            self.preview_label.setPixmap(QPixmap())
            return

        imgW, imgH = im.size
        cropW, cropH = int(self.w_spin.value()), int(self.h_spin.value())
        split_mode = self.split_combo.currentData()
        center_trim = int(self.center_trim_spin.value())
        anchor_x, anchor_y = self.anchor_combo.currentData()

        # Create base pixmap
        qimg = ImageQt.ImageQt(im)
        pixmap = QPixmap.fromImage(qimg)
        # Draw in image coordinates, scale at the very end (better accuracy for overlay)
        canvas = QPixmap(pixmap.size())
        canvas.fill(Qt.transparent)

        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fill everything as discarded (red) first
        painter.drawPixmap(0, 0, pixmap)
        painter.fillRect(0, 0, imgW, imgH, QColor(255, 0, 0, 90))

        green = QColor(0, 200, 0, 130)
        yellow = QColor(255, 220, 0, 130)
        pen_white = QPen(Qt.white); pen_white.setWidth(2)
        font = QFont(); font.setPointSize(11)
        painter.setFont(font)

        def label_text(ax: str, ay: str) -> str:
            return f"{cropW}x{cropH} – {ax}/{ay}"

        if split_mode == "vertical":
            if center_trim >= imgW:
                # nothing to show
                pass
            else:
                left_end = (imgW - center_trim) // 2
                right_start = imgW - left_end
                # Left half
                rectL = self._calc_crop_rect(left_end, imgH, cropW, cropH, anchor_x, anchor_y)
                painter.fillRect(rectL, green)
                painter.setPen(pen_white); painter.drawRect(rectL)
                painter.drawText(rectL, Qt.AlignCenter, label_text(anchor_x, anchor_y))
                # Right half (mirrored anchor_x)
                mirror_ax = {"left": "right", "right": "left"}.get(anchor_x, anchor_x)
                rectR_local = self._calc_crop_rect(left_end, imgH, cropW, cropH, mirror_ax, anchor_y)
                rectR = QRectF(rectR_local)
                rectR.translate(right_start - left_end, 0)
                painter.fillRect(rectR, yellow)
                painter.setPen(pen_white); painter.drawRect(rectR)
                painter.drawText(rectR, Qt.AlignCenter, label_text(mirror_ax, anchor_y))
        elif split_mode == "horizontal":
            if center_trim >= imgH:
                pass
            else:
                top_end = (imgH - center_trim) // 2
                bottom_start = imgH - top_end
                # Top half
                rectT = self._calc_crop_rect(imgW, top_end, cropW, cropH, anchor_x, anchor_y)
                painter.fillRect(rectT, green)
                painter.setPen(pen_white); painter.drawRect(rectT)
                painter.drawText(rectT, Qt.AlignCenter, label_text(anchor_x, anchor_y))
                # Bottom half (mirrored anchor_y)
                mirror_ay = {"top": "bottom", "bottom": "top"}.get(anchor_y, anchor_y)
                rectB_local = self._calc_crop_rect(imgW, top_end, cropW, cropH, anchor_x, mirror_ay)
                rectB = QRectF(rectB_local)
                rectB.translate(0, bottom_start - top_end)
                painter.fillRect(rectB, yellow)
                painter.setPen(pen_white); painter.drawRect(rectB)
                painter.drawText(rectB, Qt.AlignCenter, label_text(anchor_x, mirror_ay))
        else:
            rect = self._calc_crop_rect(imgW, imgH, cropW, cropH, anchor_x, anchor_y)
            painter.fillRect(rect, green)
            painter.setPen(pen_white); painter.drawRect(rect)
            painter.drawText(rect, Qt.AlignCenter, label_text(anchor_x, anchor_y))

        painter.end()

        # Finally scale to preview label size
        scaled = canvas.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(scaled)

    # ------------- Run logic -------------
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
        return [p for p in sorted(in_dir.iterdir()) if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS]

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
        split_mode = self.split_combo.currentData()
        center_trim = int(self.center_trim_spin.value())

        cfg = JobConfig(
            in_dir=in_dir,
            out_dir=out_dir,
            width=w,
            height=h,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            add_suffix=self.suffix_check.isChecked(),
            overwrite=self.overwrite_check.isChecked(),
            split_mode=split_mode,
            center_trim=center_trim,
        )

        # Prepare UI
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress.setValue(0)
        self.log.append(f"Found {len(files)} images. Split: {split_mode}, middle crop: {center_trim}px. Starting…")

        # Threading
        self._thread = QThread(self)
        self._worker = CropWorker(cfg, files)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self.on_progress)
        self._worker.message.connect(self.on_message)
        self._worker.finished.connect(self.on_finished)
        self._worker.finished.connect(self._thread.quit)

        # Clean up after thread stops
        self._thread.finished.connect(self._worker.deleteLater)
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

    # Context actions
    def _add_actions(self):
        act = QAction("Clear Log", self)
        act.triggered.connect(self.log.clear)
        self.addAction(act)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
