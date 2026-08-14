"""Retriever and dependency doubles for MCP tool tests."""

from __future__ import annotations

from mailarium.retriever import SearchResult

from .diagnostics_fakes import ToolDependencyAnnotations
from .mcp_tool_email_db_fakes import MockEmailDB


def _make_result(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    uid="uid-1",
    text="Please review the budget proposal.",
    subject="Budget Review",
    sender="employee@example.test",
    date="2025-06-01",
    conversation_id="conv-1",
    distance=0.2,
):
    """Build deterministic result data without external services."""
    return SearchResult(
        chunk_id=f"chunk_{uid}",
        text=text,
        metadata={
            "uid": uid,
            "subject": subject,
            "sender_email": sender,
            "sender_name": sender.split("@")[0].title(),
            "date": date,
            "conversation_id": conversation_id,
        },
        distance=distance,
    )


class MockRetriever:
    """Retriever stub supporting the methods used by thread/browse tools."""

    def search_by_thread(self, conversation_id=None, top_k=50):
        """Implement the search by thread behavior exposed by the MockRetriever test double."""
        return [
            _make_result(uid="uid-1", text="We decided to go with vendor A."),
            _make_result(uid="uid-2", text="Please send the updated report by Friday.", sender="bob@example.com"),
        ]

    def search_filtered(self, query="", top_k=10, **kwargs):
        """Implement the search filtered behavior exposed by the MockRetriever test double."""
        return [_make_result()]

    def format_results_for_llm(self, results):
        """Implement the format results for llm behavior exposed by the MockRetriever test double."""
        return "formatted results"

    def serialize_results(self, query, results):
        """Implement the serialize results behavior exposed by the MockRetriever test double."""
        return {"query": query, "count": len(results), "results": []}

    def list_senders(self, limit=30):
        """Implement the list senders behavior exposed by the MockRetriever test double."""
        return [{"name": "Alice", "email": "employee@example.test", "count": 10}]


class MockDeps(ToolDependencyAnnotations):
    """Dependency injection for tool modules matching ToolDepsProto."""

    _retriever = MockRetriever()
    _email_db = MockEmailDB()

    @classmethod
    def get_retriever(cls):
        """Implement the get retriever behavior exposed by the MockDeps test double."""
        return cls._retriever

    @classmethod
    def get_email_db(cls):
        """Implement the get email db behavior exposed by the MockDeps test double."""
        return cls._email_db
