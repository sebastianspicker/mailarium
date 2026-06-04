# mypy: disable-error-code=name-defined
# pylint: disable=too-many-arguments,too-many-branches,too-many-locals,too-many-statements


# pylint: disable=E0602  # cross-module names injected by compatibility facade
"""Split helpers for search answer-context runtime (search_answer_context_runtime_multi_lane)."""

from __future__ import annotations

import re
from typing import Any

from ..actor_resolution import resolve_actor_graph
from ..behavioral_evidence_chains import build_behavioral_evidence_chains
from ..behavioral_strength import apply_behavioral_strength
from ..case_intake import build_case_bundle
from ..communication_graph import build_communication_graph
from ..comparative_treatment import build_comparative_treatment
from ..cross_message_patterns import build_case_patterns
from ..formatting import weak_message_semantics
from ..investigation_report import build_investigation_report
from ..mcp_models import EmailAnswerContextInput
from ..multi_source_case_bundle import build_multi_source_case_bundle
from ..power_context import apply_power_context_to_actor_graph, build_power_context
from ..scan_session import filter_seen
from ..trigger_retaliation import build_retaliation_analysis
from . import search_answer_context_impl as impl
from .search_answer_context_budget import (
    _compact_snippets_for_budget,
    _compact_timeline_events,
    _dedupe_evidence_items,
    _estimated_json_chars,
    _reindex_evidence,
    _strip_optional_evidence_fields,
    _summarize_conversation_groups_for_budget,
    _summarize_timeline_for_budget,
    _weakest_evidence_target,
)
from .search_answer_context_case_payloads import _apply_actor_ids_to_candidates, _apply_actor_ids_to_case_bundle
from .search_answer_context_rendering import (
    _answer_policy,
    _answer_quality,
    _final_answer_contract,
    _render_final_answer,
    _resolve_exact_wording_requested,
)
from .search_answer_context_runtime_lanes import _segment_search_results
from .search_answer_context_runtime_payload import _compact_optional_case_surfaces, build_payload, rebuild_sections
from .search_answer_context_runtime_ranking import (
    _bank_entry,
    _evidence_bank_keys_with_lane_diversity,
    _evidence_bank_keys_with_support_diversity,
    _lane_expansion_terms,
    _lane_recovered_expansion_terms,
    _record_lane_match,
    _result_competition_key,
    _result_identity_key,
    _support_type_for_result,
)
from .search_answer_context_runtime_single_lane import (
    _apply_filter_seen,
    _build_evidence_bank,
    _build_lane_diagnostics_item,
    _compute_support_type_counts,
)
from .utils import ToolDepsProto, json_response

# ruff: noqa: F401


