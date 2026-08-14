"""Ensures QA fixtures remain synthetic and retain stable UID provenance."""

from __future__ import annotations

import hashlib
import json

from .helpers.repo_contracts import REPO_ROOT, _read


def test_generic_captured_eval_sets_include_grounding_and_negative_controls() -> None:
    core = json.loads(_read("tests/fixtures/qa_eval/qa_eval_questions.core.json"))["cases"]

    assert any(case.get("expected_support_source_ids") for case in core)
    assert any(case.get("expected_answer_terms") for case in core)
    assert any(case.get("forbidden_support_uids") or case.get("forbidden_support_source_ids") for case in core)


def test_qa_eval_fixtures_have_explicit_authored_synthetic_provenance() -> None:
    provenance = _read("tests/fixtures/qa_eval/PROVENANCE.md")
    core_payload = json.loads(_read("tests/fixtures/qa_eval/qa_eval_questions.core.json"))
    fixture_text = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted((REPO_ROOT / "tests/fixtures/qa_eval").glob("*.json"))
    )

    assert "intentionally authored synthetic regression data" in provenance
    assert "No operator mailbox export" in provenance
    assert "outlook-email-rag-alpha:<scenario-name>" in provenance
    uid_manifest = core_payload["uid_seed_manifest"]
    assert uid_manifest == {
        seed: hashlib.sha256(f"outlook-email-rag-alpha:{seed}".encode()).hexdigest()[:32] for seed in uid_manifest
    }
    referenced_uids = {
        uid
        for case in core_payload["cases"]
        for uid in (*case.get("expected_support_uids", []), case.get("expected_top_uid"))
        if uid
    }
    assert referenced_uids == set(uid_manifest.values())
    for stale_marker in (
        "HARICA",
        "Apple Support notes",
        "ticket system Reboot 2026",
        "Configurator 2 Blueprints",
        "891648cc4954152190a269112d54912e",
        "2606da536f3e533033cd6c2a8544f3a3",
    ):
        assert stale_marker not in fixture_text
