"""Compatibility facade for split web application test fixtures."""

from contextlib import contextmanager
from unittest.mock import MagicMock, patch

from mailarium.retriever import SearchResult

from .web_app_pages_fixtures import (
    _patched_dashboard_chart_data,
    _setup_dashboard_page,
    _setup_evidence_page,
    _setup_evidence_st,
    _setup_verified_evidence_page,
)
from .web_app_result_fixtures import _result
from .web_app_search_fixtures import (
    _columns_side_effect,
    _setup_main_search_st,
    _setup_main_session_results,
    _setup_render_results_st,
)
from .web_app_sidebar_fixtures import _sidebar_retriever

__all__ = (
    "MagicMock",
    "SearchResult",
    "_columns_side_effect",
    "_patched_dashboard_chart_data",
    "_result",
    "_setup_dashboard_page",
    "_setup_evidence_page",
    "_setup_evidence_st",
    "_setup_main_search_st",
    "_setup_main_session_results",
    "_setup_render_results_st",
    "_setup_verified_evidence_page",
    "_sidebar_retriever",
    "contextmanager",
    "patch",
)
