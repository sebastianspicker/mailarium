"""QA-report fixtures shared by diagnostics-tool tests."""

from __future__ import annotations

import json

from .diagnostics_mcp_fakes import _register


def write_json_artifact(path, payload) -> None:
    """Write a deterministic JSON test artifact."""
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_diagnostics_report(path, summary) -> None:
    """Write one diagnostics QA-evaluation report."""
    write_json_artifact(path, {"summary": summary})


def standard_core_summary(**overrides):
    """Build the common core QA-evaluation summary used by specialized-report tests."""
    summary = {
        "total_cases": 10,
        "bucket_counts": {"fact_lookup": 4},
        "top_1_correctness": {"scorable": 10, "passed": 10, "failed": 0},
        "support_uid_hit_top_3": {"scorable": 10, "passed": 10, "failed": 0},
        "evidence_precision": {"scorable": 10, "average": 0.9},
        "attachment_answer_success": {"scorable": 0, "passed": 0, "failed": 0},
        "attachment_text_evidence_success": {"scorable": 0, "passed": 0, "failed": 0},
        "attachment_ocr_text_evidence_success": {"scorable": 0, "passed": 0, "failed": 0},
        "confidence_calibration_match": {"scorable": 10, "passed": 10, "failed": 0},
        "weak_evidence_explained": {"scorable": 0, "passed": 0, "failed": 0},
        "thread_group_id_match": {"scorable": 0, "passed": 0, "failed": 0},
        "thread_group_source_match": {"scorable": 0, "passed": 0, "failed": 0},
    }
    summary.update(overrides)
    return summary


async def answer_task_readiness(monkeypatch, report_paths, *, prevalence_paths=None):
    """Run diagnostics with the supplied report candidates and return its readiness summary."""
    from mailarium.mcp_models import EmailAdminInput
    from mailarium.tools import diagnostics

    fn = _register()._tools["email_admin"]
    monkeypatch.setattr(diagnostics, "_qa_eval_report_candidates", lambda: report_paths)
    if prevalence_paths is not None:
        monkeypatch.setattr(diagnostics, "_inferred_thread_prevalence_candidates", lambda: prevalence_paths)
    return json.loads(await fn(EmailAdminInput(action="diagnostics")))["answer_task_readiness"]
