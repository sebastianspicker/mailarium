"""Characterize the extracted evidence-candidate persistence seam."""

from __future__ import annotations

import json

import pytest

from mailarium.email_db import EmailDatabase
from tests._evidence_cases import make_email


def _candidate_values(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "run_id": "run-1",
        "phase_id": "phase-1",
        "wave_id": "wave-1",
        "wave_label": "Wave one",
        "question_ids": ["Q1"],
        "email_uid": "email-1",
        "candidate_kind": "body",
        "quote_candidate": "A precise quote",
        "summary": "Candidate summary",
        "category_hint": "fact",
        "rank": 1,
        "score": 0.9,
        "verification_status": "exact_verified",
        "verified_exact": True,
        "subject": "Subject",
        "sender_name": "Sender",
        "sender_email": "sender@example.test",
        "date": "2026-01-01",
        "conversation_id": "conversation-1",
        "matched_query_lanes": ["lane-1"],
        "matched_query_queries": ["query-1"],
        "provenance": {"evidence_handle": "handle-1"},
        "context": {"support_type": "primary"},
    }
    values.update(overrides)
    return values


def _insert_evidence_item(
    db: EmailDatabase,
    *,
    email_uid: str,
    key_quote: str,
    candidate_kind: str,
    document_locator: object,
) -> int:
    cur = db.conn.execute(
        """INSERT INTO evidence_items
           (email_uid, category, key_quote, summary, relevance, candidate_kind, document_locator_json)
           VALUES (?, 'fact', ?, 'summary', 1, ?, ?)""",
        (email_uid, key_quote, candidate_kind, document_locator),
    )
    db.conn.commit()
    assert cur.lastrowid is not None
    return int(cur.lastrowid)


def _seed_email(db: EmailDatabase, *, message_id: str) -> str:
    email = make_email(message_id=message_id)
    db.insert_email(email)
    return email.uid


def test_candidate_insert_dedup_and_phase_hash_preserve_payload_and_custody() -> None:
    db = EmailDatabase(":memory:")
    try:
        email_uid = _seed_email(db, message_id="<candidate-one@example.test>")
        first = db.add_evidence_candidate(**_candidate_values(email_uid=email_uid))
        duplicate = db.add_evidence_candidate(**_candidate_values(email_uid=email_uid))
        other_phase = db.add_evidence_candidate(**_candidate_values(email_uid=email_uid, phase_id="phase-2"))

        assert first["inserted"] is True
        assert duplicate == {**first, "inserted": False}
        assert other_phase["inserted"] is True
        assert first["content_hash"] != other_phase["content_hash"]
        assert first["status"] == "harvested"
        assert first["promoted_evidence_id"] is None
        assert json.loads(first["question_ids_json"]) == ["Q1"]
        assert json.loads(first["provenance_json"]) == {"evidence_handle": "handle-1"}
        assert json.loads(first["context_json"]) == {"support_type": "primary"}
        custody = db.get_custody_chain(target_type="evidence_candidate", target_id=str(first["id"]))
        assert custody == [
            {
                **custody[0],
                "action": "evidence_candidate_add",
                "target_type": "evidence_candidate",
                "target_id": str(first["id"]),
                "details": {
                    "run_id": "run-1",
                    "phase_id": "phase-1",
                    "wave_id": "wave-1",
                    "candidate_kind": "body",
                    "email_uid": email_uid,
                    "verified_exact": True,
                },
            }
        ]
        assert db.evidence_candidate_stats(run_id="run-1") == {
            "total": 2,
            "body_candidates": 2,
            "attachments": 0,
            "exact_body_candidates": 2,
            "promoted": 0,
            "by_wave": [{"wave_id": "wave-1", "total": 2, "promoted": 0, "exact_body_candidates": 2}],
            "by_status": [{"status": "harvested", "count": 2}],
        }
    finally:
        db.close()


