"""Extracts event signals from authored and attachment text while limiting quoted-history evidence to a weak fallback."""

from __future__ import annotations

import re
from types import SimpleNamespace

import mailarium.event_extractor as event_extractor
from mailarium.event_extractor import (
    _extract_from_candidates,
    _ExtractionPass,
    _is_boilerplate_surface,
    extract_event_rows_from_email,
)


def _expected_provenance(
    *,
    source_scope: str,
    surface_scope: str,
    segment_ordinal: int | None,
    char_start: int,
    char_end: int,
    surface_hash: str,
    quoted_guardrail_fallback: bool,
) -> str:
    """Return the exact, stable event provenance serialization expected by persistence."""
    ordinal = "null" if segment_ordinal is None else str(segment_ordinal)
    fallback = str(quoted_guardrail_fallback).lower()
    return (
        f'{{"source_scope": "{source_scope}", "surface_scope": "{surface_scope}", '
        f'"segment_ordinal": {ordinal}, "char_start": {char_start}, "char_end": {char_end}, '
        f'"surface_hash": "{surface_hash}", "quoted_guardrail_fallback": {fallback}}}'
    )


def test_extract_event_rows_from_email_emits_authored_and_attachment_events() -> None:
    email = SimpleNamespace(
        uid="uid-event-1",
        date="2026-03-01",
        segments=[
            SimpleNamespace(
                ordinal=0,
                segment_type="authored_body",
                text="Bitte um Rückmeldung bis spätestens morgen.",
            ),
            SimpleNamespace(
                ordinal=1,
                segment_type="quoted_reply",
                text="Historischer Block ohne neue Ereignisse.",
            ),
        ],
        attachments=[
            {
                "name": "meeting.txt",
                "normalized_text": "SBV Beteiligung wurde nicht einbezogen.",
            }
        ],
    )

    rows = extract_event_rows_from_email(email)
    assert rows == [
        (
            "02b6f77bf25e584cd2a4500144560a940e005e3bfb3f58d68f84b71344e069c3",
            "uid-event-1",
            "request",
            "authored_body",
            "message_segments",
            0,
            0,
            5,
            "Bitte",
            "2026-03-01",
            "f0d7a8f0e2ad705289005503cb273639d667dc98dbd29d29f6546fa61283656a",
            "de",
            "high",
            "de_event_rule_v1",
            _expected_provenance(
                source_scope="authored_body",
                surface_scope="message_segments",
                segment_ordinal=0,
                char_start=0,
                char_end=5,
                surface_hash="f0d7a8f0e2ad705289005503cb273639d667dc98dbd29d29f6546fa61283656a",
                quoted_guardrail_fallback=False,
            ),
        ),
        (
            "cc7b571df3d69043c8cff1802e65ce4e23d6abeff2889b8befa65c451556513b",
            "uid-event-1",
            "request",
            "authored_body",
            "message_segments",
            0,
            6,
            20,
            "um Rückmeldung",
            "2026-03-01",
            "f0d7a8f0e2ad705289005503cb273639d667dc98dbd29d29f6546fa61283656a",
            "de",
            "high",
            "de_event_rule_v1",
            _expected_provenance(
                source_scope="authored_body",
                surface_scope="message_segments",
                segment_ordinal=0,
                char_start=6,
                char_end=20,
                surface_hash="f0d7a8f0e2ad705289005503cb273639d667dc98dbd29d29f6546fa61283656a",
                quoted_guardrail_fallback=False,
            ),
        ),
        (
            "b61fea4456f18be667fcdc4f0f96ff918cbd237f0cfc74cb37c8508670ac0c4c",
            "uid-event-1",
            "deadline_pressure",
            "authored_body",
            "message_segments",
            0,
            25,
            35,
            "spätestens",
            "2026-03-01",
            "f0d7a8f0e2ad705289005503cb273639d667dc98dbd29d29f6546fa61283656a",
            "de",
            "high",
            "de_event_rule_v1",
            _expected_provenance(
                source_scope="authored_body",
                surface_scope="message_segments",
                segment_ordinal=0,
                char_start=25,
                char_end=35,
                surface_hash="f0d7a8f0e2ad705289005503cb273639d667dc98dbd29d29f6546fa61283656a",
                quoted_guardrail_fallback=False,
            ),
        ),
        (
            "4667965a01512ee42ccea3c010e48729571d5442a2e78c5e79e182e86b5109bd",
            "uid-event-1",
            "exclusion_or_omission",
            "attachment_text",
            "attachments",
            0,
            22,
            38,
            "nicht einbezogen",
            "2026-03-01",
            "96ec08fdb962d33d1beb217783d69e3b35890d5f19eb0d6aabdc0d139b67a1ca",
            "de",
            "high",
            "de_event_rule_v1",
            _expected_provenance(
                source_scope="attachment_text",
                surface_scope="attachments",
                segment_ordinal=0,
                char_start=22,
                char_end=38,
                surface_hash="96ec08fdb962d33d1beb217783d69e3b35890d5f19eb0d6aabdc0d139b67a1ca",
                quoted_guardrail_fallback=False,
            ),
        ),
        (
            "255456bc984ec9c3974d66c47517aaccb825481f37123d831e4fbd10b18a10dd",
            "uid-event-1",
            "accommodation_or_participation",
            "attachment_text",
            "attachments",
            0,
            0,
            3,
            "SBV",
            "2026-03-01",
            "96ec08fdb962d33d1beb217783d69e3b35890d5f19eb0d6aabdc0d139b67a1ca",
            "de",
            "high",
            "de_event_rule_v1",
            _expected_provenance(
                source_scope="attachment_text",
                surface_scope="attachments",
                segment_ordinal=0,
                char_start=0,
                char_end=3,
                surface_hash="96ec08fdb962d33d1beb217783d69e3b35890d5f19eb0d6aabdc0d139b67a1ca",
                quoted_guardrail_fallback=False,
            ),
        ),
    ]


