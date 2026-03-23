from pathlib import Path
from typing import Annotated

import typer
from rich.progress import Progress

from pdf_editor.core.pages import add_pages

app = typer.Typer(help="Bulk operations on directories of PDFs.")


@app.command()
def add_cover(
    directory: Annotated[Path, typer.Argument(help="Directory containing PDF files")],
    cover: Annotated[Path, typer.Argument(help="Cover page PDF to prepend")],
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", "-o", help="Output directory (default: ./output)"),
    ] = None,
    recursive: Annotated[
        bool, typer.Option("--recursive", "-r", help="Search for PDFs recursively")
    ] = False,
    suffix: Annotated[
        str, typer.Option("--suffix", help="Suffix to add before .pdf extension")
    ] = "_with_cover",
) -> None:
    """Add a cover page to every PDF in a directory."""
    if not directory.is_dir():
        typer.echo(f"Error: {directory} is not a directory", err=True)
        raise typer.Exit(1)
    if not cover.exists():
        typer.echo(f"Error: Cover file {cover} not found", err=True)
        raise typer.Exit(1)

    if output_dir is None:
        output_dir = directory / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    pattern = "**/*.pdf" if recursive else "*.pdf"
    pdf_files = sorted(directory.glob(pattern))
    # Exclude files in the output directory
    pdf_files = [f for f in pdf_files if not f.is_relative_to(output_dir)]

    if not pdf_files:
        typer.echo("No PDF files found")
        raise typer.Exit(0)

    with Progress() as progress:
        task = progress.add_task("Adding covers...", total=len(pdf_files))
        for pdf_file in pdf_files:
            out_name = f"{pdf_file.stem}{suffix}.pdf"
            out_path = output_dir / out_name
            add_pages(pdf_file, cover, out_path, position=0)
            progress.update(task, advance=1)

    typer.echo(f"Processed {len(pdf_files)} files -> {output_dir}")
