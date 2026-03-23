from pathlib import Path
from typing import Annotated

import typer

from pdf_editor.core.images import ImagePosition, insert_image

app = typer.Typer(help="Insert images into PDF pages.")


@app.command()
def add(
    source: Annotated[Path, typer.Argument(help="Input PDF file")],
    image: Annotated[Path, typer.Argument(help="Image file to insert (PNG, JPEG, etc.)")],
    output: Annotated[Path, typer.Argument(help="Output PDF file")],
    page: Annotated[int, typer.Option("--page", help="0-based page index")] = 0,
    position: Annotated[
        str, typer.Option("--position", help="center, top-left, top-right, etc.")
    ] = "center",
    x: Annotated[float | None, typer.Option("--x", help="X coordinate in points (custom)")] = None,
    y: Annotated[float | None, typer.Option("--y", help="Y coordinate in points (custom)")] = None,
    scale: Annotated[float, typer.Option("--scale", help="Scale factor (1.0 = original)")] = 1.0,
    opacity: Annotated[float, typer.Option("--opacity", help="Opacity (0.0-1.0)")] = 1.0,
) -> None:
    """Add an image to a PDF page."""
    pos = ImagePosition(position)
    insert_image(
        source,
        image,
        output,
        page_index=page,
        position=pos,
        x=x,
        y=y,
        scale=scale,
        opacity=opacity,
    )
    typer.echo(f"Inserted {image.name} onto page {page} of {output}")
