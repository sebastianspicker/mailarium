"""Deterministic search-result factories for web application tests."""

from __future__ import annotations

from mailarium.retriever import SearchResult


def _result(**overrides: object) -> SearchResult:
    """Provide deterministic result behavior for focused test setup."""
    defaults: dict[str, object] = {
        "chunk_id": "c1",
        "score_distance": 0.2,
        "date": "2024-01-15",
        "sender_email": "a@example.com",
        "sender_name": "Alice",
        "subject": "Test Subject",
        "folder": "Inbox",
        "text": "Hello world body text",
        "to": "",
        "conversation_id": "",
        "email_type": "original",
        "attachment_count": "0",
        "attachment_names": "",
        "priority": "0",
    }
    unknown = sorted(set(overrides) - set(defaults))
    if unknown:
        raise TypeError(f"_result() got unexpected option(s): {', '.join(unknown)}")
    values = defaults | overrides
    return SearchResult(
        chunk_id=str(values["chunk_id"]),
        text=str(values["text"]),
        metadata={
            key: str(values[key])
            for key in (
                "subject",
                "sender_email",
                "sender_name",
                "date",
                "folder",
                "to",
                "conversation_id",
                "email_type",
                "attachment_count",
                "attachment_names",
                "priority",
            )
        },
        distance=float(str(values["score_distance"])),
    )


__all__ = ("_result",)
