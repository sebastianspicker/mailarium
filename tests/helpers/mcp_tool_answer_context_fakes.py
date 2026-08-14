"""Answer-context-specific MCP tool doubles and assertions."""

from .mcp_tool_search_fakes import MockRetriever, _make_result


def _inferred_thread_dependencies():
    """Build retriever/database doubles for a canonical-missing inferred thread."""

    class InferredThreadRetriever(MockRetriever):
        def search_filtered(self, query="", top_k=10, **kwargs):
            return [
                _make_result(
                    uid="uid-inferred-2",
                    text="Follow-up from the inferred-only thread.",
                    sender="bob@example.com",
                    date="2025-06-05",
                    conversation_id="",
                    distance=0.07,
                ),
                _make_result(
                    uid="uid-inferred-1",
                    text="Original inferred-only message.",
                    sender="employee@example.test",
                    date="2025-06-04",
                    conversation_id="",
                    distance=0.09,
                ),
            ]

    class InferredThreadDB:
        conn = None

        def get_emails_full_batch(self, uids):
            return {
                "uid-inferred-1": {
                    "uid": "uid-inferred-1",
                    "body_text": "Original inferred-only message.",
                    "normalized_body_source": "body_text",
                    "forensic_body_text": "",
                    "forensic_body_source": "",
                    "conversation_id": "",
                    "inferred_thread_id": "thread-inferred-1",
                    "inferred_parent_uid": "",
                },
                "uid-inferred-2": {
                    "uid": "uid-inferred-2",
                    "body_text": "Follow-up from the inferred-only thread.",
                    "normalized_body_source": "body_text",
                    "forensic_body_text": "",
                    "forensic_body_source": "",
                    "conversation_id": "",
                    "inferred_thread_id": "thread-inferred-1",
                    "inferred_parent_uid": "uid-inferred-1",
                    "inferred_match_reason": "base_subject,participants",
                    "inferred_match_confidence": 0.87,
                },
            }

        def get_inferred_thread_emails(self, inferred_thread_id):
            assert inferred_thread_id == "thread-inferred-1"
            return [
                {
                    "uid": "uid-inferred-1",
                    "subject": "Budget Review",
                    "sender_email": "employee@example.test",
                    "sender_name": "Alice",
                    "date": "2025-06-04",
                    "conversation_id": "",
                    "inferred_thread_id": "thread-inferred-1",
                },
                {
                    "uid": "uid-inferred-2",
                    "subject": "Budget Review",
                    "sender_email": "bob@example.com",
                    "sender_name": "Bob",
                    "date": "2025-06-05",
                    "conversation_id": "",
                    "inferred_thread_id": "thread-inferred-1",
                },
            ]

    return InferredThreadRetriever(), InferredThreadDB()


def _assert_strong_attachment_candidate(candidate, *, uid, filename):
    """Assert the stable evidence fields for a text-extracted attachment candidate."""
    assert candidate["uid"] == uid
    assert candidate["attachment"]["filename"] == filename
    assert candidate["attachment"]["size"] == 2048
    assert candidate["attachment"]["extraction_state"] == "text_extracted"
    assert candidate["attachment"]["text_available"] is True
    assert candidate["attachment"]["ocr_used"] is False
    assert candidate["attachment"]["failure_reason"] is None
    assert candidate["attachment"]["evidence_strength"] == "strong_text"
    assert candidate["attachment"]["is_inline"] is False