def _search_multi_lane(
    *,
    retriever: Any,
    search_kwargs: dict[str, Any],
    query_lanes: list[str],
    top_k: int,
    scan_id: str | None,
    lane_search_top_k: int,
    bank_limit: int,
    reserve_per_lane: int,
) -> tuple[list[Any], list[dict[str, Any]], dict[str, Any]]:
    lane_diagnostics: list[dict[str, Any]] = []
    exact_wording = bool(search_kwargs.get("_exact_wording_requested"))
    base_lane_query = str(query_lanes[0] or "")

    combined: dict[str, Any] = {}
    lane_hits: dict[str, list[str]] = {}
    lane_queries_by_key: dict[str, list[str]] = {}
    reserved_keys: list[str] = []
    for index, lane_query in enumerate(query_lanes, start=1):
        lane_id = f"lane_{index}"
        lane_initial_keys = set(combined.keys())
        lane_kwargs = {
            key: value
            for key, value in {**search_kwargs, "query": lane_query, "top_k": lane_search_top_k}.items()
            if not str(key).startswith("_")
        }
        lane_results = retriever.search_filtered(**lane_kwargs)
        raw_lane_results = lane_results if isinstance(lane_results, list) else []
        for result in raw_lane_results:
            key = _result_identity_key(result, fallback=lane_id)
            _record_lane_match(
                key=key,
                lane_id=lane_id,
                lane_query=lane_query,
                lane_hits=lane_hits,
                lane_queries_by_key=lane_queries_by_key,
            )
        lane_scan_meta: dict[str, Any] | None = None
        lane_results, lane_scan_meta = _apply_filter_seen(scan_id, lane_results)
        debug = dict(getattr(retriever, "last_search_debug", getattr(retriever, "_last_search_debug", None)) or {})
        executed_query = str(debug.get("executed_query") or lane_query)
        expansion_terms = _lane_expansion_terms(
            base_query=base_lane_query,
            lane_query=lane_query,
            executed_query=executed_query,
            query_expansion_suffix=str(debug.get("query_expansion_suffix") or ""),
        )
        segment_results, segment_diag = _segment_search_results(
            retriever=retriever,
            lane_query=lane_query,
            lane_id=lane_id,
            limit=max(4, min(bank_limit, lane_search_top_k // 2 or 4)),
            scan_id=scan_id,
        )
        lane_diagnostics.append(
            _build_lane_diagnostics_item(
                lane_id=lane_id,
                query=lane_query,
                executed_query=executed_query,
                results=lane_results,
                scan_id=scan_id,
                scan_meta=lane_scan_meta,
                lane_search_top_k=lane_search_top_k,
                expansion_terms=expansion_terms,
                debug=debug,
                segment_diag=segment_diag,
            )
        )
        lane_reserved_keys: list[str] = []
        for result in lane_results:
            key = _result_identity_key(result, fallback=lane_id)
            existing = combined.get(key)
            if existing is None or _result_competition_key(result, exact_wording=exact_wording) > _result_competition_key(
                existing,
                exact_wording=exact_wording,
            ):
                combined[key] = result
            if key not in lane_reserved_keys:
                lane_reserved_keys.append(key)
        for result in segment_results:
            key = _result_identity_key(result, fallback=lane_id)
            _record_lane_match(
                key=key,
                lane_id=lane_id,
                lane_query=lane_query,
                lane_hits=lane_hits,
                lane_queries_by_key=lane_queries_by_key,
            )
            existing = combined.get(key)
            if existing is None or _result_competition_key(result, exact_wording=exact_wording) > _result_competition_key(
                existing,
                exact_wording=exact_wording,
            ):
                combined[key] = result
            if key not in lane_reserved_keys:
                lane_reserved_keys.append(key)
        for key in lane_reserved_keys[: max(reserve_per_lane, 0)]:
            if key not in reserved_keys:
                reserved_keys.append(key)
        lane_new_keys = [key for key in combined if key not in lane_initial_keys]
        lane_diagnostics[-1]["new_key_count"] = len(lane_new_keys)
        recovered_terms, recovered_key_count = _lane_recovered_expansion_terms(
            expansion_terms=expansion_terms,
            new_keys=lane_new_keys,
            result_lookup=combined,
        )
        lane_diagnostics[-1]["recovered_expansion_terms"] = recovered_terms
        lane_diagnostics[-1]["recovered_expansion_key_count"] = recovered_key_count
    ranked = sorted(
        combined.items(), key=lambda item: _result_competition_key(item[1], exact_wording=exact_wording), reverse=True
    )
    merged_keys: list[str] = []
    for key in reserved_keys:
        if key in combined and key not in merged_keys:
            merged_keys.append(key)
        if len(merged_keys) >= top_k:
            break
    for key, _result in ranked:
        if key in merged_keys:
            continue
        merged_keys.append(key)
        if len(merged_keys) >= top_k:
            break
    merged = [combined[key] for key in merged_keys[:top_k]]
    for result in merged:
        metadata = result.metadata if isinstance(result.metadata, dict) else {}
        key = _result_identity_key(result, fallback="")
        metadata["matched_query_lanes"] = lane_hits.get(key, [])
        metadata["matched_query_queries"] = lane_queries_by_key.get(key, [])
    bank_keys = _evidence_bank_keys_with_lane_diversity(
        ranked=ranked,
        lane_hits=lane_hits,
        bank_limit=bank_limit,
        reserve_per_lane=reserve_per_lane,
    )
    bank_keys = _evidence_bank_keys_with_support_diversity(
        ranked=ranked,
        selected_keys=bank_keys,
        lane_queries_by_key=lane_queries_by_key,
        bank_limit=bank_limit,
    )
    evidence_bank = _build_evidence_bank(
        bank_keys=bank_keys,
        combined=combined,
        lane_hits=lane_hits,
        lane_queries_by_key=lane_queries_by_key,
    )
    support_type_counts = _compute_support_type_counts(
        bank_keys=bank_keys,
        combined=combined,
        lane_queries_by_key=lane_queries_by_key,
    )
    return (
        merged,
        lane_diagnostics,
        {
            "candidate_pool_count": len(ranked),
            "selected_result_count": len(merged),
            "lane_top_k": lane_search_top_k,
            "merge_budget": bank_limit,
            "reserved_per_lane": reserve_per_lane,
            "reserved_key_count": len(reserved_keys),
            "support_diversity": {
                "selected_support_types": sorted(support_type_counts.keys()),
                "counts_by_support_type": support_type_counts,
            },
            "expansion_attribution": [
                {
                    "lane_id": str(item.get("lane_id") or ""),
                    "query": str(item.get("query") or ""),
                    "new_key_count": int(item.get("new_key_count") or 0),
                    "expansion_terms": [str(term) for term in item.get("expansion_terms", []) if str(term).strip()],
                    "recovered_expansion_terms": [
                        str(term) for term in item.get("recovered_expansion_terms", []) if str(term).strip()
                    ],
                    "recovered_expansion_key_count": int(item.get("recovered_expansion_key_count") or 0),
                }
                for item in lane_diagnostics
                if isinstance(item, dict)
            ],
            "evidence_bank": evidence_bank,
            "evidence_results": [combined[key] for key in bank_keys],
        },
    )


__all__ = [
    "_search_multi_lane",
]
