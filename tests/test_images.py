import pytest
from pdf_editor.core.images import insert_image, ImagePosition
from pdf_editor.core.pages import get_page_count


class TestInsertImage:
    def test_insert_center(self, sample_pdf, sample_image, tmp_path):
        output = tmp_path / "output.pdf"
        insert_image(sample_pdf, sample_image, output)
        assert output.exists()
        assert get_page_count(output) == 3

    def test_insert_top_left(self, sample_pdf, sample_image, tmp_path):
        output = tmp_path / "output.pdf"
        insert_image(sample_pdf, sample_image, output, position=ImagePosition.TOP_LEFT)
        assert output.exists()

    def test_insert_bottom_right(self, sample_pdf, sample_image, tmp_path):
        output = tmp_path / "output.pdf"
        insert_image(sample_pdf, sample_image, output, position=ImagePosition.BOTTOM_RIGHT)
        assert output.exists()

    def test_insert_custom_position(self, sample_pdf, sample_image, tmp_path):
        output = tmp_path / "output.pdf"
        insert_image(
            sample_pdf, sample_image, output,
            position=ImagePosition.CUSTOM, x=100, y=200,
        )
        assert output.exists()

    def test_insert_custom_missing_coords(self, sample_pdf, sample_image, tmp_path):
        output = tmp_path / "output.pdf"
        with pytest.raises(ValueError, match="x and y"):
            insert_image(
                sample_pdf, sample_image, output, position=ImagePosition.CUSTOM
            )

    def test_insert_scaled(self, sample_pdf, sample_image, tmp_path):
        output = tmp_path / "output.pdf"
        insert_image(sample_pdf, sample_image, output, scale=2.0)
        assert output.exists()

    def test_insert_on_specific_page(self, sample_pdf, sample_image, tmp_path):
        output = tmp_path / "output.pdf"
        insert_image(sample_pdf, sample_image, output, page_index=2)
        assert output.exists()

    def test_invalid_page_index(self, sample_pdf, sample_image, tmp_path):
        output = tmp_path / "output.pdf"
        with pytest.raises(IndexError):
            insert_image(sample_pdf, sample_image, output, page_index=10)

    def test_missing_source(self, sample_image, tmp_path):
        with pytest.raises(FileNotFoundError):
            insert_image(tmp_path / "nope.pdf", sample_image, tmp_path / "out.pdf")

    def test_missing_image(self, sample_pdf, tmp_path):
        with pytest.raises(FileNotFoundError):
            insert_image(sample_pdf, tmp_path / "nope.png", tmp_path / "out.pdf")
