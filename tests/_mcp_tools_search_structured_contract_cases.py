"""MCP structured-search input and response contract cases."""

import json

import pytest

from .helpers.mcp_tool_fakes import _BasicRetriever, _make_result, _patch_capturing_search_deps, _patch_search_deps


@pytest.mark.asyncio
async def test_email_search_structured_forwards_new_filters(monkeypatch):
    from mailarium.mcp_models import EmailSearchStructuredInput
    from mailarium.tools.search import email_search_structured

    captured = _patch_capturing_search_deps(monkeypatch)

    params = EmailSearchStructuredInput(
        query="hello",
        top_k=5,
        scope="Finance Operations",
        subject="approval",
        folder="inbox",
        cc="finance",
        min_score=0.8,
    )
    payload = await email_search_structured(params)
    data = json.loads(payload)

    assert captured["subject"] == "approval"
    assert captured["folder"] == "inbox"
    assert captured["cc"] == "finance"
    assert captured["min_score"] == 0.8
    assert captured["scope"] == "finance operations"
    assert data["filters"]["subject"] == "approval"
    assert data["filters"]["folder"] == "inbox"
    assert data["filters"]["cc"] == "finance"
    assert data["filters"]["min_score"] == 0.8
    assert data["filters"]["scope"] == "finance operations"


@pytest.mark.asyncio
async def test_email_search_structured_accepts_legacy_aliases(monkeypatch):
    from mailarium.mcp_models import EmailSearchStructuredInput
    from mailarium.tools.search import email_search_structured

    captured = _patch_capturing_search_deps(monkeypatch)

    params = EmailSearchStructuredInput.model_validate(
        {
            "query": "hello",
            "max_results": 7,
            "query_expansion": True,
        }
    )
    payload = await email_search_structured(params)
    data = json.loads(payload)

    assert captured["top_k"] == 7
    assert captured["expand_query"] is True
    assert data["top_k"] == 7
    assert data["filters"]["expand_query"] is True


@pytest.mark.asyncio
async def test_email_search_structured_emits_strict_json(monkeypatch):
    from mailarium.mcp_models import EmailSearchStructuredInput
    from mailarium.tools.search import email_search_structured

    class DummyRetriever(_BasicRetriever):
        def search_filtered(self, query, top_k=10, **kwargs):
            return [_make_result(distance=float("nan"))]

    _patch_search_deps(monkeypatch, DummyRetriever())

    params = EmailSearchStructuredInput(query="hello", top_k=5)
    payload = await email_search_structured(params)

    assert "NaN" not in payload
    assert "Infinity" not in payload


@pytest.mark.asyncio
async def test_email_search_structured_exposes_retrieval_diagnostics(monkeypatch):
    from mailarium.mcp_models import EmailSearchStructuredInput
    from mailarium.tools.search import email_search_structured

    class DummyRetriever(_BasicRetriever):
        @property
        def last_search_debug(self):
            return {
                "original_query": "student.case@example.test",
                "executed_query": "student.case@example.test sbv timeline",
                "expand_query_requested": True,
                "used_query_expansion": True,
                "query_expansion_suffix": "sbv timeline",
                "retrieval_policy": {
                    "scope": "general",
                    "semantic_weight": 0.3,
                    "keyword_weight": 0.7,
                    "allow_domain_boost": False,
                    "reason_codes": ["scope_general", "email_token"],
                },
                "fusion": {
                    "method": "weighted_reciprocal_rank_fusion",
                    "semantic_weight": 0.3,
                    "keyword_weight": 0.7,
                },
            }

    _patch_search_deps(monkeypatch, DummyRetriever())

    params = EmailSearchStructuredInput(query="student.case@example.test", expand_query=True)
    payload = await email_search_structured(params)
    data = json.loads(payload)

    assert data["retrieval_diagnostics"]["original_query"] == "student.case@example.test"
    assert data["retrieval_diagnostics"]["executed_query"].endswith("sbv timeline")
    assert data["retrieval_diagnostics"]["expand_query_requested"] is True
    assert data["retrieval_diagnostics"]["used_query_expansion"] is True
    assert data["retrieval_diagnostics"]["retrieval_policy"]["scope"] == "general"
    assert data["retrieval_diagnostics"]["fusion"]["keyword_weight"] == 0.7


