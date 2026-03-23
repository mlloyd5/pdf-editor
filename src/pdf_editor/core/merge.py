from pathlib import Path

import pikepdf


def merge_pdfs(
    inputs: list[Path],
    output: Path,
    *,
    bookmarks: bool = True,
) -> Path:
    """Merge multiple PDFs into one.

    Args:
        inputs: List of PDF file paths, merged in order.
        output: Path to write the merged result.
        bookmarks: If True, add a bookmark at each file boundary.
    """
    if not inputs:
        raise ValueError("inputs must not be empty")
    for path in inputs:
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")

    merged = pikepdf.Pdf.new()
    bookmark_entries: list[tuple[str, int]] = []
    page_count = 0

    for input_path in inputs:
        with pikepdf.Pdf.open(input_path) as src:
            if bookmarks:
                bookmark_entries.append((input_path.stem, page_count))
            merged.pages.extend(src.pages)
            page_count += len(src.pages)

    if bookmark_entries:
        with merged.open_outline() as outline:
            for title, page_num in bookmark_entries:
                outline.root.append(pikepdf.OutlineItem(title, page_num))

    merged.save(output)
    return output


def split_pdf(
    source: Path,
    output_dir: Path,
    *,
    pages_per_split: int = 1,
    filename_pattern: str = "{stem}_part{n:03d}.pdf",
) -> list[Path]:
    """Split a PDF into multiple files.

    Args:
        source: Path to the input PDF.
        output_dir: Directory to write split files into.
        pages_per_split: Number of pages per output file.
        filename_pattern: Pattern for output filenames.
    """
    if pages_per_split < 1:
        raise ValueError("pages_per_split must be >= 1")

    output_dir.mkdir(parents=True, exist_ok=True)
    stem = source.stem
    outputs = []

    with pikepdf.Pdf.open(source) as pdf:
        total = len(pdf.pages)
        part = 1
        for start in range(0, total, pages_per_split):
            end = min(start + pages_per_split, total)
            new_pdf = pikepdf.Pdf.new()
            for i in range(start, end):
                new_pdf.pages.append(pdf.pages[i])

            filename = filename_pattern.format(stem=stem, n=part)
            out_path = output_dir / filename
            new_pdf.save(out_path)
            outputs.append(out_path)
            part += 1

    return outputs
