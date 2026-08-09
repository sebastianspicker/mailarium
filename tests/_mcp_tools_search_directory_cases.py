"""MCP search directory-listing cases."""

import json

import pytest

from .helpers.mcp_tool_fakes import _patch_search_deps


@pytest.mark.asyncio
async def test_email_list_senders_returns_json(monkeypatch):
    from mailarium.mcp_models import ListSendersInput
    from mailarium.tools.search import email_list_senders

    class DummyRetriever:
        def list_senders(self, limit=30):
            return [
                {
                    "name": "Alice",
                    "email": "employee@example.test",
                    "count": 3,
                }
            ]

    _patch_search_deps(monkeypatch, DummyRetriever())
    output = await email_list_senders(ListSendersInput(limit=10))
    data = json.loads(output)

    assert data["count"] == 1
    assert data["senders"][0]["name"] == "Alice"
    assert data["senders"][0]["count"] == 3


@pytest.mark.asyncio
async def test_email_list_folders_returns_json(monkeypatch):
    from mailarium.tools.search import email_list_folders

    class DummyRetriever:
        def list_folders(self):
            return [
                {"folder": "Inbox", "count": 42},
                {"folder": "Archive", "count": 7},
            ]

    _patch_search_deps(monkeypatch, DummyRetriever())
    output = await email_list_folders()
    data = json.loads(output)

    assert data["count"] == 2
    assert data["folders"][0]["folder"] == "Inbox"
    assert data["folders"][0]["count"] == 42
    assert data["folders"][1]["folder"] == "Archive"


@pytest.mark.asyncio
async def test_email_list_folders_empty_archive(monkeypatch):
    from mailarium.tools.search import email_list_folders

    class DummyRetriever:
        def list_folders(self):
            return []

    _patch_search_deps(monkeypatch, DummyRetriever())
    output = await email_list_folders()
    data = json.loads(output)

    assert data["count"] == 0
    assert data["folders"] == []
