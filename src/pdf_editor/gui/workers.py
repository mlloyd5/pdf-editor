from __future__ import annotations

import traceback
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class WorkerSignals(QObject):
    """Signals for Worker threads."""

    finished = Signal(object)
    error = Signal(str)
    progress = Signal(int)


class Worker(QRunnable):
    """Generic worker that runs a callable on QThreadPool."""

    def __init__(self, fn: Any, *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.setAutoDelete(True)

    @Slot()
    def run(self) -> None:
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception:
            self.signals.error.emit(traceback.format_exc())