@pytest.mark.asyncio
async def test_email_search_structured_exposes_semantic_filter_failure_diagnostics(monkeypatch):
    from mailarium.mcp_models import EmailSearchStructuredInput
    from mailarium.tools.search import email_search_structured

    class DummyRetriever(_BasicRetriever):
        @property
        def last_search_debug(self):
            return {
                "original_query": "budget",
                "executed_query": "budget",
                "semantic_filter_status": "error",
                "semantic_filter_uid_count": 0,
                "semantic_filter_errors": [
                    {
                        "filter": "topic_id",
                        "value": 7,
                        "error_type": "RuntimeError",
                        "message": "topic lookup failed",
                    }
                ],
            }

    _patch_search_deps(monkeypatch, DummyRetriever())

    params = EmailSearchStructuredInput(query="budget", topic_id=7)
    payload = await email_search_structured(params)
    data = json.loads(payload)

    diagnostics = data["retrieval_diagnostics"]
    assert diagnostics["semantic_filter_status"] == "error"
    assert diagnostics["semantic_filter_uid_count"] == 0
    assert diagnostics["semantic_filter_errors"][0]["filter"] == "topic_id"
    assert diagnostics["semantic_filter_errors"][0]["error_type"] == "RuntimeError"


@pytest.mark.asyncio
async def test_email_search_structured_exposes_query_expansion_failure_diagnostics(monkeypatch):
    from mailarium.mcp_models import EmailSearchStructuredInput
    from mailarium.tools.search import email_search_structured

    class DummyRetriever(_BasicRetriever):
        @property
        def last_search_debug(self):
            return {
                "original_query": "budget",
                "executed_query": "budget",
                "expand_query_requested": True,
                "used_query_expansion": False,
                "query_expansion_status": "error",
                "query_expansion_error_type": "RuntimeError",
                "query_expansion_error": "cannot import query expander",
            }

    _patch_search_deps(monkeypatch, DummyRetriever())

    params = EmailSearchStructuredInput(query="budget", expand_query=True)
    payload = await email_search_structured(params)
    data = json.loads(payload)

    diagnostics = data["retrieval_diagnostics"]
    assert diagnostics["query_expansion_status"] == "error"
    assert diagnostics["query_expansion_error_type"] == "RuntimeError"
    assert diagnostics["query_expansion_error"] == "cannot import query expander"


@pytest.mark.asyncio
async def test_email_search_structured_forwards_email_type(monkeypatch):
    from mailarium.mcp_models import EmailSearchStructuredInput
    from mailarium.tools.search import email_search_structured

    captured = _patch_capturing_search_deps(monkeypatch)

    params = EmailSearchStructuredInput(
        query="hello",
        email_type="reply",
    )
    payload = await email_search_structured(params)
    data = json.loads(payload)

    assert captured["email_type"] == "reply"
    assert data["filters"]["email_type"] == "reply"


@pytest.mark.asyncio
async def test_email_search_structured_forwards_attachment_filters(monkeypatch):
    from mailarium.mcp_models import EmailSearchStructuredInput
    from mailarium.tools.search import email_search_structured

    captured = _patch_capturing_search_deps(monkeypatch)

    params = EmailSearchStructuredInput(
        query="hello",
        attachment_name="report",
        attachment_type="pdf",
    )
    payload = await email_search_structured(params)
    data = json.loads(payload)

    assert captured["attachment_name"] == "report"
    assert captured["attachment_type"] == "pdf"
    assert data["filters"]["attachment_name"] == "report"
    assert data["filters"]["attachment_type"] == "pdf"
