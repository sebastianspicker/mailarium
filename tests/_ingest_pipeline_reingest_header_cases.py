"""Force and non-force header behavior for body reingestion."""

from .helpers.ingest_fixtures import _make_header_email, _seed_ingest_database


def test_reingest_force_updates_headers(monkeypatch, tmp_path):
    """--reingest-bodies --force should update subject, sender_name, sender_email."""
    import mailarium.ingest as ingest_mod
    from mailarium.email_db import EmailDatabase
    from mailarium.parse_olm import Email

    # First ingest: store emails with MIME-encoded subject and sender name.
    encoded_emails = [
        Email(
            message_id="<msg1@example.test>",
            subject="=?iso-8859-1?Q?Caf=E9?=",
            sender_name="=?utf-8?B?TMO8ZGVy?=",
            sender_email="old@example.test",
            to=["r@example.test"],
            cc=[],
            bcc=[],
            date="2024-01-01T10:00:00",
            body_text="Old body",
            body_html="",
            folder="Inbox",
            has_attachments=False,
        )
    ]
    _, sqlite_file = _seed_ingest_database(monkeypatch, tmp_path, encoded_emails)

    # Verify encoded values were stored as-is (simulating old parser without decode).
    db = EmailDatabase(sqlite_file)
    row = db.conn.execute("SELECT subject, sender_name, sender_email FROM emails").fetchone()
    assert row["subject"] == "=?iso-8859-1?Q?Caf=E9?="
    db.close()

    # Now simulate re-parse with decoded values (as the fixed parser would produce).
    decoded_emails = [
        _make_header_email(subject="Café", sender_name="Lüder", sender_email="new@example.test", body_text="New body")
    ]
    monkeypatch.setattr(ingest_mod, "parse_olm", lambda _path, **_kw: decoded_emails)

    result = ingest_mod.reingest_bodies("mock.olm", sqlite_path=sqlite_file, force=True)
    assert result["updated"] == 1

    db = EmailDatabase(sqlite_file)
    row = db.conn.execute("SELECT subject, sender_name, sender_email, base_subject, email_type FROM emails").fetchone()
    assert row["subject"] == "Café"
    assert row["sender_name"] == "Lüder"
    assert row["sender_email"] == "new@example.test"
    assert row["base_subject"] == "Café"
    assert row["email_type"] == "original"
    db.close()


def test_reingest_no_force_skips_headers(monkeypatch, tmp_path):
    """Without --force, reingest should NOT update headers (only missing bodies)."""
    import mailarium.ingest as ingest_mod
    from mailarium.email_db import EmailDatabase
    from mailarium.parse_olm import Email

    emails = [
        Email(
            message_id="<msg1@example.test>",
            subject="=?utf-8?Q?encoded?=",
            sender_name="Old Name",
            sender_email="old@example.test",
            to=["r@example.test"],
            cc=[],
            bcc=[],
            date="2024-01-01T10:00:00",
            body_text="Body text",
            body_html="",
            folder="Inbox",
            has_attachments=False,
        )
    ]
    _, sqlite_file = _seed_ingest_database(monkeypatch, tmp_path, emails)

    # Non-force reingest: all bodies present → nothing to do, headers untouched.
    decoded_emails = [
        _make_header_email(subject="decoded", sender_name="New Name", sender_email="new@example.test", body_text="New body")
    ]
    monkeypatch.setattr(ingest_mod, "parse_olm", lambda _path, **_kw: decoded_emails)

    result = ingest_mod.reingest_bodies("mock.olm", sqlite_path=sqlite_file, force=False)
    assert result["updated"] == 0  # nothing missing

    db = EmailDatabase(sqlite_file)
    row = db.conn.execute("SELECT subject, sender_name FROM emails").fetchone()
    assert row["subject"] == "=?utf-8?Q?encoded?="  # unchanged
    assert row["sender_name"] == "Old Name"  # unchanged
    db.close()