def test_extract_event_rows_from_email_returns_empty_without_uid() -> None:
    email = SimpleNamespace(uid="", date="", segments=[], attachments=[])

    assert extract_event_rows_from_email(email) == []


def test_extract_event_rows_skips_quoted_events_when_authored_signal_exists() -> None:
    email = SimpleNamespace(
        uid="uid-event-quoted-1",
        date="2026-03-02",
        segments=[
            SimpleNamespace(ordinal=0, segment_type="authored_body", text="Bitte um Rueckmeldung heute."),
            SimpleNamespace(ordinal=1, segment_type="quoted_reply", text="Der Antrag wurde abgelehnt."),
        ],
        attachments=[],
    )

    rows = extract_event_rows_from_email(email)
    kinds = {str(row[2]) for row in rows}
    scopes = {str(row[3]) for row in rows}

    assert "request" in kinds
    assert "denial" not in kinds
    assert "quoted_body" not in scopes


def test_extract_event_rows_quoted_fallback_marks_low_confidence() -> None:
    email = SimpleNamespace(
        uid="uid-event-quoted-fallback",
        date="2026-03-03",
        segments=[SimpleNamespace(ordinal=0, segment_type="quoted_reply", text="Der Antrag wurde abgelehnt.")],
        attachments=[],
    )

    rows = extract_event_rows_from_email(email)
    assert rows == [
        (
            "f95017708e063cd2389ef77c81ea23558ed657cb2c42bf71d10f7a53faca7ab4",
            "uid-event-quoted-fallback",
            "denial",
            "quoted_body",
            "message_segments",
            0,
            17,
            26,
            "abgelehnt",
            "2026-03-03",
            "7f83e5ae85f5a9b9de9b1968b8323119967b72a9c53b4854ea1c8efef2251852",
            "unknown",
            "low",
            "de_event_rule_v1",
            _expected_provenance(
                source_scope="quoted_body",
                surface_scope="message_segments",
                segment_ordinal=0,
                char_start=17,
                char_end=26,
                surface_hash="7f83e5ae85f5a9b9de9b1968b8323119967b72a9c53b4854ea1c8efef2251852",
                quoted_guardrail_fallback=True,
            ),
        )
    ]


def test_extract_event_rows_ignores_footer_boilerplate() -> None:
    footer_text = "This email is confidential and intended recipient only. Bitte nicht drucken. Diese E-Mail ist vertraulich."
    email = SimpleNamespace(
        uid="uid-event-footer",
        date="2026-03-04",
        segments=[SimpleNamespace(ordinal=0, segment_type="authored_body", text=footer_text)],
        attachments=[],
    )

    assert extract_event_rows_from_email(email) == []


def test_boilerplate_detection_handles_empty_and_unbounded_surfaces() -> None:
    assert _is_boilerplate_surface("   \n\t") is True
    assert _is_boilerplate_surface("This email is confidential and intended recipient only. " + ("x" * 601)) is False


