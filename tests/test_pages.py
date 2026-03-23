import pytest
from pdf_editor.core.pages import (
    get_page_count,
    add_pages,
    remove_pages,
    reorder_pages,
    extract_pages,
)


class TestGetPageCount:
    def test_three_page_pdf(self, sample_pdf):
        assert get_page_count(sample_pdf) == 3

    def test_single_page_pdf(self, single_page_pdf):
        assert get_page_count(single_page_pdf) == 1


class TestAddPages:
    def test_append_pages(self, sample_pdf, single_page_pdf, tmp_path):
        output = tmp_path / "output.pdf"
        add_pages(sample_pdf, single_page_pdf, output)
        assert get_page_count(output) == 4

    def test_prepend_pages(self, sample_pdf, single_page_pdf, tmp_path):
        output = tmp_path / "output.pdf"
        add_pages(sample_pdf, single_page_pdf, output, position=0)
        assert get_page_count(output) == 4

    def test_insert_at_position(self, sample_pdf, single_page_pdf, tmp_path):
        output = tmp_path / "output.pdf"
        add_pages(sample_pdf, single_page_pdf, output, position=1)
        assert get_page_count(output) == 4

    def test_invalid_position(self, sample_pdf, single_page_pdf, tmp_path):
        output = tmp_path / "output.pdf"
        with pytest.raises(IndexError):
            add_pages(sample_pdf, single_page_pdf, output, position=10)


class TestRemovePages:
    def test_remove_single_page(self, sample_pdf, tmp_path):
        output = tmp_path / "output.pdf"
        remove_pages(sample_pdf, output, page_indices=[0])
        assert get_page_count(output) == 2

    def test_remove_multiple_pages(self, sample_pdf, tmp_path):
        output = tmp_path / "output.pdf"
        remove_pages(sample_pdf, output, page_indices=[0, 2])
        assert get_page_count(output) == 1

    def test_remove_all_pages_raises(self, sample_pdf, tmp_path):
        output = tmp_path / "output.pdf"
        with pytest.raises(ValueError, match="Cannot remove all pages"):
            remove_pages(sample_pdf, output, page_indices=[0, 1, 2])

    def test_invalid_index(self, sample_pdf, tmp_path):
        output = tmp_path / "output.pdf"
        with pytest.raises(IndexError):
            remove_pages(sample_pdf, output, page_indices=[5])


class TestReorderPages:
    def test_reverse_order(self, sample_pdf, tmp_path):
        output = tmp_path / "output.pdf"
        reorder_pages(sample_pdf, output, new_order=[2, 1, 0])
        assert get_page_count(output) == 3

    def test_identity_order(self, sample_pdf, tmp_path):
        output = tmp_path / "output.pdf"
        reorder_pages(sample_pdf, output, new_order=[0, 1, 2])
        assert get_page_count(output) == 3

    def test_invalid_permutation(self, sample_pdf, tmp_path):
        output = tmp_path / "output.pdf"
        with pytest.raises(ValueError, match="permutation"):
            reorder_pages(sample_pdf, output, new_order=[0, 1])

    def test_duplicate_indices(self, sample_pdf, tmp_path):
        output = tmp_path / "output.pdf"
        with pytest.raises(ValueError, match="permutation"):
            reorder_pages(sample_pdf, output, new_order=[0, 0, 1])


class TestExtractPages:
    def test_extract_single_page(self, sample_pdf, tmp_path):
        output = tmp_path / "output.pdf"
        extract_pages(sample_pdf, output, page_indices=[1])
        assert get_page_count(output) == 1

    def test_extract_multiple_pages(self, sample_pdf, tmp_path):
        output = tmp_path / "output.pdf"
        extract_pages(sample_pdf, output, page_indices=[0, 2])
        assert get_page_count(output) == 2

    def test_extract_reorders(self, sample_pdf, tmp_path):
        output = tmp_path / "output.pdf"
        extract_pages(sample_pdf, output, page_indices=[2, 0])
        assert get_page_count(output) == 2

    def test_invalid_index(self, sample_pdf, tmp_path):
        output = tmp_path / "output.pdf"
        with pytest.raises(IndexError):
            extract_pages(sample_pdf, output, page_indices=[5])
