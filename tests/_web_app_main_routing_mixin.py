"""Main-page routing and empty-archive cases."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


class _MainRoutingCasesMixin:
    @pytest.mark.parametrize(
        ("page_name", "handler_name"),
        [
            ("Overview", "dashboard"),
            ("People", "entity"),
            ("Connections", "network"),
            ("Evidence", "evidence"),
        ],
    )
    def test_main_routes_to_page(self, page_name, handler_name):
        from mailarium.web_app import main

        with self._patch_main_deps() as m:
            m.st.sidebar.radio.return_value = page_name
            m.get_retriever.return_value = MagicMock()
            main()
            getattr(m, handler_name).assert_called_once()

    def test_main_empty_collection_shows_warning(self):
        from mailarium.web_app import main

        with self._patch_main_deps() as m:
            retriever = MagicMock()
            retriever.collection.count.return_value = 0
            m.get_retriever.return_value = retriever
            main()
            m.st.warning.assert_called_with("No emails indexed yet.")
