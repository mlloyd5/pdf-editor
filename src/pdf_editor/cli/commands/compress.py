from pathlib import Path
from typing import Annotated

import typer

from pdf_editor.core.optimize import CompressionLevel, compress_pdf


def compress_command(
    source: Annotated[Path, typer.Argument(help="Input PDF file")],
    output: Annotated[Path, typer.Argument(help="Output PDF file")],
    level: Annotated[
        str, typer.Option("--level", "-l", help="Compression level: low, medium, high")
    ] = "medium",
    image_dpi: Annotated[
        int, typer.Option("--image-dpi", help="Target DPI for images (only used with --level high)")
    ] = 150,
) -> None:
    """Compress a PDF to reduce file size."""
    comp_level = CompressionLevel(level)
    _, orig_size, comp_size = compress_pdf(source, output, level=comp_level, image_dpi=image_dpi)
    reduction = (1 - comp_size / orig_size) * 100 if orig_size > 0 else 0
    typer.echo(
        f"Compressed {source} ({_fmt_size(orig_size)}) -> {output} ({_fmt_size(comp_size)}) "
        f"[{reduction:.1f}% reduction]"
    )


def _fmt_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
