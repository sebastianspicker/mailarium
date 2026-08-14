"""Page-specific Streamlit and database setup helpers for web application tests."""

from __future__ import annotations

from contextlib import contextmanager
from unittest.mock import MagicMock, patch


def _setup_evidence_st(mock_st, *, selectbox_side_effect=None, slider_val=1, text_input_val="", button_val=False):
    """Common setup for evidence page tests."""
    mock_st.columns.side_effect = lambda n: [MagicMock() for _ in range(n)] if isinstance(n, int) else [MagicMock() for _ in n]
    mock_st.selectbox.side_effect = selectbox_side_effect or ["All", "html", 1]
    mock_st.slider.return_value = slider_val
    mock_st.text_input.return_value = text_input_val
    mock_st.button.return_value = button_val
    mock_st.expander.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)


def _setup_dashboard_page(mock_st, mock_db_safe, *, contacts=None):
    """Supply the stable dashboard controls and a database double."""
    db = MagicMock()
    db.top_contacts.return_value = [] if contacts is None else contacts
    mock_db_safe.return_value = db
    mock_st.selectbox.return_value = "month"
    mock_st.text_input.return_value = ""
    return db


@contextmanager
def _patched_dashboard_chart_data(*, volume_data=None, heatmap_data=None, response_time_data=None):
    """Patch dashboard chart adapters with explicit test-specific data."""
    with (
        patch("mailarium.dashboard_charts.prepare_volume_chart_data") as volume,
        patch("mailarium.dashboard_charts.prepare_heatmap_data") as heatmap,
        patch("mailarium.dashboard_charts.prepare_response_times_data") as response_times,
        patch("mailarium.temporal_analysis.TemporalAnalyzer"),
    ):
        volume.return_value = [] if volume_data is None else volume_data
        heatmap.return_value = [[0] * 24 for _ in range(7)] if heatmap_data is None else heatmap_data
        response_times.return_value = [] if response_time_data is None else response_time_data
        yield


def _setup_evidence_page(
    mock_st,
    mock_db_safe,
    *,
    stats,
    categories,
    list_response=None,
    search_response=None,
    streamlit_options=None,
):
    """Provide only the evidence repository responses needed by one test."""
    db = MagicMock()
    db.evidence_stats.return_value = stats
    db.evidence_categories.return_value = categories
    if list_response is not None:
        db.list_evidence.return_value = list_response
    if search_response is not None:
        db.search_evidence.return_value = search_response
    mock_db_safe.return_value = db
    _setup_evidence_st(mock_st, **({} if streamlit_options is None else streamlit_options))
    return db


def _setup_verified_evidence_page(mock_st, mock_db_safe, *, list_response, streamlit_options=None):
    """Configure the common single verified harassment-evidence scenario."""
    return _setup_evidence_page(
        mock_st,
        mock_db_safe,
        stats={"total": 1, "verified": 1, "unverified": 0},
        categories=[{"category": "harassment", "count": 1}],
        list_response=list_response,
        streamlit_options=streamlit_options,
    )


__all__ = (
    "_patched_dashboard_chart_data",
    "_setup_dashboard_page",
    "_setup_evidence_page",
    "_setup_evidence_st",
    "_setup_verified_evidence_page",
)
