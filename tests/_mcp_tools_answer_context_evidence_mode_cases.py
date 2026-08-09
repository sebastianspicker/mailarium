"""Answer-context evidence and public response mode cases."""

import pytest

from .helpers.answer_context_fakes import _run_answer_context_json
from .helpers.mcp_tool_fakes import _BasicRetriever, _make_result


@pytest.mark.asyncio
async def test_email_answer_context_returns_ranked_evidence_bundle(monkeypatch):
    from mailarium.mcp_models import EmailAnswerContextInput

    class DummyRetriever(_BasicRetriever):
        def search_filtered(self, query, top_k=10, **kwargs):
            assert query == "Who asked for the updated budget?"
            assert top_k == 3
            assert kwargs["sender"] == "employee@example.test"
            return [
                _make_result(
                    uid="uid-ctx-1",
                    chunk_id="chunk-1",
                    text="Please send the updated budget by Friday.",
                    distance=0.15,
                )
            ]

    class DummyDB:
        conn = None

        def get_emails_full_batch(self, uids):
            return {
                "uid-ctx-1": {
                    "uid": "uid-ctx-1",
                    "body_text": "Intro. Please send the updated budget by Friday. Thanks.",
                    "normalized_body_source": "body_text_html",
                    "forensic_body_text": "",
                    "forensic_body_source": "",
                }
            }

    data = await _run_answer_context_json(
        monkeypatch,
        retriever=DummyRetriever(),
        db=DummyDB(),
        params=EmailAnswerContextInput(
            question="Who asked for the updated budget?",
            max_results=3,
            sender="employee@example.test",
        ),
    )

    assert data["question"] == "Who asked for the updated budget?"
    assert data["count"] == 1
    assert data["candidates"][0]["rank"] == 1
    assert data["candidates"][0]["score"] == pytest.approx(0.85)
    assert data["candidates"][0]["snippet"] == "Please send the updated budget by Friday."
    assert data["candidates"][0]["follow_up"]["tool"] == "email_deep_context"
    assert data["search"]["sender"] == "employee@example.test"
    assert data["candidates"][0]["body_render_mode"] == "retrieval"
    assert data["candidates"][0]["body_render_source"] == "body_text_html"
    assert data["candidates"][0]["provenance"]["uid"] == "uid-ctx-1"
    assert data["candidates"][0]["provenance"]["snippet_start"] == 7
    assert data["candidates"][0]["provenance"]["snippet_end"] == 48
    assert data["candidates"][0]["provenance"]["segment_ordinal"] is None
    assert data["candidates"][0]["provenance"]["evidence_handle"].startswith("email:uid-ctx-1:retrieval:body_text_html:7:48")


@pytest.mark.asyncio
async def test_email_answer_context_forensic_mode_uses_forensic_body(monkeypatch):
    from mailarium.mcp_models import EmailAnswerContextInput

    class DummyRetriever(_BasicRetriever):
        def search_filtered(self, query, top_k=10, **kwargs):
            return [
                _make_result(
                    uid="uid-forensic-1",
                    chunk_id="chunk-1",
                    text="Please send the updated budget by Friday.",
                    distance=0.15,
                )
            ]

    class DummyDB:
        conn = None

        def get_emails_full_batch(self, uids):
            return {
                "uid-forensic-1": {
                    "uid": "uid-forensic-1",
                    "body_text": "Intro. Please send the updated budget by Friday. Thanks.",
                    "normalized_body_source": "body_text_html",
                    "forensic_body_text": "Quoted header\nPlease send the updated budget by Friday.\nRegards",
                    "forensic_body_source": "raw_body_html",
                }
            }

    data = await _run_answer_context_json(
        monkeypatch,
        retriever=DummyRetriever(),
        db=DummyDB(),
        params=EmailAnswerContextInput(
            question="Who asked for the updated budget?",
            evidence_mode="forensic",
        ),
    )

    assert data["evidence_mode"]["requested"] == "forensic"
    assert data["candidates"][0]["body_render_mode"] == "forensic"
    assert data["candidates"][0]["body_render_source"] == "raw_body_html"
    assert data["candidates"][0]["snippet"] == "Please send the updated budget by Friday."
    assert data["candidates"][0]["verification_status"] == "forensic_exact"
    assert data["candidates"][0]["provenance"]["evidence_handle"].startswith("email:uid-forensic-1:forensic:raw_body_html:")


@pytest.mark.asyncio
async def test_email_answer_context_hybrid_mode_falls_back_explicitly_when_forensic_missing(monkeypatch):
    from mailarium.mcp_models import EmailAnswerContextInput

    class DummyRetriever(_BasicRetriever):
        def search_filtered(self, query, top_k=10, **kwargs):
            return [
                _make_result(
                    uid="uid-hybrid-1",
                    chunk_id="chunk-1",
                    text="Please send the updated budget by Friday.",
                    distance=0.15,
                )
            ]

    class DummyDB:
        conn = None

        def get_emails_full_batch(self, uids):
            return {
                "uid-hybrid-1": {
                    "uid": "uid-hybrid-1",
                    "body_text": "Intro. Please send the updated budget by Friday. Thanks.",
                    "normalized_body_source": "body_text_html",
                    "forensic_body_text": "",
                    "forensic_body_source": "",
                }
            }

    data = await _run_answer_context_json(
        monkeypatch,
        retriever=DummyRetriever(),
        db=DummyDB(),
        params=EmailAnswerContextInput(
            question="Who asked for the updated budget?",
            evidence_mode="hybrid",
        ),
    )

    assert data["evidence_mode"]["requested"] == "hybrid"
    assert data["candidates"][0]["body_render_mode"] == "retrieval"
    assert data["candidates"][0]["verification_status"] == "hybrid_fallback_retrieval"
    assert data["candidates"][0]["provenance"]["evidence_handle"].startswith("email:uid-hybrid-1:retrieval:body_text_html:")


@pytest.mark.asyncio
async def test_email_answer_context_handles_no_results(monkeypatch):
    from mailarium.mcp_models import EmailAnswerContextInput

    class DummyRetriever(_BasicRetriever):
        def search_filtered(self, query, top_k=10, **kwargs):
            return []

    data = await _run_answer_context_json(
        monkeypatch,
        retriever=DummyRetriever(),
        db=None,
        params=EmailAnswerContextInput(question="Was there any update on the rack move?"),
    )

    assert data["question"] == "Was there any update on the rack move?"
    assert data["count"] == 0
    assert data["candidates"] == []
    assert data["attachment_candidates"] == []
    assert "message" in data
