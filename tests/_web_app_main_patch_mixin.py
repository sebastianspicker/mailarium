"""Shared patch matrix for main-page web application cases."""

from __future__ import annotations

from contextlib import ExitStack, contextmanager
from types import SimpleNamespace
from unittest.mock import patch


class _MainPatchMixin:
    @contextmanager
    def _patch_main_deps(self):
        targets = {
            "st": "mailarium.web_app.st",
            "get_retriever": "mailarium.web_app.get_retriever",
            "inject": "mailarium.web_app.inject_styles",
            "sidebar": "mailarium.web_app.render_sidebar_impl",
            "dashboard": "mailarium.web_app.render_dashboard_page",
            "entity": "mailarium.web_app.render_entity_page",
            "network": "mailarium.web_app.render_network_page",
            "evidence": "mailarium.web_app.render_evidence_page",
            "render_results": "mailarium.web_app.render_results",
            "summary": "mailarium.web_app.render_results_summary",
            "workspace": "mailarium.web_app_search.render_search_workspace_impl",
            "labels": "mailarium.web_app.build_active_filter_labels",
            "export": "mailarium.web_app.build_export_payload",
            "csv": "mailarium.web_app._build_csv_export",
        }
        with ExitStack() as stack:
            mocks = {name: stack.enter_context(patch(target)) for name, target in targets.items()}
            mocks["export"].return_value = {}
            mocks["csv"].return_value = ""
            mocks["labels"].return_value = []
            mocks["st"].sidebar.text_input.return_value = ""
            yield SimpleNamespace(**mocks)
