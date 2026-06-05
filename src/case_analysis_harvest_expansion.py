# mypy: disable-error-code=name-defined
# pylint: disable=too-many-arguments,too-many-locals,too-many-positional-arguments


# pylint: disable=E0602  # cross-module names injected by compatibility facade
"""Split archive-harvest helpers (case_analysis_harvest_expansion)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .case_analysis_harvest_common import (
    EnrichedRowIdentity,
    _build_enriched_row_identity,
    _compact,
)
from .case_analysis_harvest_expansion_diagnostics import _coerce_expansion_stage_result
from .case_analysis_harvest_expansion_rows import (
    _attachment_expansion_rows,
    _thread_expansion_rows,
)
from .mcp_models import EmailAnswerContextInput

if TYPE_CHECKING:
    from .tools.utils import ToolDepsProto

# ruff: noqa: F401


def _enrich_segment_candidate(
    db: Any,
    entry: dict[str, Any],
    metadata: dict[str, Any],
    result: Any,
    impl: Any,
    index: int,
    uid: str,
) -> dict[str, Any]:
    segment_full_email: dict[str, Any] = {}
    if db is not None and uid and hasattr(db, "get_emails_full_batch"):
        segment_full_email = dict((db.get_emails_full_batch([uid]) or {}).get(uid) or {})
    thread_locator = impl._thread_locator_for_candidate(
        {"uid": uid, "conversation_id": metadata.get("conversation_id", "")},
        segment_full_email or None,
    )
    recipients_summary = impl._recipients_summary(segment_full_email or None)
    speaker_attribution = impl._speaker_attribution_for_candidate(
        db,
        uid=uid,
        conversation_id=str(metadata.get("conversation_id") or ""),
        sender_email=str(metadata.get("sender_email") or ""),
        sender_name=str(metadata.get("sender_name") or ""),
        conversation_context=None,
        full_email=segment_full_email or None,
    )
    reply_context_from, reply_context_emails = impl._reply_context_identities(
        segment_full_email or None,
        str(metadata.get("sender_email") or ""),
    )
    return _build_enriched_row_identity(
        index,
        entry,
        metadata,
        result,
        identity=EnrichedRowIdentity(
            snippet=impl._snippet(getattr(result, "text", "") or ""),
            body_render_mode="segment",
            body_render_source=_compact(metadata.get("body_render_source")) or "message_segments",
            verification_status="segment_exact",
            provenance={
                "evidence_handle": (
                    f"segment:{uid}:{_compact(metadata.get('segment_type'))}:{int(metadata.get('segment_ordinal') or 0)}"
                ),
                "uid": uid,
                "segment_type": _compact(metadata.get("segment_type")),
                "segment_ordinal": int(metadata.get("segment_ordinal") or 0),
                "body_render_source": _compact(metadata.get("body_render_source")) or "message_segments",
            },
            harvest_source="segment_search",
            recipients_summary=recipients_summary,
            speaker_attribution=speaker_attribution,
            reply_context_from=reply_context_from,
            reply_context_emails=reply_context_emails,
            thread_locator=thread_locator,
            email_language_source=segment_full_email or metadata,
            extra_fields={
                "segment_type": _compact(metadata.get("segment_type")),
                "segment_ordinal": int(metadata.get("segment_ordinal") or 0),
            },
        ),
    )


def _enrich_body_candidate(
    db: Any,
    entry: dict[str, Any],
    metadata: dict[str, Any],
    result: Any,
    impl: Any,
    index: int,
    uid: str,
) -> dict[str, Any]:
    retrieval_snippet = impl._snippet(getattr(result, "text", "") or "")
    provenance_result = impl._provenance_for_candidate(
        db,
        uid,
        retrieval_snippet,
        metadata=metadata,
    )
    snippet = provenance_result[0]
    body_render_mode = provenance_result[1]
    body_render_source = provenance_result[2]
    verification_status = provenance_result[3]
    provenance_payload = provenance_result[4]
    full_email: dict[str, Any] | None = provenance_result[5]
    thread_locator = impl._thread_locator_for_candidate(
        {"uid": uid, "conversation_id": metadata.get("conversation_id", "")},
        full_email,
    )
    recipients_summary = impl._recipients_summary(full_email)
    speaker_attribution = impl._speaker_attribution_for_candidate(
        db,
        uid=uid,
        conversation_id=str(metadata.get("conversation_id") or ""),
        sender_email=str(metadata.get("sender_email") or ""),
        sender_name=str(metadata.get("sender_name") or ""),
        conversation_context=None,
        full_email=full_email,
    )
    reply_context_from, reply_context_emails = impl._reply_context_identities(
        full_email,
        str(metadata.get("sender_email") or ""),
    )
    return _build_enriched_row_identity(
        index,
        entry,
        metadata,
        result,
        identity=EnrichedRowIdentity(
            snippet=snippet,
            body_render_mode=body_render_mode,
            body_render_source=body_render_source,
            verification_status=verification_status,
            provenance=provenance_payload,
            harvest_source="search_result",
            recipients_summary=recipients_summary,
            speaker_attribution=speaker_attribution,
            reply_context_from=reply_context_from,
            reply_context_emails=reply_context_emails,
            thread_locator=thread_locator,
            email_language_source=full_email or {},
        ),
    )


def _augment_event_occurrences(
    db: Any,
    enriched_rows: list[dict[str, Any]],
) -> None:
    candidate_uids = [str(item.get("uid") or "") for item in enriched_rows if _compact(item.get("uid"))]
    if db is None or not candidate_uids:
        return
    event_map = db.event_records_for_uids(candidate_uids) if hasattr(db, "event_records_for_uids") else {}
    occurrence_map = db.entity_occurrences_for_uids(candidate_uids) if hasattr(db, "entity_occurrences_for_uids") else {}
    for row in enriched_rows:
        uid = _compact(row.get("uid"))
        if not uid:
            continue
        events = event_map.get(uid) if isinstance(event_map, dict) else None
        if isinstance(events, list) and events:
            row["event_records"] = [dict(item) for item in events if isinstance(item, dict)]
        occurrences = occurrence_map.get(uid) if isinstance(occurrence_map, dict) else None
        if isinstance(occurrences, list) and occurrences:
            row["entity_occurrences"] = [dict(item) for item in occurrences if isinstance(item, dict)]


def _enrich_evidence_bank(
    *,
    db: Any,
    answer_params: EmailAnswerContextInput,
    bank_entries: list[dict[str, Any]],
    bank_results: list[Any],
    exhaustive_review: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    from .tools import search_answer_context_impl as impl

    enriched: list[dict[str, Any]] = []
    for index, entry in enumerate(bank_entries):
        result = bank_results[index] if index < len(bank_results) else None
        if result is None:
            enriched.append(dict(entry))
            continue
        metadata = dict(result.metadata) if isinstance(result.metadata, dict) else {}
        metadata.setdefault("evidence_mode", answer_params.evidence_mode)
        uid = _compact(metadata.get("uid"))
        if _compact(metadata.get("score_kind")) == "segment_sql":
            enriched.append(_enrich_segment_candidate(db, entry, metadata, result, impl, index, uid))
            continue
        if _compact(entry.get("candidate_kind")) == "attachment":
            attachment_candidate = impl._attachment_candidate(db, result, rank=index + 1, params=answer_params)
            attachment_candidate["harvest_source"] = "search_result"
            attachment_candidate["harvest_round"] = int(entry.get("harvest_round") or 0)
            enriched.append({**dict(entry), **attachment_candidate, "candidate_kind": "attachment"})
            continue
        enriched.append(_enrich_body_candidate(db, entry, metadata, result, impl, index, uid))

    _augment_event_occurrences(db, enriched)

    expanded = [*enriched]
    thread_rows, thread_diagnostics = _coerce_expansion_stage_result(
        _thread_expansion_rows(db, evidence_bank=enriched, exhaustive_review=exhaustive_review),
        stage="thread_expansion",
    )
    attachment_rows, attachment_diagnostics = _coerce_expansion_stage_result(
        _attachment_expansion_rows(db, evidence_bank=enriched, exhaustive_review=exhaustive_review),
        stage="attachment_expansion",
    )
    expanded.extend(thread_rows)
    expanded.extend(attachment_rows)
    expansion_diagnostics = {
        "status": (
            "partial"
            if int(thread_diagnostics.get("error_count") or 0) > 0 or int(attachment_diagnostics.get("error_count") or 0) > 0
            else "ok"
        ),
        "error_count": int(thread_diagnostics.get("error_count") or 0) + int(attachment_diagnostics.get("error_count") or 0),
        "thread_expansion": thread_diagnostics,
        "attachment_expansion": attachment_diagnostics,
    }
    return expanded, expansion_diagnostics


__all__ = [
    "_attachment_expansion_rows",
    "_augment_event_occurrences",
    "_enrich_body_candidate",
    "_enrich_evidence_bank",
    "_enrich_segment_candidate",
    "_thread_expansion_rows",
]
