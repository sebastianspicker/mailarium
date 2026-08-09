"""Characterization tests for email database persistence row builders."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from mailarium.email_db import EmailDatabase
from mailarium.email_db_persistence import build_v7_email_update_row

from ._email_db_cases import _make_email


def test_build_v7_email_update_row_preserves_column_order_and_serialization() -> None:
    email = SimpleNamespace(
        uid="email-1",
        categories=["Grün"],
        thread_topic="Budget",
        inference_classification="internal",
        is_calendar_message=True,
        references=["Référence"],
        meeting_data={"Ort": "München"},
        exchange_extracted_links=[{"url": "https://example.test/über"}],
        exchange_extracted_emails=["élise@example.test"],
        exchange_extracted_contacts=["Jürgen"],
        exchange_extracted_meetings=[{"subject": "Überblick"}],
    )

    assert build_v7_email_update_row(email) == (
        '["Gr\\u00fcn"]',
        "Budget",
        "internal",
        1,
        '["R\\u00e9f\\u00e9rence"]',
        '{"Ort": "München"}',
        '[{"url": "https://example.test/über"}]',
        '["élise@example.test"]',
        '["Jürgen"]',
        '[{"subject": "Überblick"}]',
        "email-1",
    )


def test_build_v7_email_update_row_uses_falsey_defaults() -> None:
    email = SimpleNamespace(
        uid="email-1",
        categories={},
        thread_topic=0,
        inference_classification=None,
        is_calendar_message=False,
        references={},
        meeting_data=None,
        exchange_extracted_links=None,
        exchange_extracted_emails=None,
        exchange_extracted_contacts=None,
        exchange_extracted_meetings=None,
    )

    assert build_v7_email_update_row(email) == ("[]", "", "", 0, "[]", "{}", "[]", "[]", "[]", "[]", "email-1")


def test_update_v7_metadata_returns_false_before_replacing_related_rows_for_unknown_uid() -> None:
    db = EmailDatabase(":memory:")
    email = _make_email(categories=["Finance"], attachments=[{"name": "report.pdf"}])

    with (
        patch("mailarium.email_db._replace_v7_categories") as replace_categories,
        patch("mailarium.email_db._replace_v7_attachments") as replace_attachments,
    ):
        assert db.update_v7_metadata(email) is False

    replace_categories.assert_not_called()
    replace_attachments.assert_not_called()
    db.close()


def test_update_v7_metadata_commit_false_leaves_transaction_to_caller() -> None:
    db = EmailDatabase(":memory:")
    email = _make_email(categories=["Original"])
    db.insert_email(email)

    email.categories = ["Replacement"]
    assert db.update_v7_metadata(email, commit=False) is True
    db.conn.rollback()

    row = db.conn.execute("SELECT categories FROM emails WHERE uid = ?", (email.uid,)).fetchone()
    categories = db.conn.execute("SELECT category FROM email_categories WHERE email_uid = ?", (email.uid,)).fetchall()
    assert row is not None
    assert row["categories"] == '["Original"]'
    assert [category["category"] for category in categories] == ["Original"]
    db.close()
