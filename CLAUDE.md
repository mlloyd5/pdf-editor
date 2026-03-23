# PDF Editor

A free and open source PDF utility for Linux, macOS, and Windows.

## Tech Stack

- **Language**: Python 3.10+
- **GUI**: PySide6 (Qt 6)
- **PDF Core**: pikepdf (page operations, optimization) + PyMuPDF (rendering, image insertion)
- **CLI**: typer
- **Testing**: pytest
- **Packaging**: PyInstaller / Nuitka for standalone binaries

## Project Structure

```
pdf-editor/
├── src/
│   └── pdf_editor/
│       ├── __init__.py
│       ├── core/           # PDF manipulation logic (no GUI deps)
│       │   ├── __init__.py
│       │   ├── pages.py    # Add, remove, reorder pages
│       │   ├── images.py   # Insert images into pages
│       │   ├── optimize.py # Compress/shrink PDF file size
│       │   └── merge.py    # Merge/split PDFs
│       ├── gui/            # PySide6 UI
│       │   ├── __init__.py
│       │   ├── app.py      # Application entry point
│       │   ├── main_window.py
│       │   └── widgets/    # Custom widgets (thumbnail view, etc.)
│       └── cli/            # typer CLI
│           ├── __init__.py
│           └── commands.py
├── tests/
│   ├── conftest.py
│   ├── test_pages.py
│   ├── test_images.py
│   ├── test_optimize.py
│   └── test_merge.py
├── pyproject.toml
└── CLAUDE.md
```

## Architecture Principles

- **Core is GUI-independent**: All PDF logic lives in `core/` with no Qt imports. Both GUI and CLI consume the same core API.
- **No unnecessary abstractions**: Keep it simple. Direct functions over class hierarchies.
- **Fail fast**: Validate inputs early, raise clear exceptions.

## Development

```bash
# Install in dev mode
pip install -e ".[dev]"

# Run GUI
python -m pdf_editor.gui

# Run CLI
python -m pdf_editor.cli --help

# Run tests
pytest
```

## Commands

- `pytest` — run all tests
- `pytest -x` — stop on first failure
- `ruff check src/` — lint
- `ruff format src/` — format

## Style

- Follow ruff defaults (based on pycodestyle + pyflakes)
- Type hints on public function signatures
- Docstrings only on non-obvious public APIs
