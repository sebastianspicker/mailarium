# mypy: disable-error-code=name-defined
# pylint: disable=too-many-locals


# pylint: disable=E0602  # cross-module names injected by compatibility facade
"""Split archive-harvest expansion-row helpers (case_analysis_harvest_expansion_rows)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .case_analysis_harvest_common import (
    _best_body_text,
    _compact,
    _email_language_fields,
    _expansion_error_entry,
)
from .case_analysis_harvest_expansion_diagnostics import _default_expansion_stage_diagnostics

if TYPE_CHECKING:
    from .tools.utils import ToolDepsProto

# ruff: noqa: F401, F821


def _thread_expansion_rows(
    db: Any,
    *,
    evidence_bank: list[dict[str, Any]],
    exhaustive_review: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    diagnostics = _default_expansion_stage_diagnostics("thread_expansion")
    if db is None or not hasattr(db, "get_thread_emails"):
        return [], diagnostics
    existing_uids = {str(item.get("uid") or "") for item in evidence_bank if _compact(item.get("uid"))}
    expanded: list[dict[str, Any]] = []
    for seed in evidence_bank:
        if str(seed.get("candidate_kind") or "") == "attachment":
            continue
        conversation_id = _compact(seed.get("conversation_id"))
        if not conversation_id:
            continue
        diagnostics["attempted_count"] = int(diagnostics.get("attempted_count") or 0) + 1
        try:
            thread_rows = db.get_thread_emails(conversation_id) or []
        except Exception as exc:  # pylint: disable=broad-exception-caught
            _expansion_error_entry(
                diagnostics,
                {
                    "conversation_id": conversation_id,
                    "seed_uid": _compact(seed.get("uid")),
                    "error_type": type(exc).__name__,
                    "error": _compact(str(exc))[:240],
                },
            )
            continue
        relevance_terms = _seed_relevance_terms(seed)
        ranked_thread_rows = sorted(
            [row for row in thread_rows if isinstance(row, dict)],
            key=lambda row, rt=relevance_terms: (
                -_text_overlap_score(
                    haystack=" ".join(
                        [
                            str(row.get("subject") or ""),
                            str(row.get("sender_name") or ""),
                            str(row.get("sender_email") or ""),
                            _best_body_text(dict(row)),
                        ]
                    ),
                    terms=rt,
                ),
                0 if bool(row.get("has_attachments") or row.get("attachment_count")) else 1,
                str(row.get("date") or ""),
            ),
        )
        max_additions = 4 if exhaustive_review else 2
        additions = 0
        for row in ranked_thread_rows:
            uid = _compact(row.get("uid"))
            if not uid or uid in existing_uids:
                continue
            relevance_score = _text_overlap_score(
                haystack=" ".join([str(row.get("subject") or ""), _best_body_text(dict(row))]),
                terms=relevance_terms,
            )
            existing_uids.add(uid)
            expanded.append(
                {
                    "uid": uid,
                    "chunk_id": f"{uid}:thread_expansion",
                    "score": float(seed.get("score") or 0.0) * (0.85 + min(relevance_score, 4) * 0.03),
                    "subject": _compact(row.get("subject")),
                    "sender_email": _compact(row.get("sender_email")),
                    "sender_name": _compact(row.get("sender_name")),
                    "date": _compact(row.get("date")),
                    "conversation_id": conversation_id,
                    "folder": _compact(row.get("folder")),
                    "has_attachments": bool(row.get("has_attachments") or row.get("attachment_count")),
                    "candidate_kind": "body",
                    "attachment_filename": "",
                    "snippet": _best_body_text(dict(row))[:280],
                    "matched_query_lanes": list(seed.get("matched_query_lanes") or []),
                    "matched_query_queries": list(seed.get("matched_query_queries") or []),
                    "result_key": f"{uid}:thread_expansion",
                    "harvest_source": "thread_expansion",
                    "harvest_round": int(seed.get("harvest_round") or 0),
                    "verification_status": "thread_context",
                    "relevance_score": relevance_score,
                    **_email_language_fields(dict(row)),
                    "provenance": {
                        "evidence_handle": f"thread:{uid}:{conversation_id}",
                        "uid": uid,
                        "conversation_id": conversation_id,
                        "body_render_source": "thread_expansion",
                    },
                }
            )
            additions += 1
            if additions >= max_additions:
                break
    diagnostics["expanded_row_count"] = len(expanded)
    diagnostics["status"] = "partial" if int(diagnostics.get("error_count") or 0) > 0 else "ok"
    return expanded, diagnostics


def _attachment_expansion_rows(
    db: Any,
    *,
    evidence_bank: list[dict[str, Any]],
    exhaustive_review: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    diagnostics = _default_expansion_stage_diagnostics("attachment_expansion")
    if db is None or not hasattr(db, "attachments_for_email"):
        return [], diagnostics
    expanded: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in evidence_bank:
        uid = _compact(item.get("uid"))
        if not uid:
            continue
        diagnostics["attempted_count"] = int(diagnostics.get("attempted_count") or 0) + 1
        try:
            attachments = db.attachments_for_email(uid) or []
        except Exception as exc:  # pylint: disable=broad-exception-caught
            _expansion_error_entry(
                diagnostics,
                {
                    "uid": uid,
                    "seed_result_key": _compact(item.get("result_key")),
                    "error_type": type(exc).__name__,
                    "error": _compact(str(exc))[:240],
                },
            )
            continue
        relevance_terms = _seed_relevance_terms(item)
        ranked_attachments = sorted(
            [attachment for attachment in attachments if isinstance(attachment, dict)],
            key=lambda attachment, rt=relevance_terms: (
                -_text_overlap_score(
                    haystack=" ".join(
                        [
                            str(attachment.get("name") or ""),
                            str(attachment.get("extracted_text") or ""),
                            str(attachment.get("text_preview") or ""),
                            str((attachment.get("documentary_support") or {}).get("source_type_hint") or ""),
                        ]
                    ),
                    terms=rt,
                ),
                0 if not bool(attachment.get("is_inline")) else 1,
                0 if bool(_compact(attachment.get("extracted_text") or attachment.get("text_preview"))) else 1,
                0
                if _compact((attachment.get("documentary_support") or {}).get("source_type_hint"))
                in {"formal_document", "note_record", "participation_record", "time_record"}
                else 1,
                0 if _compact(attachment.get("name")).lower().endswith((".pdf", ".eml", ".ics", ".docx", ".txt")) else 1,
                _compact(attachment.get("name")).casefold(),
            ),
        )
        selected = []
        for attachment in ranked_attachments:
            if bool(attachment.get("is_inline")) and not _compact(
                attachment.get("extracted_text") or attachment.get("text_preview")
            ):
                continue
            selected.append(attachment)
            if len(selected) >= (5 if exhaustive_review else 3):
                break
        for attachment in selected:
            filename = _compact(attachment.get("name"))
            if not filename or (uid, filename) in seen:
                continue
            seen.add((uid, filename))
            relevance_score = _text_overlap_score(
                haystack=" ".join(
                    [
                        str(attachment.get("name") or ""),
                        str(attachment.get("extracted_text") or ""),
                        str(attachment.get("text_preview") or ""),
                    ]
                ),
                terms=relevance_terms,
            )
            snippet = _compact(attachment.get("extracted_text") or attachment.get("text_preview") or attachment.get("name"))
            expanded.append(
                {
                    "uid": uid,
                    "chunk_id": f"{uid}:attachment:{filename}",
                    "score": float(item.get("score") or 0.0) * (0.8 + min(relevance_score, 4) * 0.04),
                    "subject": _compact(item.get("subject")),
                    "sender_email": _compact(item.get("sender_email")),
                    "sender_name": _compact(item.get("sender_name")),
                    "date": _compact(item.get("date")),
                    "conversation_id": _compact(item.get("conversation_id")),
                    "folder": _compact(item.get("folder")),
                    "has_attachments": True,
                    "candidate_kind": "attachment",
                    "attachment_filename": filename,
                    "snippet": snippet[:280],
                    "matched_query_lanes": list(item.get("matched_query_lanes") or []),
                    "matched_query_queries": list(item.get("matched_query_queries") or []),
                    "result_key": f"{uid}:attachment:{filename}",
                    "harvest_source": "attachment_expansion",
                    "harvest_round": int(item.get("harvest_round") or 0),
                    "verification_status": "attachment_reference",
                    "relevance_score": relevance_score,
                    "attachment": {
                        "filename": filename,
                        "mime_type": _compact(attachment.get("mime_type")),
                        "evidence_strength": _compact(attachment.get("evidence_strength")) or "weak_reference",
                        "text_available": bool(_compact(attachment.get("extracted_text") or attachment.get("text_preview"))),
                    },
                    "detected_language": _compact(item.get("detected_language")),
                    "detected_language_confidence": _compact(item.get("detected_language_confidence")),
                    "provenance": {
                        "evidence_handle": f"attachment:{uid}:{filename}",
                        "uid": uid,
                        "attachment_filename": filename,
                        "body_render_source": "attachment_expansion",
                    },
                }
            )
    diagnostics["expanded_row_count"] = len(expanded)
    diagnostics["status"] = "partial" if int(diagnostics.get("error_count") or 0) > 0 else "ok"
    return expanded, diagnostics


__all__ = [
    "_attachment_expansion_rows",
    "_thread_expansion_rows",
]
