# Lessons Learned

## PySide6 QRunnable Worker GC Bug
**Pattern**: When using QRunnable workers with QThreadPool and signals, the Python garbage collector
can destroy the Worker object before the queued signal is delivered to the main thread.
**Fix**: Set `worker.setAutoDelete(False)` and keep a Python reference to the worker until the
signal callback fires. Release the reference in the callback.
