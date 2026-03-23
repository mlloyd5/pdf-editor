import pytest
from pdf_editor.core.optimize import compress_pdf, get_file_stats, CompressionLevel


class TestCompressPdf:
    def test_compress_low(self, sample_pdf, tmp_path):
        output = tmp_path / "compressed.pdf"
        result_path, orig_size, comp_size = compress_pdf(
            sample_pdf, output, level=CompressionLevel.LOW
        )
        assert result_path == output
        assert output.exists()
        assert orig_size > 0
        assert comp_size > 0

    def test_compress_medium(self, sample_pdf, tmp_path):
        output = tmp_path / "compressed.pdf"
        result_path, orig_size, comp_size = compress_pdf(
            sample_pdf, output, level=CompressionLevel.MEDIUM
        )
        assert result_path == output
        assert output.exists()

    def test_compress_high(self, sample_pdf, tmp_path):
        output = tmp_path / "compressed.pdf"
        result_path, orig_size, comp_size = compress_pdf(
            sample_pdf, output, level=CompressionLevel.HIGH
        )
        assert result_path == output
        assert output.exists()

    def test_compress_default_level(self, sample_pdf, tmp_path):
        output = tmp_path / "compressed.pdf"
        compress_pdf(sample_pdf, output)
        assert output.exists()


class TestGetFileStats:
    def test_basic_stats(self, sample_pdf):
        stats = get_file_stats(sample_pdf)
        assert stats["page_count"] == 3
        assert stats["file_size_bytes"] > 0
        assert isinstance(stats["has_images"], bool)

    def test_single_page_stats(self, single_page_pdf):
        stats = get_file_stats(single_page_pdf)
        assert stats["page_count"] == 1
