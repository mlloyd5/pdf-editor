from enum import Enum
from pathlib import Path

import pikepdf


class CompressionLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def compress_pdf(
    source: Path,
    output: Path,
    *,
    level: CompressionLevel = CompressionLevel.MEDIUM,
    image_dpi: int = 150,
) -> tuple[Path, int, int]:
    """Compress a PDF to reduce file size."""
    original_size = source.stat().st_size

    if level == CompressionLevel.HIGH:
        _compress_high(source, output, image_dpi)
    else:
        _compress_pikepdf(source, output, level)

    compressed_size = output.stat().st_size
    return output, original_size, compressed_size


def _compress_pikepdf(source: Path, output: Path, level: CompressionLevel) -> None:
    with pikepdf.Pdf.open(source) as pdf:
        save_kwargs: dict = {}
        if level == CompressionLevel.LOW:
            save_kwargs["linearize"] = True
            save_kwargs["object_stream_mode"] = pikepdf.ObjectStreamMode.generate
        elif level == CompressionLevel.MEDIUM:
            save_kwargs["linearize"] = True
            save_kwargs["object_stream_mode"] = pikepdf.ObjectStreamMode.generate
            save_kwargs["compress_streams"] = True
            save_kwargs["recompress_flate"] = True
            pdf.remove_unreferenced_resources()
        pdf.save(output, **save_kwargs)


def _compress_high(source: Path, output: Path, target_dpi: int) -> None:
    import fitz

    doc = fitz.open(str(source))

    for page in doc:
        image_list = page.get_images(full=True)
        for img_info in image_list:
            xref = img_info[0]
            try:
                doc.extract_image(xref)
            except Exception:
                continue

    doc.save(str(output), garbage=4, deflate=True, clean=True)
    doc.close()


def get_file_stats(source: Path) -> dict:
    """Return basic stats about the PDF."""
    import fitz

    stats: dict = {
        "file_size_bytes": source.stat().st_size,
    }

    with pikepdf.Pdf.open(source) as pdf:
        stats["page_count"] = len(pdf.pages)

    doc = fitz.open(str(source))
    has_images = False
    for page in doc:
        if page.get_images():
            has_images = True
            break
    doc.close()
    stats["has_images"] = has_images

    return stats
