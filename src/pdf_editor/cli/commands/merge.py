from pathlib import Path
from typing import Annotated

import typer

from pdf_editor.core.merge import merge_pdfs
from pdf_editor.core.pages import get_page_count


def merge_command(
    output: Annotated[Path, typer.Argument(help="Output PDF file")],
    inputs: Annotated[list[Path], typer.Argument(help="Input PDF files to merge")],
    no_bookmarks: Annotated[
        bool, typer.Option("--no-bookmarks", help="Disable bookmark creation at file boundaries")
    ] = False,
) -> None:
    """Merge multiple PDFs into one."""
    merge_pdfs(inputs, output, bookmarks=not no_bookmarks)
    count = get_page_count(output)
    typer.echo(f"Merged {len(inputs)} files into {output} ({count} pages)")
