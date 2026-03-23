from enum import Enum
from pathlib import Path

import fitz  # PyMuPDF


class ImagePosition(Enum):
    CENTER = "center"
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
    CUSTOM = "custom"


def insert_image(
    source: Path,
    image: Path,
    output: Path,
    *,
    page_index: int = 0,
    position: ImagePosition = ImagePosition.CENTER,
    x: float | None = None,
    y: float | None = None,
    scale: float = 1.0,
    opacity: float = 1.0,
) -> Path:
    """Insert an image onto a specific page of the PDF."""
    if not source.exists():
        raise FileNotFoundError(f"Source PDF not found: {source}")
    if not image.exists():
        raise FileNotFoundError(f"Image not found: {image}")
    if position == ImagePosition.CUSTOM and (x is None or y is None):
        raise ValueError("x and y are required when position=CUSTOM")

    doc = fitz.open(str(source))
    page_count = len(doc)

    if page_index < 0 or page_index >= page_count:
        doc.close()
        raise IndexError(f"Page index {page_index} out of range for {page_count}-page PDF")

    page = doc[page_index]
    page_rect = page.rect

    # Get image dimensions
    img = fitz.Pixmap(str(image))
    img_width = img.width * scale
    img_height = img.height * scale
    img = None  # release pixmap

    # Calculate position
    rect = _calculate_rect(page_rect, img_width, img_height, position, x, y)

    # Insert the image
    page.insert_image(rect, filename=str(image), overlay=True)

    doc.save(str(output), garbage=4, deflate=True)
    doc.close()
    return output


def _calculate_rect(
    page_rect: fitz.Rect,
    img_width: float,
    img_height: float,
    position: ImagePosition,
    x: float | None,
    y: float | None,
) -> fitz.Rect:
    """Calculate the fitz.Rect for image placement."""
    pw, ph = page_rect.width, page_rect.height

    if position == ImagePosition.CENTER:
        cx = (pw - img_width) / 2
        cy = (ph - img_height) / 2
    elif position == ImagePosition.TOP_LEFT:
        cx, cy = 0, 0
    elif position == ImagePosition.TOP_RIGHT:
        cx = pw - img_width
        cy = 0
    elif position == ImagePosition.BOTTOM_LEFT:
        cx = 0
        cy = ph - img_height
    elif position == ImagePosition.BOTTOM_RIGHT:
        cx = pw - img_width
        cy = ph - img_height
    elif position == ImagePosition.CUSTOM:
        cx, cy = x, y
    else:
        cx = (pw - img_width) / 2
        cy = (ph - img_height) / 2

    return fitz.Rect(cx, cy, cx + img_width, cy + img_height)
