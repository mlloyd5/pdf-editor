from __future__ import annotations

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QToolBar


def create_toolbar(window: QMainWindow) -> tuple[QToolBar, dict[str, QAction]]:
    """Create the main toolbar and return it with a dict of named actions."""
    toolbar = QToolBar("Main Toolbar")
    toolbar.setMovable(False)
    actions: dict[str, QAction] = {}

    def add_action(name: str, text: str, shortcut: str | None = None) -> QAction:
        action = QAction(text, window)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        toolbar.addAction(action)
        actions[name] = action
        return action

    add_action("open", "Open", "Ctrl+O")
    add_action("save", "Save", "Ctrl+S")
    add_action("save_as", "Save As", "Ctrl+Shift+S")
    toolbar.addSeparator()
    add_action("add_pages", "Add Pages")
    add_action("remove_pages", "Remove Pages")
    add_action("extract_pages", "Extract Pages")
    toolbar.addSeparator()
    add_action("merge", "Merge")
    add_action("compress", "Compress")
    add_action("insert_image", "Insert Image")

    return toolbar, actions
