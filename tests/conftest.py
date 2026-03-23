import pikepdf
import pytest
from pathlib import Path


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a minimal 3-page PDF for testing."""
    pdf = pikepdf.Pdf.new()
    for i in range(3):
        page = pikepdf.Page(pikepdf.Dictionary(
            Type=pikepdf.Name.Page,
            MediaBox=[0, 0, 612, 792],
            Contents=pdf.make_stream(f"BT /F1 12 Tf 100 700 Td (Page {i+1}) Tj ET".encode()),
            Resources=pikepdf.Dictionary(
                Font=pikepdf.Dictionary(
                    F1=pikepdf.Dictionary(
                        Type=pikepdf.Name.Font,
                        Subtype=pikepdf.Name.Type1,
                        BaseFont=pikepdf.Name.Helvetica,
                    )
                )
            ),
        ))
        pdf.pages.append(page)
    path = tmp_path / "sample_3page.pdf"
    pdf.save(path)
    return path


@pytest.fixture
def single_page_pdf(tmp_path: Path) -> Path:
    """Create a minimal single-page PDF."""
    pdf = pikepdf.Pdf.new()
    page = pikepdf.Page(pikepdf.Dictionary(
        Type=pikepdf.Name.Page,
        MediaBox=[0, 0, 612, 792],
        Contents=pdf.make_stream(b"BT /F1 12 Tf 100 700 Td (Single Page) Tj ET"),
        Resources=pikepdf.Dictionary(
            Font=pikepdf.Dictionary(
                F1=pikepdf.Dictionary(
                    Type=pikepdf.Name.Font,
                    Subtype=pikepdf.Name.Type1,
                    BaseFont=pikepdf.Name.Helvetica,
                )
            )
        ),
    ))
    pdf.pages.append(page)
    path = tmp_path / "single_page.pdf"
    pdf.save(path)
    return path


@pytest.fixture
def sample_image(tmp_path: Path) -> Path:
    """Create a minimal PNG image for testing."""
    import struct, zlib
    # Create a 10x10 red PNG
    width, height = 10, 10
    raw_data = b""
    for _ in range(height):
        raw_data += b"\x00"  # filter byte
        raw_data += b"\xff\x00\x00" * width  # RGB red pixels

    def make_chunk(chunk_type, data):
        chunk = chunk_type + data
        return struct.pack(">I", len(data)) + chunk + struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += make_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += make_chunk(b"IDAT", zlib.compress(raw_data))
    png += make_chunk(b"IEND", b"")

    path = tmp_path / "test_image.png"
    path.write_bytes(png)
    return path
