"""Structured email search MCP cases."""

import json

import pytest

from .helpers.mcp_tool_fakes import _BasicRetriever, _patch_search_deps


@pytest.mark.asyncio
async def test_email_search_structured_tool_returns_json(monkeypatch):
    from mailarium.mcp_models import EmailSearchStructuredInput
    from mailarium.tools.search import email_search_structured

    _patch_search_deps(monkeypatch, _BasicRetriever())

    params = EmailSearchStructuredInput(query="hello", top_k=5)
    payload = await email_search_structured(params)
    data = json.loads(payload)

    assert data["query"] == "hello"
    assert data["count"] == 1
    assert data["results"][0]["chunk_id"] == "x"
