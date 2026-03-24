from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QPixmap, QWheelEvent
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView

from pdf_editor.core.render import render_page_preview
from pdf_editor.gui.workers import Worker


class PagePreviewWidget(QGraphicsView):
    """Zoomable page preview using QGraphicsView."""

    ZOOM_FACTOR = 1.15
    MIN_ZOOM = 0.1
    MAX_ZOOM = 5.0

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._pixmap_item: QGraphicsPixmapItem | None = None
        self._current_zoom = 1.0
        self._pool = QThreadPool.globalInstance()
        self._source: Path | None = None
        self._page_index: int = 0
        self._current_worker: Worker | None = None

        from PySide6.QtGui import QPainter

        self.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(Qt.GlobalColor.darkGray)

    def show_page(self, source: Path, page_index: int) -> None:
        """Render and display a page asynchronously."""
        self._source = source
        self._page_index = page_index

        # Show loading state
        self._scene.clear()
        self._pixmap_item = None
        text = self._scene.addText("Loading...")
        text.setDefaultTextColor(Qt.GlobalColor.white)

        worker = Worker(render_page_preview, source, page_index, dpi=150)
        worker.setAutoDelete(False)
        worker.signals.finished.connect(self._on_preview_ready)
        worker.signals.error.connect(self._on_preview_error)
        self._current_worker = worker  # prevent GC before signal delivery
        self._pool.start(worker)

    def _on_preview_ready(self, png_data: bytes) -> None:
        pixmap = QPixmap()
        pixmap.loadFromData(png_data, "PNG")

        self._scene.clear()
        self._pixmap_item = self._scene.addPixmap(pixmap)
        self._scene.setSceneRect(pixmap.rect().toRectF())

        # Fit to view on first load
        self._current_zoom = 1.0
        self.resetTransform()
        self.fitInView(self._pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

    def _on_preview_error(self, error_msg: str) -> None:
        self._scene.clear()
        text = self._scene.addText("Error loading page")
        text.setDefaultTextColor(Qt.GlobalColor.red)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Zoom with Ctrl+Scroll."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = self.ZOOM_FACTOR if event.angleDelta().y() > 0 else 1.0 / self.ZOOM_FACTOR

            new_zoom = self._current_zoom * factor
            if self.MIN_ZOOM <= new_zoom <= self.MAX_ZOOM:
                self._current_zoom = new_zoom
                self.scale(factor, factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def fit_to_width(self) -> None:
        """Fit the page to the view width."""
        if self._pixmap_item:
            self.resetTransform()
            self._current_zoom = 1.0
            self.fitInView(self._pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
