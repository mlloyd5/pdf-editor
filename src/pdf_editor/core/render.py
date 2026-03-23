from pathlib import Path

import fitz  # PyMuPDF


def render_page_thumbnail(
    source: Path,
    page_index: int,
    *,
    max_width: int = 200,
    max_height: int = 280,
) -> bytes:
    """Render a single page as a PNG thumbnail."""
    doc = fitz.open(str(source))
    page_count = len(doc)

    if page_index < 0 or page_index >= page_count:
        doc.close()
        raise IndexError(f"Page index {page_index} out of range for {page_count}-page PDF")

    page = doc[page_index]

    # Calculate zoom to fit within max dimensions
    zoom_x = max_width / page.rect.width
    zoom_y = max_height / page.rect.height
    zoom = min(zoom_x, zoom_y)

    matrix = fitz.Matrix(zoom, zoom)
    pixmap = page.get_pixmap(matrix=matrix)
    png_bytes = pixmap.tobytes("png")

    doc.close()
    return png_bytes


def render_page_preview(
    source: Path,
    page_index: int,
    *,
    dpi: int = 150,
) -> bytes:
    """Render a single page at higher quality for preview."""
    doc = fitz.open(str(source))
    page_count = len(doc)

    if page_index < 0 or page_index >= page_count:
        doc.close()
        raise IndexError(f"Page index {page_index} out of range for {page_count}-page PDF")

    page = doc[page_index]
    zoom = dpi / 72.0  # PDF default is 72 DPI
    matrix = fitz.Matrix(zoom, zoom)
    pixmap = page.get_pixmap(matrix=matrix)
    png_bytes = pixmap.tobytes("png")

    doc.close()
    return png_bytes
