"""Structural tests for EmailDatabase persistence/enrichment extraction."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from mailarium.email_db import EmailDatabase, _update_v7_email_row
from tests._email_db_cases import _make_email


def test_insert_email_wrapper_delegates_to_helper() -> None:
    db = EmailDatabase(":memory:")
    email = _make_email()
    with patch("mailarium.email_db.insert_email_impl", return_value=True) as mock_impl:
        result = db.insert_email(email, ingestion_run_id=5)
    assert result is True
    mock_impl.assert_called_once_with(db, email, ingestion_run_id=5)
    db.close()


def test_insert_emails_batch_wrapper_delegates_to_helper() -> None:
    db = EmailDatabase(":memory:")
    emails = [_make_email(message_id="<m1@example.com>")]
    with patch("mailarium.email_db.insert_emails_batch_impl", return_value={"uid-1"}) as mock_impl:
        result = db.insert_emails_batch(emails, ingestion_run_id=9)
    assert result == {"uid-1"}
    mock_impl.assert_called_once_with(db, emails, ingestion_run_id=9)
    db.close()


def test_update_v7_email_row_delegates_parameter_ordering_to_builder() -> None:
    cur = MagicMock()
    cur.rowcount = 1
    email = SimpleNamespace(uid="email-1")
    update_row = (
        "categories",
        "topic",
        "classification",
        1,
        "references",
        "meeting",
        "links",
        "emails",
        "contacts",
        "meetings",
        "email-1",
    )

    with patch("mailarium.email_db.build_v7_email_update_row", return_value=update_row) as build_row:
        assert _update_v7_email_row(cur, email) is True

    build_row.assert_called_once_with(email)
    sql, parameters = cur.execute.call_args.args
    assert "WHERE uid = ?" in sql
    assert parameters is update_row
