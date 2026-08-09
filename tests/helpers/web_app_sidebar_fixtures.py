"""Sidebar-oriented Streamlit doubles for web application tests."""

from __future__ import annotations

from unittest.mock import MagicMock


def _sidebar_retriever(mock_st, *, stats, senders):
    """Configure the sidebar containers and return a retriever with supplied data."""
    mock_st.sidebar.expander.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.sidebar.expander.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.sidebar.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
    retriever = MagicMock()
    retriever.stats.return_value = stats
    retriever.list_senders.return_value = senders
    return retriever


__all__ = ("_sidebar_retriever",)