def test_candidate_preparation_skips_empty_text_and_empty_cleaned_matches(monkeypatch) -> None:
    extraction_pass = _ExtractionPass(
        uid="uid-event-empty",
        event_date="2026-03-04",
        seen_event_keys=set(),
        degrade_confidence=False,
        skip_boilerplate=False,
    )
    monkeypatch.setattr(event_extractor, "_EVENT_RULES", (("request", re.compile(r"\s+")),))

    rows = _extract_from_candidates(
        extraction_pass=extraction_pass,
        candidates=[("authored_body", "message_segments", 0, ""), ("authored_body", "message_segments", 1, " ")],
    )

    assert rows == []
    assert extraction_pass.seen_event_keys == set()


def test_extraction_pass_suppresses_duplicate_event_keys_across_calls_without_reordering() -> None:
    seen_event_keys: set[str] = set()
    candidate = ("authored_body", "message_segments", None, "Bitte heute.")
    extraction_pass = _ExtractionPass(
        uid="uid-event-dedup",
        event_date="2026-03-05",
        seen_event_keys=seen_event_keys,
        degrade_confidence=False,
        skip_boilerplate=True,
    )

    rows = _extract_from_candidates(
        extraction_pass=extraction_pass,
        candidates=[candidate],
    )

    assert rows == [
        (
            "fa94af744dcff5c7f42ad6da89df63f2f8a0eee9e87759e7a2807c89a7edb5c7",
            "uid-event-dedup",
            "request",
            "authored_body",
            "message_segments",
            None,
            0,
            5,
            "Bitte",
            "2026-03-05",
            "e7ae5987c3524b023300eb3c8f2a0d1504fd7e44ab76587738f86a8b0f06ba00",
            "de",
            "low",
            "de_event_rule_v1",
            _expected_provenance(
                source_scope="authored_body",
                surface_scope="message_segments",
                segment_ordinal=None,
                char_start=0,
                char_end=5,
                surface_hash="e7ae5987c3524b023300eb3c8f2a0d1504fd7e44ab76587738f86a8b0f06ba00",
                quoted_guardrail_fallback=False,
            ),
        ),
        (
            "50fc15eb83f244cec3e623be0ba8a9ff4a735828e114a9561434e9575a9aefde",
            "uid-event-dedup",
            "deadline_pressure",
            "authored_body",
            "message_segments",
            None,
            6,
            11,
            "heute",
            "2026-03-05",
            "e7ae5987c3524b023300eb3c8f2a0d1504fd7e44ab76587738f86a8b0f06ba00",
            "de",
            "low",
            "de_event_rule_v1",
            _expected_provenance(
                source_scope="authored_body",
                surface_scope="message_segments",
                segment_ordinal=None,
                char_start=6,
                char_end=11,
                surface_hash="e7ae5987c3524b023300eb3c8f2a0d1504fd7e44ab76587738f86a8b0f06ba00",
                quoted_guardrail_fallback=False,
            ),
        ),
    ]
    assert len({row[0] for row in rows}) == len(rows)
    assert len(seen_event_keys) == len(rows)
    assert all(len(row) == 15 for row in rows)
    assert _extract_from_candidates(extraction_pass=extraction_pass, candidates=[candidate]) == []
    assert len(seen_event_keys) == len(rows)


def test_extract_event_rows_falls_back_to_quoted_only_after_primary_and_attachment_yield_no_rows() -> None:
    footer_text = "This email is confidential and intended recipient only. Bitte nicht drucken. Diese E-Mail ist vertraulich."
    email = SimpleNamespace(
        uid="uid-event-guardrail-order",
        date="2026-03-06",
        segments=[
            SimpleNamespace(ordinal=0, segment_type="authored_body", text=footer_text),
            SimpleNamespace(ordinal=1, segment_type="quoted_reply", text="Der Antrag wurde abgelehnt. Bitte heute."),
        ],
        attachments=[{"normalized_text": footer_text}],
    )

    rows = extract_event_rows_from_email(email)

    assert [tuple(row[index] for index in (2, 3, 8, 12)) for row in rows] == [
        ("request", "quoted_body", "Bitte", "low"),
        ("denial", "quoted_body", "abgelehnt", "low"),
        ("deadline_pressure", "quoted_body", "heute", "low"),
    ]
    assert all('"quoted_guardrail_fallback": true' in str(row[14]) for row in rows)
