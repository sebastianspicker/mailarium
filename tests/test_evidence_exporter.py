"""Evidence-exporter test identities backed by semantic case helpers."""

from pathlib import Path

from . import _evidence_exporter_cases as _cases


def test_html_export_contains_items():
    _cases.assert_html_export_contains_items()


def test_export_file_rejects_existing_html_output_path(tmp_path: Path) -> None:
    _cases.assert_export_file_rejects_existing_html_output_path(tmp_path)


def test_export_file_rejects_existing_csv_output_path(tmp_path: Path) -> None:
    _cases.assert_export_file_rejects_existing_csv_output_path(tmp_path)


def test_html_export_contains_quotes():
    _cases.assert_html_export_contains_quotes()


def test_html_export_respects_min_relevance():
    _cases.assert_html_export_respects_min_relevance()


def test_html_export_respects_category():
    _cases.assert_html_export_respects_category()


def test_html_export_verification_banner():
    _cases.assert_html_export_verification_banner()


def test_html_export_appendix_contains_body():
    _cases.assert_html_export_appendix_contains_body()


def test_html_export_empty():
    _cases.assert_html_export_empty()


def test_csv_export_headers():
    _cases.assert_csv_export_headers()


def test_csv_export_data_rows():
    _cases.assert_csv_export_data_rows()


def test_csv_export_respects_filters():
    _cases.assert_csv_export_respects_filters()


def test_csv_export_neutralizes_formula_values_in_every_untrusted_column(monkeypatch):
    _cases.assert_csv_export_neutralizes_formula_values_in_every_untrusted_column(monkeypatch)


def test_export_file_html(tmp_path):
    _cases.assert_export_file_html(tmp_path)


def test_export_file_csv(tmp_path):
    _cases.assert_export_file_csv(tmp_path)


def test_export_file_pdf_fallback(tmp_path):
    _cases.assert_export_file_pdf_fallback(tmp_path)


def test_export_file_creates_parent_dirs(tmp_path):
    _cases.assert_export_file_creates_parent_dirs(tmp_path)


def test_evidence_stats_unfiltered():
    _cases.assert_evidence_stats_unfiltered()


def test_evidence_stats_with_category_filter():
    _cases.assert_evidence_stats_with_category_filter()


def test_evidence_stats_with_min_relevance_filter():
    _cases.assert_evidence_stats_with_min_relevance_filter()


def test_evidence_stats_with_both_filters():
    _cases.assert_evidence_stats_with_both_filters()
