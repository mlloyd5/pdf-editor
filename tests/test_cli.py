import pikepdf
import pytest
from typer.testing import CliRunner

from pdf_editor.cli.app import app
from pdf_editor.core.pages import get_page_count

runner = CliRunner()


@pytest.fixture
def cli_pdf(tmp_path):
    """Create a 3-page PDF for CLI tests."""
    pdf = pikepdf.Pdf.new()
    for i in range(3):
        page = pikepdf.Page(
            pikepdf.Dictionary(
                Type=pikepdf.Name.Page,
                MediaBox=[0, 0, 612, 792],
                Contents=pdf.make_stream(
                    f"BT /F1 12 Tf 100 700 Td (Page {i + 1}) Tj ET".encode()
                ),
                Resources=pikepdf.Dictionary(
                    Font=pikepdf.Dictionary(
                        F1=pikepdf.Dictionary(
                            Type=pikepdf.Name.Font,
                            Subtype=pikepdf.Name.Type1,
                            BaseFont=pikepdf.Name.Helvetica,
                        )
                    )
                ),
            )
        )
        pdf.pages.append(page)
    path = tmp_path / "input.pdf"
    pdf.save(path)
    return path


@pytest.fixture
def cli_single_pdf(tmp_path):
    """Create a single-page PDF for CLI tests."""
    pdf = pikepdf.Pdf.new()
    page = pikepdf.Page(
        pikepdf.Dictionary(
            Type=pikepdf.Name.Page,
            MediaBox=[0, 0, 612, 792],
            Contents=pdf.make_stream(b"BT /F1 12 Tf 100 700 Td (Cover) Tj ET"),
            Resources=pikepdf.Dictionary(
                Font=pikepdf.Dictionary(
                    F1=pikepdf.Dictionary(
                        Type=pikepdf.Name.Font,
                        Subtype=pikepdf.Name.Type1,
                        BaseFont=pikepdf.Name.Helvetica,
                    )
                )
            ),
        )
    )
    pdf.pages.append(page)
    path = tmp_path / "cover.pdf"
    pdf.save(path)
    return path


class TestPagesAdd:
    def test_append(self, cli_pdf, cli_single_pdf, tmp_path):
        output = tmp_path / "out.pdf"
        result = runner.invoke(app, ["pages", "add", str(cli_pdf), str(cli_single_pdf), str(output)])
        assert result.exit_code == 0
        assert "4 pages" in result.stdout
        assert get_page_count(output) == 4

    def test_prepend(self, cli_pdf, cli_single_pdf, tmp_path):
        output = tmp_path / "out.pdf"
        result = runner.invoke(
            app, ["pages", "add", str(cli_pdf), str(cli_single_pdf), str(output), "--position", "0"]
        )
        assert result.exit_code == 0
        assert get_page_count(output) == 4


class TestPagesRemove:
    def test_remove(self, cli_pdf, tmp_path):
        output = tmp_path / "out.pdf"
        result = runner.invoke(app, ["pages", "remove", str(cli_pdf), str(output), "--pages", "0,2"])
        assert result.exit_code == 0
        assert "1 pages" in result.stdout
        assert get_page_count(output) == 1


class TestPagesReorder:
    def test_reorder(self, cli_pdf, tmp_path):
        output = tmp_path / "out.pdf"
        result = runner.invoke(
            app, ["pages", "reorder", str(cli_pdf), str(output), "--order", "2,0,1"]
        )
        assert result.exit_code == 0
        assert get_page_count(output) == 3


class TestPagesExtract:
    def test_extract(self, cli_pdf, tmp_path):
        output = tmp_path / "out.pdf"
        result = runner.invoke(
            app, ["pages", "extract", str(cli_pdf), str(output), "--pages", "0,2"]
        )
        assert result.exit_code == 0
        assert "2 pages" in result.stdout
        assert get_page_count(output) == 2


class TestMerge:
    def test_merge(self, cli_pdf, cli_single_pdf, tmp_path):
        output = tmp_path / "merged.pdf"
        result = runner.invoke(
            app, ["merge", str(output), str(cli_pdf), str(cli_single_pdf)]
        )
        assert result.exit_code == 0
        assert "Merged 2 files" in result.stdout
        assert get_page_count(output) == 4

    def test_merge_no_bookmarks(self, cli_pdf, cli_single_pdf, tmp_path):
        output = tmp_path / "merged.pdf"
        result = runner.invoke(
            app, ["merge", str(output), str(cli_pdf), str(cli_single_pdf), "--no-bookmarks"]
        )
        assert result.exit_code == 0
        assert get_page_count(output) == 4


class TestCompress:
    def test_compress_default(self, cli_pdf, tmp_path):
        output = tmp_path / "compressed.pdf"
        result = runner.invoke(app, ["compress", str(cli_pdf), str(output)])
        assert result.exit_code == 0
        assert "reduction" in result.stdout

    def test_compress_high(self, cli_pdf, tmp_path):
        output = tmp_path / "compressed.pdf"
        result = runner.invoke(
            app, ["compress", str(cli_pdf), str(output), "--level", "high"]
        )
        assert result.exit_code == 0


class TestImageAdd:
    def test_add_image(self, cli_pdf, sample_image, tmp_path):
        output = tmp_path / "with_image.pdf"
        result = runner.invoke(
            app, ["image", "add", str(cli_pdf), str(sample_image), str(output)]
        )
        assert result.exit_code == 0
        assert "Inserted" in result.stdout

    def test_add_image_positioned(self, cli_pdf, sample_image, tmp_path):
        output = tmp_path / "with_image.pdf"
        result = runner.invoke(
            app,
            [
                "image", "add", str(cli_pdf), str(sample_image), str(output),
                "--position", "top-left", "--page", "1",
            ],
        )
        assert result.exit_code == 0


class TestBulkAddCover:
    def test_add_cover_to_directory(self, cli_pdf, cli_single_pdf, tmp_path):
        # Set up a directory with PDFs
        pdf_dir = tmp_path / "pdfs"
        pdf_dir.mkdir()
        import shutil

        shutil.copy(cli_pdf, pdf_dir / "doc1.pdf")
        shutil.copy(cli_pdf, pdf_dir / "doc2.pdf")

        output_dir = tmp_path / "output"
        result = runner.invoke(
            app,
            ["bulk", "add-cover", str(pdf_dir), str(cli_single_pdf), "--output-dir", str(output_dir)],
        )
        assert result.exit_code == 0
        assert "Processed 2 files" in result.stdout
        assert (output_dir / "doc1_with_cover.pdf").exists()
        assert (output_dir / "doc2_with_cover.pdf").exists()
        assert get_page_count(output_dir / "doc1_with_cover.pdf") == 4

    def test_no_pdfs_found(self, cli_single_pdf, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        result = runner.invoke(app, ["bulk", "add-cover", str(empty_dir), str(cli_single_pdf)])
        assert result.exit_code == 0
        assert "No PDF files found" in result.stdout
