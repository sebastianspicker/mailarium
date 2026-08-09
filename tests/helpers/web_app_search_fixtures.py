"""Search-page Streamlit setup helpers for web application tests."""

from __future__ import annotations

from unittest.mock import MagicMock


def _columns_side_effect(n, **_kwargs):
    """Return a function that produces exactly N MagicMock objects."""
    if isinstance(n, int):
        return [MagicMock() for _ in range(n)]
    if isinstance(n, list):
        return [MagicMock() for _ in n]
    return [MagicMock() for _ in range(3)]


def _setup_render_results_st(mock_st):
    """Configure the containers used by result-card renderers."""
    mock_st.expander.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.columns.side_effect = _columns_side_effect


def _setup_main_search_st(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    mock_st,
    *,
    search_clicked=False,
    text_inputs=None,
    number_inputs=None,
    selectbox_inputs=None,
    slider_inputs=None,
    date_inputs=None,
    checkbox_inputs=None,
):
    """Common setup for main() search page tests."""
    mock_st.sidebar.radio.return_value = "Search"
    mock_st.sidebar.text_input.return_value = ""
    mock_st.session_state = {}
    mock_st.form.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.columns.side_effect = _columns_side_effect
    mock_st.expander.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

    mock_st.text_input.side_effect = text_inputs or ["", "", "", "", "", "", "", ""]
    mock_st.number_input.side_effect = number_inputs or [10, 0]
    mock_st.selectbox.side_effect = [*(selectbox_inputs or ["Relevance", "Any"]), "General"]
    mock_st.slider.side_effect = slider_inputs or [0.0, 1200]
    mock_st.date_input.side_effect = date_inputs or [None, None]
    mock_st.checkbox.side_effect = checkbox_inputs or [False, False, False, False]
    mock_st.form_submit_button.return_value = search_clicked
    mock_st.button.return_value = False


def _setup_main_session_results(
    mock_st,
    *,
    results,
    query="query",
    filters=None,
    sort="relevance",
    page=0,
    thread_id=None,
):
    """Prepare the idle search form around a saved result-set or thread view."""
    _setup_main_search_st(mock_st)
    mock_st.text_input.side_effect = None
    mock_st.text_input.return_value = ""
    mock_st.number_input.side_effect = None
    mock_st.number_input.return_value = 10
    mock_st.selectbox.side_effect = None
    mock_st.selectbox.return_value = "Relevance"
    mock_st.date_input.side_effect = None
    mock_st.date_input.return_value = None
    mock_st.checkbox.side_effect = None
    mock_st.checkbox.return_value = False
    mock_st.session_state = {
        "web_results": results,
        "web_query": query,
        "web_filters": {} if filters is None else filters,
        "web_sort": sort,
        "web_page": page,
        "web_thread_id": thread_id,
    }


__all__ = (
    "_columns_side_effect",
    "_setup_main_search_st",
    "_setup_main_session_results",
    "_setup_render_results_st",
)
