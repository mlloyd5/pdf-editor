from __future__ import annotations

import tempfile
from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
)


def _make_temp_pdf() -> Path:
    fd, name = tempfile.mkstemp(suffix=".pdf")
    import os

    os.close(fd)
    return Path(name)


def _fmt_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


class CompressDialog(QDialog):
    """Dialog for compressing a PDF."""

    def __init__(self, source: Path, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Compress PDF")
        self.setMinimumWidth(400)
        self._source = source
        self.result_path: Path | None = None
        self.original_size_str = ""
        self.compressed_size_str = ""

        layout = QVBoxLayout(self)

        # Current file info
        orig_size = source.stat().st_size
        self.original_size_str = _fmt_size(orig_size)
        layout.addWidget(QLabel(f"Current size: {self.original_size_str}"))

        # Level selection
        group = QGroupBox("Compression Level")
        group_layout = QVBoxLayout()
        self._radio_low = QRadioButton("Low — lossless optimization")
        self._radio_medium = QRadioButton("Medium — recompress streams (recommended)")
        self._radio_high = QRadioButton("High — aggressive, may reduce image quality")
        self._radio_medium.setChecked(True)
        group_layout.addWidget(self._radio_low)
        group_layout.addWidget(self._radio_medium)
        group_layout.addWidget(self._radio_high)
        group.setLayout(group_layout)
        layout.addWidget(group)

        # DPI
        dpi_layout = QHBoxLayout()
        dpi_layout.addWidget(QLabel("Image DPI (for High):"))
        self._dpi_spin = QSpinBox()
        self._dpi_spin.setRange(72, 600)
        self._dpi_spin.setValue(150)
        self._dpi_spin.setEnabled(False)
        dpi_layout.addWidget(self._dpi_spin)
        layout.addLayout(dpi_layout)

        self._radio_high.toggled.connect(self._dpi_spin.setEnabled)

        # Result label
        self._result_label = QLabel("")
        layout.addWidget(self._result_label)

        # Buttons
        buttons = QDialogButtonBox()
        self._compress_btn = buttons.addButton("Compress", QDialogButtonBox.ButtonRole.AcceptRole)
        buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        self._compress_btn.clicked.connect(self._do_compress)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _get_level(self):
        from pdf_editor.core.optimize import CompressionLevel

        if self._radio_low.isChecked():
            return CompressionLevel.LOW
        if self._radio_high.isChecked():
            return CompressionLevel.HIGH
        return CompressionLevel.MEDIUM

    def _do_compress(self) -> None:
        from pdf_editor.core.optimize import compress_pdf

        level = self._get_level()
        output = _make_temp_pdf()

        try:
            _, orig, comp = compress_pdf(
                self._source, output, level=level, image_dpi=self._dpi_spin.value()
            )
            self.original_size_str = _fmt_size(orig)
            self.compressed_size_str = _fmt_size(comp)
            reduction = (1 - comp / orig) * 100 if orig > 0 else 0
            self._result_label.setText(
                f"Result: {self.compressed_size_str} ({reduction:.1f}% reduction)"
            )
            self.result_path = output
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class MergeDialog(QDialog):
    """Dialog for merging multiple PDFs."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Merge PDFs")
        self.setMinimumSize(500, 400)
        self.result_path: Path | None = None

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Add PDF files in the order you want them merged:"))

        self._file_list = QListWidget()
        layout.addWidget(self._file_list)

        # File list buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Files...")
        remove_btn = QPushButton("Remove")
        up_btn = QPushButton("Move Up")
        down_btn = QPushButton("Move Down")
        add_btn.clicked.connect(self._add_files)
        remove_btn.clicked.connect(self._remove_selected)
        up_btn.clicked.connect(self._move_up)
        down_btn.clicked.connect(self._move_down)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(up_btn)
        btn_layout.addWidget(down_btn)
        layout.addLayout(btn_layout)

        # Buttons
        buttons = QDialogButtonBox()
        merge_btn = buttons.addButton("Merge", QDialogButtonBox.ButtonRole.AcceptRole)
        buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        merge_btn.clicked.connect(self._do_merge)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _add_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", "", "PDF Files (*.pdf)")
        for p in paths:
            self._file_list.addItem(p)

    def _remove_selected(self) -> None:
        for item in self._file_list.selectedItems():
            self._file_list.takeItem(self._file_list.row(item))

    def _move_up(self) -> None:
        row = self._file_list.currentRow()
        if row > 0:
            item = self._file_list.takeItem(row)
            self._file_list.insertItem(row - 1, item)
            self._file_list.setCurrentRow(row - 1)

    def _move_down(self) -> None:
        row = self._file_list.currentRow()
        if row < self._file_list.count() - 1:
            item = self._file_list.takeItem(row)
            self._file_list.insertItem(row + 1, item)
            self._file_list.setCurrentRow(row + 1)

    def _do_merge(self) -> None:
        if self._file_list.count() < 2:
            QMessageBox.warning(self, "Not Enough Files", "Add at least 2 files to merge.")
            return

        from pdf_editor.core.merge import merge_pdfs

        inputs = [Path(self._file_list.item(i).text()) for i in range(self._file_list.count())]
        output = _make_temp_pdf()

        try:
            merge_pdfs(inputs, output)
            self.result_path = output
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class InsertImageDialog(QDialog):
    """Dialog for inserting an image into a PDF page."""

    def __init__(self, source: Path, current_page: int, page_count: int, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Insert Image")
        self.setMinimumWidth(400)
        self._source = source
        self.result_path: Path | None = None

        layout = QVBoxLayout(self)

        # Image file
        img_layout = QHBoxLayout()
        img_layout.addWidget(QLabel("Image:"))
        self._img_path_label = QLabel("No image selected")
        self._img_path_label.setStyleSheet("color: gray;")
        img_layout.addWidget(self._img_path_label, 1)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_image)
        img_layout.addWidget(browse_btn)
        layout.addLayout(img_layout)

        self._image_path: Path | None = None

        # Page
        page_layout = QHBoxLayout()
        page_layout.addWidget(QLabel("Page:"))
        self._page_spin = QSpinBox()
        self._page_spin.setRange(1, page_count)
        self._page_spin.setValue(current_page + 1)
        page_layout.addWidget(self._page_spin)
        page_layout.addStretch()
        layout.addLayout(page_layout)

        # Position
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("Position:"))
        self._position_combo = QComboBox()
        self._position_combo.addItems(
            [
                "center",
                "top-left",
                "top-right",
                "bottom-left",
                "bottom-right",
            ]
        )
        pos_layout.addWidget(self._position_combo)
        pos_layout.addStretch()
        layout.addLayout(pos_layout)

        # Scale
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Scale:"))
        self._scale_spin = QDoubleSpinBox()
        self._scale_spin.setRange(0.1, 5.0)
        self._scale_spin.setValue(1.0)
        self._scale_spin.setSingleStep(0.1)
        scale_layout.addWidget(self._scale_spin)
        scale_layout.addStretch()
        layout.addLayout(scale_layout)

        # Buttons
        buttons = QDialogButtonBox()
        insert_btn = buttons.addButton("Insert", QDialogButtonBox.ButtonRole.AcceptRole)
        buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        insert_btn.clicked.connect(self._do_insert)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if path:
            self._image_path = Path(path)
            self._img_path_label.setText(self._image_path.name)
            self._img_path_label.setStyleSheet("")

    def _do_insert(self) -> None:
        if not self._image_path:
            QMessageBox.warning(self, "No Image", "Select an image file first.")
            return

        from pdf_editor.core.images import ImagePosition, insert_image

        position = ImagePosition(self._position_combo.currentText())
        page_index = self._page_spin.value() - 1
        scale = self._scale_spin.value()

        output = _make_temp_pdf()

        try:
            insert_image(
                self._source,
                self._image_path,
                output,
                page_index=page_index,
                position=position,
                scale=scale,
            )
            self.result_path = output
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
