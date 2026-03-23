import pytest
from pdf_editor.core.merge import merge_pdfs, split_pdf
from pdf_editor.core.pages import get_page_count


class TestMergePdfs:
    def test_merge_two_files(self, sample_pdf, single_page_pdf, tmp_path):
        output = tmp_path / "merged.pdf"
        merge_pdfs([sample_pdf, single_page_pdf], output)
        assert get_page_count(output) == 4

    def test_merge_same_file_twice(self, sample_pdf, tmp_path):
        output = tmp_path / "merged.pdf"
        merge_pdfs([sample_pdf, sample_pdf], output)
        assert get_page_count(output) == 6

    def test_merge_single_file(self, sample_pdf, tmp_path):
        output = tmp_path / "merged.pdf"
        merge_pdfs([sample_pdf], output)
        assert get_page_count(output) == 3

    def test_merge_empty_list(self, tmp_path):
        output = tmp_path / "merged.pdf"
        with pytest.raises(ValueError, match="empty"):
            merge_pdfs([], output)

    def test_merge_missing_file(self, tmp_path):
        output = tmp_path / "merged.pdf"
        with pytest.raises(FileNotFoundError):
            merge_pdfs([tmp_path / "nonexistent.pdf"], output)

    def test_merge_without_bookmarks(self, sample_pdf, single_page_pdf, tmp_path):
        output = tmp_path / "merged.pdf"
        merge_pdfs([sample_pdf, single_page_pdf], output, bookmarks=False)
        assert get_page_count(output) == 4


class TestSplitPdf:
    def test_split_one_page_each(self, sample_pdf, tmp_path):
        output_dir = tmp_path / "split"
        results = split_pdf(sample_pdf, output_dir)
        assert len(results) == 3
        for path in results:
            assert path.exists()
            assert get_page_count(path) == 1

    def test_split_two_pages_each(self, sample_pdf, tmp_path):
        output_dir = tmp_path / "split"
        results = split_pdf(sample_pdf, output_dir, pages_per_split=2)
        assert len(results) == 2
        assert get_page_count(results[0]) == 2
        assert get_page_count(results[1]) == 1  # remainder

    def test_split_all_pages(self, sample_pdf, tmp_path):
        output_dir = tmp_path / "split"
        results = split_pdf(sample_pdf, output_dir, pages_per_split=3)
        assert len(results) == 1
        assert get_page_count(results[0]) == 3

    def test_split_invalid_pages_per_split(self, sample_pdf, tmp_path):
        with pytest.raises(ValueError, match="pages_per_split"):
            split_pdf(sample_pdf, tmp_path / "split", pages_per_split=0)

    def test_split_creates_output_dir(self, sample_pdf, tmp_path):
        output_dir = tmp_path / "nested" / "split"
        results = split_pdf(sample_pdf, output_dir)
        assert output_dir.exists()
        assert len(results) == 3

    def test_split_custom_pattern(self, sample_pdf, tmp_path):
        output_dir = tmp_path / "split"
        results = split_pdf(
            sample_pdf, output_dir, filename_pattern="{stem}-{n:02d}.pdf"
        )
        assert results[0].name == "sample_3page-01.pdf"
