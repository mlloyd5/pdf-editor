from pathlib import Path

import pikepdf


def get_page_count(source: Path) -> int:
    """Return the number of pages in the PDF."""
    with pikepdf.Pdf.open(source) as pdf:
        return len(pdf.pages)


def add_pages(
    source: Path,
    pages_to_add: Path,
    output: Path,
    *,
    position: int | None = None,
) -> Path:
    """Insert all pages from pages_to_add into source at the given position.

    position=None appends at end. position=0 prepends.
    """
    with pikepdf.Pdf.open(source) as pdf, pikepdf.Pdf.open(pages_to_add) as donor:
        if position is None:
            position = len(pdf.pages)
        if position < 0 or position > len(pdf.pages):
            raise IndexError(f"Position {position} out of range for {len(pdf.pages)}-page PDF")
        for i, page in enumerate(donor.pages):
            pdf.pages.insert(position + i, page)
        pdf.save(output)
    return output


def remove_pages(
    source: Path,
    output: Path,
    *,
    page_indices: list[int],
) -> Path:
    """Remove pages at the given 0-based indices from the PDF."""
    with pikepdf.Pdf.open(source) as pdf:
        total = len(pdf.pages)
        for idx in page_indices:
            if idx < 0 or idx >= total:
                raise IndexError(f"Page index {idx} out of range for {total}-page PDF")
        # Remove in reverse order to preserve indices
        for idx in sorted(set(page_indices), reverse=True):
            del pdf.pages[idx]
        if len(pdf.pages) == 0:
            raise ValueError("Cannot remove all pages from a PDF")
        pdf.save(output)
    return output


def reorder_pages(
    source: Path,
    output: Path,
    *,
    new_order: list[int],
) -> Path:
    """Reorder pages according to new_order (a permutation of [0..n-1])."""
    with pikepdf.Pdf.open(source) as pdf:
        total = len(pdf.pages)
        if sorted(new_order) != list(range(total)):
            raise ValueError(
                f"new_order must be a permutation of [0..{total - 1}], got {new_order}"
            )
        # Copy page references, then rebuild
        original_pages = list(pdf.pages)
        while len(pdf.pages) > 0:
            del pdf.pages[-1]
        for idx in new_order:
            pdf.pages.append(original_pages[idx])
        pdf.save(output)
    return output


def extract_pages(
    source: Path,
    output: Path,
    *,
    page_indices: list[int],
) -> Path:
    """Extract specific pages into a new PDF."""
    with pikepdf.Pdf.open(source) as pdf:
        total = len(pdf.pages)
        for idx in page_indices:
            if idx < 0 or idx >= total:
                raise IndexError(f"Page index {idx} out of range for {total}-page PDF")
        new_pdf = pikepdf.Pdf.new()
        for idx in page_indices:
            new_pdf.pages.append(pdf.pages[idx])
        new_pdf.save(output)
    return output
