from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt, QThreadPool, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QAbstractItemView, QListWidget, QListWidgetItem

from pdf_editor.core.render import render_page_thumbnail
from pdf_editor.gui.workers import Worker


class ThumbnailListWidget(QListWidget):
    """Sidebar showing page thumbnails with drag-and-drop reordering."""

    page_selected = Signal(int)
    pages_reordered = Signal(list)

    THUMB_WIDTH = 140
    THUMB_HEIGHT = 180

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._source: Path | None = None
        self._page_count = 0
        self._pool = QThreadPool.globalInstance()
        self._pending_workers: list = []  # prevent GC of workers before signal delivery

        self.setViewMode(QListWidget.ViewMode.ListMode)
        self.setIconSize(QSize(self.THUMB_WIDTH, self.THUMB_HEIGHT))
        self.setSpacing(4)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setMinimumWidth(self.THUMB_WIDTH + 60)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Drag-and-drop reordering
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)

        self.currentRowChanged.connect(self._on_row_changed)

    def load_pdf(self, source: Path) -> None:
        """Load thumbnails for all pages in the PDF."""
        self.clear()
        self._pending_workers.clear()
        self._source = source

        from pdf_editor.core.pages import get_page_count

        self._page_count = get_page_count(source)

        # Create placeholder items
        for i in range(self._page_count):
            item = QListWidgetItem(f"Page {i + 1}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            item.setSizeHint(QSize(self.THUMB_WIDTH + 40, self.THUMB_HEIGHT + 10))
            self.addItem(item)
            # Launch async thumbnail render
            self._load_thumbnail_async(source, i)

        if self._page_count > 0:
            self.setCurrentRow(0)

    def _load_thumbnail_async(self, source: Path, page_index: int) -> None:
        worker = Worker(
            render_page_thumbnail,
            source,
            page_index,
            max_width=self.THUMB_WIDTH,
            max_height=self.THUMB_HEIGHT,
        )
        worker.setAutoDelete(False)
        worker.signals.finished.connect(
            lambda data, idx=page_index, w=worker: self._on_thumbnail_ready(idx, data, w)
        )
        self._pending_workers.append(worker)
        self._pool.start(worker)

    def _on_thumbnail_ready(self, page_index: int, png_data: bytes, worker: Worker) -> None:
        if worker in self._pending_workers:
            self._pending_workers.remove(worker)
        if page_index >= self.count():
            return
        pixmap = QPixmap()
        pixmap.loadFromData(png_data, "PNG")
        item = self.item(page_index)
        if item:
            item.setIcon(QIcon(pixmap))

    def _on_row_changed(self, row: int) -> None:
        if row >= 0:
            item = self.item(row)
            if item:
                page_index = item.data(Qt.ItemDataRole.UserRole)
                self.page_selected.emit(page_index)

    def dropEvent(self, event) -> None:
        # Capture order before drop
        old_order = [self.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.count())]
        super().dropEvent(event)
        # Capture order after drop
        new_order = [self.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.count())]
        if new_order != old_order:
            # Update labels
            for i in range(self.count()):
                self.item(i).setText(f"Page {i + 1}")
            self.pages_reordered.emit(new_order)

    def selected_page_indices(self) -> list[int]:
        """Return the original page indices of currently selected items."""
        return [item.data(Qt.ItemDataRole.UserRole) for item in self.selectedItems()]

    def current_page_index(self) -> int | None:
        """Return the page index of the currently focused item."""
        item = self.currentItem()
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None
