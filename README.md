# PDF Editor

A free and open source PDF utility for Linux, macOS, and Windows.

## Features

- Add, remove, and reorder pages
- Insert images into PDF pages
- Compress/optimize PDFs to reduce file size
- Merge and split PDFs
- CLI for bulk operations (e.g., add a cover sheet to every PDF in a directory)

## Installation

```bash
uv sync --extra dev
```

## Usage

### CLI

```bash
pdf-editor --help
pdf-editor pages add input.pdf extra_pages.pdf output.pdf
pdf-editor compress input.pdf output.pdf --level medium
pdf-editor merge output.pdf file1.pdf file2.pdf file3.pdf
pdf-editor bulk add-cover ./invoices/ cover.pdf
```

### GUI (coming soon)

```bash
pdf-editor-gui
```

## License

MIT
