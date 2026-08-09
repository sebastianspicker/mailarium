"""Streamlit main-page routing, search state, filtering, failures, and pagination."""

from ._web_app_aux_cases import *  # noqa: F403
from ._web_app_main_patch_mixin import _MainPatchMixin
from ._web_app_main_routing_mixin import _MainRoutingCasesMixin
from ._web_app_main_search_mixin import _MainSearchCasesMixin
from ._web_app_main_session_mixin import _MainSessionCasesMixin


class TestMain(
    _MainPatchMixin,
    _MainRoutingCasesMixin,
    _MainSearchCasesMixin,
    _MainSessionCasesMixin,
):
    """Public collection facade retaining the established main-case IDs."""
