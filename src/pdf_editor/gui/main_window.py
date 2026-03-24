from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
)

from pdf_editor.gui.widgets.page_preview import PagePreviewWidget
from pdf_editor.gui.widgets.thumbnail_list import ThumbnailListWidget
from pdf_editor.gui.widgets.toolbar import create_toolbar
from pdf_editor.gui.workers import Worker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PDF Editor")
        self.resize(1100, 750)

        # Document state
        self._current_file: Path | None = None
        self._working_file: Path | None = None
        self._temp_dir: tempfile.TemporaryDirectory | None = None
        self._unsaved_changes = False
        self._pool = QThreadPool.globalInstance()
        self._active_worker = None  # prevent GC of operation workers

        self._setup_ui()
        self._setup_menus()
        self._connect_signals()
        self._update_title()
        self.statusBar().showMessage("No file loaded")

    # ── UI Setup ──────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self._thumbnail_list = ThumbnailListWidget()
        self._preview = PagePreviewWidget()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._thumbnail_list)
        splitter.addWidget(self._preview)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([220, 880])
        self.setCentralWidget(splitter)

        toolbar, self._actions = create_toolbar(self)
        self.addToolBar(toolbar)

        self.setStatusBar(QStatusBar())

    def _setup_menus(self) -> None:
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self._actions["open"])
        file_menu.addAction(self._actions["save"])
        file_menu.addAction(self._actions["save_as"])
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction(self._actions["add_pages"])
        edit_menu.addAction(self._actions["remove_pages"])
        edit_menu.addAction(self._actions["extract_pages"])

        tools_menu = menu_bar.addMenu("Tools")
        tools_menu.addAction(self._actions["merge"])
        tools_menu.addAction(self._actions["compress"])
        tools_menu.addAction(self._actions["insert_image"])

    def _connect_signals(self) -> None:
        # Toolbar actions
        self._actions["open"].triggered.connect(self._open_file)
        self._actions["save"].triggered.connect(self._save_file)
        self._actions["save_as"].triggered.connect(self._save_as_file)
        self._actions["add_pages"].triggered.connect(self._add_pages)
        self._actions["remove_pages"].triggered.connect(self._remove_pages)
        self._actions["extract_pages"].triggered.connect(self._extract_pages)
        self._actions["merge"].triggered.connect(self._merge_pdfs)
        self._actions["compress"].triggered.connect(self._compress_pdf)
        self._actions["insert_image"].triggered.connect(self._insert_image)

        # Thumbnail signals
        self._thumbnail_list.page_selected.connect(self._on_page_selected)
        self._thumbnail_list.pages_reordered.connect(self._on_pages_reordered)

    # ── Document Model ────────────────────────────────────────

    def _create_working_copy(self, source: Path) -> Path:
        """Copy source PDF to a temp directory for non-destructive editing."""
        if self._temp_dir:
            self._temp_dir.cleanup()
        self._temp_dir = tempfile.TemporaryDirectory()
        working = Path(self._temp_dir.name) / "working.pdf"
        shutil.copy2(source, working)
        return working

    def _update_title(self) -> None:
        title = "PDF Editor"
        if self._current_file:
            title = f"{self._current_file.name} — PDF Editor"
            if self._unsaved_changes:
                title = f"* {title}"
        self.setWindowTitle(title)

    def _update_status(self) -> None:
        if not self._working_file:
            self.statusBar().showMessage("No file loaded")
            return
        from pdf_editor.core.optimize import get_file_stats

        stats = get_file_stats(self._working_file)
        size_kb = stats["file_size_bytes"] / 1024
        size_str = f"{size_kb / 1024:.1f} MB" if size_kb > 1024 else f"{size_kb:.1f} KB"
        name = self._current_file.name if self._current_file else "Untitled"
        self.statusBar().showMessage(f"{name} — {stats['page_count']} pages — {size_str}")

    def _mark_unsaved(self) -> None:
        self._unsaved_changes = True
        self._update_title()

    def _reload_document(self, select_page: int = 0) -> None:
        """Reload thumbnails and preview after a modification."""
        if self._working_file:
            self._thumbnail_list.load_pdf(self._working_file)
            self._update_status()
            if select_page >= 0:
                self._thumbnail_list.setCurrentRow(
                    min(select_page, self._thumbnail_list.count() - 1)
                )

    # ── File Operations ───────────────────────────────────────

    def _open_file(self) -> None:
        if self._unsaved_changes and not self._confirm_discard():
            return
        path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if not path:
            return
        self._current_file = Path(path)
        self._working_file = self._create_working_copy(self._current_file)
        self._unsaved_changes = False
        self._reload_document()
        self._update_title()

    def _save_file(self) -> None:
        if not self._working_file:
            return
        if not self._current_file:
            self._save_as_file()
            return
        shutil.copy2(self._working_file, self._current_file)
        self._unsaved_changes = False
        self._update_title()
        self.statusBar().showMessage(f"Saved to {self._current_file}", 3000)

    def _save_as_file(self) -> None:
        if not self._working_file:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF As", "", "PDF Files (*.pdf)")
        if not path:
            return
        dest = Path(path)
        shutil.copy2(self._working_file, dest)
        self._current_file = dest
        self._unsaved_changes = False
        self._update_title()
        self.statusBar().showMessage(f"Saved to {dest}", 3000)

    def _confirm_discard(self) -> bool:
        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            "You have unsaved changes. Discard them?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    def closeEvent(self, event) -> None:
        if self._unsaved_changes and not self._confirm_discard():
            event.ignore()
            return
        if self._temp_dir:
            self._temp_dir.cleanup()
        event.accept()

    # ── Page Selection ────────────────────────────────────────

    def _on_page_selected(self, page_index: int) -> None:
        if self._working_file:
            self._preview.show_page(self._working_file, page_index)

    # ── Page Operations ───────────────────────────────────────

    def _run_operation(self, fn, *args, on_done=None, **kwargs) -> None:
        """Run a core operation in a worker thread."""
        worker = Worker(fn, *args, **kwargs)
        worker.setAutoDelete(False)

        def _on_finished(result):
            self._active_worker = None  # release reference
            if on_done:
                on_done(result)

        def _on_error(msg):
            self._active_worker = None
            QMessageBox.critical(self, "Error", f"Operation failed:\n{msg}")

        worker.signals.finished.connect(_on_finished)
        worker.signals.error.connect(_on_error)
        self._active_worker = worker  # prevent GC before signal delivery
        self._pool.start(worker)

    def _add_pages(self) -> None:
        if not self._working_file:
            QMessageBox.warning(self, "No File", "Open a PDF first.")
            return
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF to add", "", "PDF Files (*.pdf)")
        if not path:
            return

        current = self._thumbnail_list.current_page_index()
        items = ["After current page", "Before current page", "At the beginning", "At the end"]
        choice, ok = QInputDialog.getItem(
            self, "Insert Position", "Where to insert?", items, 0, False
        )
        if not ok:
            return

        from pdf_editor.core.pages import add_pages, get_page_count

        position = None  # append
        if choice == "Before current page" and current is not None:
            position = current
        elif choice == "After current page" and current is not None:
            position = current + 1
        elif choice == "At the beginning":
            position = 0

        pages_to_add = Path(path)
        new_pages_count = get_page_count(pages_to_add)
        out = self._working_file.parent / "temp_op.pdf"

        def _done(_result):
            shutil.move(str(out), str(self._working_file))
            self._mark_unsaved()
            select = position if position is not None else self._thumbnail_list.count()
            self._reload_document(select_page=select)
            self.statusBar().showMessage(f"Added {new_pages_count} pages", 3000)

        self._run_operation(
            add_pages,
            self._working_file,
            pages_to_add,
            out,
            position=position,
            on_done=_done,
        )

    def _remove_pages(self) -> None:
        if not self._working_file:
            QMessageBox.warning(self, "No File", "Open a PDF first.")
            return
        indices = self._thumbnail_list.selected_page_indices()
        if not indices:
            QMessageBox.warning(self, "No Selection", "Select pages to remove.")
            return

        reply = QMessageBox.question(
            self,
            "Remove Pages",
            f"Remove {len(indices)} page(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        from pdf_editor.core.pages import remove_pages

        out = self._working_file.parent / "temp_op.pdf"

        def _done(_result):
            shutil.move(str(out), str(self._working_file))
            self._mark_unsaved()
            self._reload_document(select_page=max(0, min(indices) - 1))
            self.statusBar().showMessage(f"Removed {len(indices)} pages", 3000)

        self._run_operation(
            remove_pages,
            self._working_file,
            out,
            page_indices=indices,
            on_done=_done,
        )

    def _extract_pages(self) -> None:
        if not self._working_file:
            QMessageBox.warning(self, "No File", "Open a PDF first.")
            return
        indices = self._thumbnail_list.selected_page_indices()
        if not indices:
            QMessageBox.warning(self, "No Selection", "Select pages to extract.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Extracted Pages", "", "PDF Files (*.pdf)")
        if not path:
            return

        from pdf_editor.core.pages import extract_pages

        def _done(_result):
            self.statusBar().showMessage(f"Extracted {len(indices)} pages to {path}", 3000)

        self._run_operation(
            extract_pages,
            self._working_file,
            Path(path),
            page_indices=indices,
            on_done=_done,
        )

    def _on_pages_reordered(self, new_order: list[int]) -> None:
        if not self._working_file:
            return

        from pdf_editor.core.pages import reorder_pages

        out = self._working_file.parent / "temp_op.pdf"

        def _done(_result):
            shutil.move(str(out), str(self._working_file))
            self._mark_unsaved()
            self._reload_document()
            self.statusBar().showMessage("Pages reordered", 3000)

        self._run_operation(
            reorder_pages,
            self._working_file,
            out,
            new_order=new_order,
            on_done=_done,
        )

    # ── Dialogs ───────────────────────────────────────────────

    def _merge_pdfs(self) -> None:
        from pdf_editor.gui.dialogs import MergeDialog

        dialog = MergeDialog(self)
        if dialog.exec():
            result_path = dialog.result_path
            if result_path and result_path.exists():
                self._current_file = None
                self._working_file = self._create_working_copy(result_path)
                self._mark_unsaved()
                self._reload_document()
                self.statusBar().showMessage("PDFs merged", 3000)

    def _compress_pdf(self) -> None:
        if not self._working_file:
            QMessageBox.warning(self, "No File", "Open a PDF first.")
            return

        from pdf_editor.gui.dialogs import CompressDialog

        dialog = CompressDialog(self._working_file, self)
        if dialog.exec():
            compressed = dialog.result_path
            if compressed and compressed.exists():
                shutil.move(str(compressed), str(self._working_file))
                self._mark_unsaved()
                self._reload_document()
                self.statusBar().showMessage(
                    f"Compressed: {dialog.original_size_str} → {dialog.compressed_size_str}",
                    5000,
                )

    def _insert_image(self) -> None:
        if not self._working_file:
            QMessageBox.warning(self, "No File", "Open a PDF first.")
            return

        from pdf_editor.gui.dialogs import InsertImageDialog

        current_page = self._thumbnail_list.current_page_index() or 0
        page_count = self._thumbnail_list.count()
        dialog = InsertImageDialog(self._working_file, current_page, page_count, self)
        if dialog.exec():
            result = dialog.result_path
            if result and result.exists():
                shutil.move(str(result), str(self._working_file))
                self._mark_unsaved()
                self._reload_document(select_page=current_page)
                self.statusBar().showMessage("Image inserted", 3000)
