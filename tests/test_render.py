import pytest
from pdf_editor.core.render import render_page_thumbnail, render_page_preview


class TestRenderPageThumbnail:
    def test_renders_png(self, sample_pdf):
        data = render_page_thumbnail(sample_pdf, 0)
        assert isinstance(data, bytes)
        assert len(data) > 0
        assert data[:8] == b"\x89PNG\r\n\x1a\n"  # PNG magic bytes

    def test_renders_each_page(self, sample_pdf):
        for i in range(3):
            data = render_page_thumbnail(sample_pdf, i)
            assert len(data) > 0

    def test_invalid_page_index(self, sample_pdf):
        with pytest.raises(IndexError):
            render_page_thumbnail(sample_pdf, 10)

    def test_custom_dimensions(self, sample_pdf):
        data = render_page_thumbnail(sample_pdf, 0, max_width=100, max_height=140)
        assert len(data) > 0


class TestRenderPagePreview:
    def test_renders_png(self, sample_pdf):
        data = render_page_preview(sample_pdf, 0)
        assert isinstance(data, bytes)
        assert data[:8] == b"\x89PNG\r\n\x1a\n"

    def test_higher_dpi_larger(self, sample_pdf):
        low = render_page_preview(sample_pdf, 0, dpi=72)
        high = render_page_preview(sample_pdf, 0, dpi=300)
        assert len(high) > len(low)

    def test_invalid_page_index(self, sample_pdf):
        with pytest.raises(IndexError):
            render_page_preview(sample_pdf, 10)
