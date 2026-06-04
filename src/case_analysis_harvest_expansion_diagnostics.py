# mypy: disable-error-code=name-defined
# pylint: disable=E0602  # cross-module names injected by compatibility facade
"""Split archive-harvest helpers (case_analysis_harvest_expansion_diagnostics)."""

from __future__ import annotations

from typing import Any

from .case_analysis_harvest_common import _EXPANSION_ERROR_SAMPLE_LIMIT


def _default_expansion_stage_diagnostics(stage: str) -> dict[str, Any]:
    return {
        "stage": stage,
        "status": "ok",
        "attempted_count": 0,
        "expanded_row_count": 0,
        "error_count": 0,
        "errors": [],
    }


def _coerce_expansion_stage_result(
    result: Any,
    *,
    stage: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]]
    diagnostics = _default_expansion_stage_diagnostics(stage)
    if isinstance(result, tuple) and len(result) == 2:
        result_rows = result[0]
        result_diagnostics = result[1]
        rows = [item for item in result_rows if isinstance(item, dict)] if isinstance(result_rows, list) else []
        if isinstance(result_diagnostics, dict):
            diagnostics = {
                **diagnostics,
                **result_diagnostics,
            }
            diagnostics["errors"] = [
                item for item in list(diagnostics.get("errors") or [])[:_EXPANSION_ERROR_SAMPLE_LIMIT] if isinstance(item, dict)
            ]
            diagnostics["error_count"] = int(diagnostics.get("error_count") or len(diagnostics["errors"]))
            diagnostics["attempted_count"] = int(diagnostics.get("attempted_count") or 0)
            diagnostics["expanded_row_count"] = int(diagnostics.get("expanded_row_count") or len(rows))
            diagnostics["status"] = "partial" if int(diagnostics.get("error_count") or 0) > 0 else "ok"
            return rows, diagnostics
        diagnostics["expanded_row_count"] = len(rows)
        return rows, diagnostics
    rows = [item for item in result if isinstance(item, dict)] if isinstance(result, list) else []
    diagnostics["expanded_row_count"] = len(rows)
    return rows, diagnostics


def _aggregate_expansion_diagnostics(rounds: list[dict[str, Any]]) -> dict[str, Any]:
    normalized_rounds = [round_entry for round_entry in rounds if isinstance(round_entry, dict)]
    thread_error_count = sum(
        int((round_entry.get("thread_expansion") or {}).get("error_count") or 0) for round_entry in normalized_rounds
    )
    attachment_error_count = sum(
        int((round_entry.get("attachment_expansion") or {}).get("error_count") or 0) for round_entry in normalized_rounds
    )
    total_error_count = thread_error_count + attachment_error_count
    return {
        "status": "partial" if total_error_count > 0 else "ok",
        "error_count": total_error_count,
        "thread_expansion_error_count": thread_error_count,
        "attachment_expansion_error_count": attachment_error_count,
        "rounds": normalized_rounds,
    }


__all__ = [
    "_aggregate_expansion_diagnostics",
    "_coerce_expansion_stage_result",
    "_default_expansion_stage_diagnostics",
]
