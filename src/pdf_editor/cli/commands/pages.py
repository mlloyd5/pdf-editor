from pathlib import Path
from typing import Annotated

import typer

from pdf_editor.core.pages import (
    add_pages,
    extract_pages,
    get_page_count,
    remove_pages,
    reorder_pages,
)

app = typer.Typer(help="Add, remove, reorder, and extract pages.")


@app.command()
def add(
    source: Annotated[Path, typer.Argument(help="Input PDF file")],
    pages_to_add: Annotated[Path, typer.Argument(help="PDF file whose pages will be inserted")],
    output: Annotated[Path, typer.Argument(help="Output PDF file")],
    position: Annotated[
        int | None,
        typer.Option("--position", "-p", help="0-based insert position (default: append)"),
    ] = None,
) -> None:
    """Add pages from one PDF into another."""
    add_pages(source, pages_to_add, output, position=position)
    count = get_page_count(output)
    typer.echo(f"Created {output} ({count} pages)")


@app.command()
def remove(
    source: Annotated[Path, typer.Argument(help="Input PDF file")],
    output: Annotated[Path, typer.Argument(help="Output PDF file")],
    pages: Annotated[str, typer.Option("--pages", help="Comma-separated 0-based page indices")],
) -> None:
    """Remove pages from a PDF."""
    page_indices = [int(p.strip()) for p in pages.split(",")]
    remove_pages(source, output, page_indices=page_indices)
    count = get_page_count(output)
    typer.echo(f"Created {output} ({count} pages)")


@app.command()
def reorder(
    source: Annotated[Path, typer.Argument(help="Input PDF file")],
    output: Annotated[Path, typer.Argument(help="Output PDF file")],
    order: Annotated[str, typer.Option("--order", help="Comma-separated new page order (0-based)")],
) -> None:
    """Reorder pages in a PDF."""
    new_order = [int(p.strip()) for p in order.split(",")]
    reorder_pages(source, output, new_order=new_order)
    typer.echo(f"Created {output} ({len(new_order)} pages)")


@app.command()
def extract(
    source: Annotated[Path, typer.Argument(help="Input PDF file")],
    output: Annotated[Path, typer.Argument(help="Output PDF file")],
    pages: Annotated[str, typer.Option("--pages", help="Comma-separated 0-based page indices")],
) -> None:
    """Extract specific pages into a new PDF."""
    page_indices = [int(p.strip()) for p in pages.split(",")]
    extract_pages(source, output, page_indices=page_indices)
    count = get_page_count(output)
    typer.echo(f"Created {output} ({count} pages)")