def test_candidate_insert_rolls_back_row_when_custody_logging_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    db = EmailDatabase(":memory:")
    try:
        email_uid = _seed_email(db, message_id="<candidate-rollback@example.test>")

        def fail_custody(*_args: object, **_kwargs: object) -> int:
            raise RuntimeError("custody failure")

        monkeypatch.setattr(db, "log_custody_event", fail_custody)

        with pytest.raises(RuntimeError, match="custody failure"):
            db.add_evidence_candidate(**_candidate_values(email_uid=email_uid))

        assert db.conn.execute("SELECT COUNT(*) FROM evidence_candidates").fetchone()[0] == 0
    finally:
        db.close()


def test_candidate_promotion_updates_lifecycle_and_stats() -> None:
    db = EmailDatabase(":memory:")
    try:
        email_uid = _seed_email(db, message_id="<candidate-promotion@example.test>")
        evidence_id = _insert_evidence_item(
            db,
            email_uid=email_uid,
            key_quote="Promoted evidence",
            candidate_kind="body",
            document_locator="{}",
        )
        candidate = db.add_evidence_candidate(
            **_candidate_values(email_uid=email_uid, candidate_kind="attachment", verified_exact=False)
        )

        assert db.mark_evidence_candidate_promoted(candidate["id"], evidence_id=evidence_id) is True
        assert db.mark_evidence_candidate_promoted(999, evidence_id=evidence_id) is False
        row = db.conn.execute(
            "SELECT status, promoted_evidence_id FROM evidence_candidates WHERE id = ?", (candidate["id"],)
        ).fetchone()
        assert dict(row) == {"status": "promoted", "promoted_evidence_id": evidence_id}
        assert db.evidence_candidate_stats(run_id="run-1")["promoted"] == 1
        custody = db.get_custody_chain(target_type="evidence_candidate", target_id=str(candidate["id"]))
        promoted_event = next(event for event in custody if event["action"] == "evidence_candidate_promote")
        assert promoted_event["details"] == {"evidence_id": evidence_id}
    finally:
        db.close()


def test_candidate_quote_matching_preserves_casefolded_artifact_identity_rules() -> None:
    db = EmailDatabase(":memory:")
    try:
        email_one = _seed_email(db, message_id="<quote-one@example.test>")
        email_two = _seed_email(db, message_id="<quote-two@example.test>")
        quote_id = _insert_evidence_item(
            db,
            email_uid=email_one,
            key_quote="A Precise Quote",
            candidate_kind="body",
            document_locator=json.dumps({"segment_type": "body", "segment_ordinal": 1}),
        )
        conflicting_attachment_id = _insert_evidence_item(
            db,
            email_uid=email_one,
            key_quote="A Precise Quote",
            candidate_kind="attachment",
            document_locator=json.dumps({"attachment_id": "other-file"}),
        )
        attachment_id = _insert_evidence_item(
            db,
            email_uid=email_one,
            key_quote="A Precise Quote",
            candidate_kind="attachment",
            document_locator=json.dumps({"attachment_id": "file-1", "attachment_filename": "Letter.PDF"}),
        )
        legacy_id = _insert_evidence_item(
            db,
            email_uid=email_two,
            key_quote="Legacy Quote",
            candidate_kind="body",
            document_locator="not-json",
        )

        assert db.find_evidence_by_email_quote(email_uid=email_one, key_quote="a precise quote")["id"] == quote_id
        assert (
            db.find_evidence_by_email_artifact_quote(
                email_uid=f" {email_one} ",
                key_quote=" a precise quote ",
                candidate_kind="body",
                document_locator={"segment_type": " BODY ", "segment_ordinal": "1"},
            )["id"]
            == quote_id
        )
        assert (
            db.find_evidence_by_email_artifact_quote(
                email_uid=email_one,
                key_quote="a precise quote",
                candidate_kind="attachment",
                document_locator={"attachment_id": "FILE-1", "attachment_filename": "letter.pdf"},
            )["id"]
            == attachment_id
        )
        assert (
            db.find_evidence_by_email_artifact_quote(
                email_uid=email_one,
                key_quote="a precise quote",
                candidate_kind="attachment",
                document_locator={"attachment_id": "missing-file"},
            )
            is None
        )
        assert (
            db.find_evidence_by_email_artifact_quote(
                email_uid=email_two,
                key_quote="legacy quote",
                candidate_kind="body",
            )["id"]
            == legacy_id
        )
        assert conflicting_attachment_id < attachment_id
    finally:
        db.close()
