"""Answer-context thread grouping cases."""

import pytest

from .helpers.answer_context_fakes import _run_answer_context_json
from .helpers.mcp_tool_extended_fakes import _inferred_thread_dependencies


@pytest.mark.asyncio
async def test_email_answer_context_groups_by_inferred_thread_when_canonical_missing(monkeypatch):
    from mailarium.mcp_models import EmailAnswerContextInput

    retriever, email_db = _inferred_thread_dependencies()
    data = await _run_answer_context_json(
        monkeypatch,
        retriever=retriever,
        db=email_db,
        params=EmailAnswerContextInput(question="What happened in the inferred thread?", max_results=2),
    )

    group = data["conversation_groups"][0]
    assert group["conversation_id"] == ""
    assert group["inferred_thread_id"] == "thread-inferred-1"
    assert group["thread_group_id"] == "thread-inferred-1"
    assert group["thread_group_source"] == "inferred"
    assert group["top_uid"] == "uid-inferred-2"
    assert group["message_count"] == 2
    assert group["participants"] == ["bob@example.com", "employee@example.test"]
    assert data["candidates"][0]["conversation_context"]["thread_group_source"] == "inferred"
    assert data["answer_quality"]["top_conversation_id"] == ""
    assert data["answer_quality"]["top_thread_group_id"] == "thread-inferred-1"
    assert data["answer_quality"]["top_thread_group_source"] == "inferred"
