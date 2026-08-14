"""SQLite-backed email database doubles for MCP tool tests."""

from __future__ import annotations

import sqlite3

from .diagnostics_fakes import SqliteConnectionOwner


def close_sqlite_connection(owner) -> None:
    """Close the optional SQLite connection held by an in-memory test double."""
    if owner.conn is not None:
        owner.conn.close()
        owner.conn = None


class MockEmailDB(SqliteConnectionOwner):
    """Minimal email database stub with an in-memory SQLite connection."""

    def __init__(self):
        """Implement the init behavior exposed by the MockEmailDB test double."""
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(
            "CREATE TABLE emails ("
            "uid TEXT PRIMARY KEY, subject TEXT, sender_email TEXT, "
            "sender_name TEXT, date TEXT, body_text TEXT, "
            "conversation_id TEXT, folder TEXT, forensic_body_text TEXT, "
            "forensic_body_source TEXT, "
            "normalized_body_source TEXT, "
            "body_kind TEXT, body_empty_reason TEXT, recovery_strategy TEXT, recovery_confidence REAL, "
            "in_reply_to TEXT, references_json TEXT, "
            "inferred_parent_uid TEXT, inferred_thread_id TEXT, "
            "inferred_match_reason TEXT, inferred_match_confidence REAL, "
            "detected_language TEXT, detected_language_confidence TEXT, "
            "detected_language_reason TEXT, detected_language_token_count INTEGER, "
            "detected_language_source TEXT, sentiment_label TEXT, sentiment_score REAL, "
            "ingestion_run_id TEXT)"
        )
        self.conn.execute(
            """INSERT INTO emails VALUES (
                'uid-1', 'Budget Review', 'employee@example.test', 'Alice',
                '2025-06-01', 'We decided to go with vendor A.', 'conv-1', 'Inbox',
                'Full forensic body for uid-1.', 'forensic_body_text', 'body_text',
                'content', '', '', 1.0, '', '[]', '', '', '', 0.0,
                'en', 'high', 'stopword_overlap', 8, 'forensic_body_text', 'positive', 0.85, 'run-1'
            )"""
        )
        self.conn.execute(
            """INSERT INTO emails VALUES (
                'uid-2', 'Budget Review', 'bob@example.com', 'Bob',
                '2025-06-02', 'Please send the updated report by Friday.', 'conv-1', 'Inbox',
                'Full forensic body for uid-2.', 'forensic_body_text',
                'body_text_html', 'content', '', '', 1.0,
                'budget-parent@example.com', '["budget-root@example.com", "budget-parent@example.com"]',
                'uid-1', 'conv-1', 'base_subject,participants', 0.91,
                'en', 'medium', 'stopword_overlap', 7, 'forensic_body_text', 'neutral', 0.50, 'run-1'
            )"""
        )
        self.conn.execute(
            "CREATE TABLE message_segments ("
            "email_uid TEXT, ordinal INTEGER, segment_type TEXT, depth INTEGER, "
            "text TEXT, source_surface TEXT, provenance_json TEXT)"
        )
        self.conn.execute(
            "CREATE TABLE attachments ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, email_uid TEXT, name TEXT, "
            "mime_type TEXT, size INTEGER, content_id TEXT, is_inline INTEGER)"
        )
        self.conn.execute(
            "INSERT INTO message_segments VALUES "
            "('uid-1', 0, 'authored_body', 0, 'We decided to go with vendor A.', 'body_text', '{}')"
        )
        self.conn.execute(
            "INSERT INTO message_segments VALUES "
            "('uid-1', 1, 'quoted_reply', 1, 'Can you send the updated report?', 'body_text', '{}')"
        )
        self.conn.execute(
            "INSERT INTO attachments (email_uid, name, mime_type, size, content_id, is_inline) VALUES "
            "('uid-1', 'budget.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 2048, '', 0)"
        )
        self.conn.commit()

    def get_email_full(self, uid):
        """Implement the get email full behavior exposed by the MockEmailDB test double."""
        row = self.conn.execute("SELECT * FROM emails WHERE uid = ?", (uid,)).fetchone()
        if not row:
            return None
        return dict(row)

    def get_thread_emails(self, conversation_id):
        """Implement the get thread emails behavior exposed by the MockEmailDB test double."""
        rows = self.conn.execute(
            "SELECT * FROM emails WHERE conversation_id = ? ORDER BY date",
            (conversation_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def list_emails_paginated(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, offset=0, limit=10, folder=None, sender=None, category=None, sort_order="DESC", date_from=None, date_to=None
    ):
        """Implement the list emails paginated behavior exposed by the MockEmailDB test double."""
        return {
            "emails": [
                {"uid": "uid-1", "subject": "Budget Review", "sender_email": "employee@example.test", "date": "2025-06-01"},
            ],
            "total": 1,
            "offset": offset,
            "limit": limit,
        }

    def get_emails_full_batch(self, uids):
        """Implement the get emails full batch behavior exposed by the MockEmailDB test double."""
        result = {}
        for uid in uids:
            full = self.get_email_full(uid)
            if full:
                result[uid] = full
        return result

    def attachments_for_email(self, uid):
        """Implement the attachments for email behavior exposed by the MockEmailDB test double."""
        rows = self.conn.execute(
            "SELECT name, mime_type, size, content_id, is_inline FROM attachments WHERE email_uid = ?",
            (uid,),
        ).fetchall()
        return [dict(r) for r in rows]

    def list_evidence(self, email_uid=None, limit=50):
        """Implement the list evidence behavior exposed by the MockEmailDB test double."""
        return {"items": []}

    def top_contacts(self, email, limit=5):
        """Implement the top contacts behavior exposed by the MockEmailDB test double."""
        return [{"email": "bob@example.com", "count": 5}]

    def category_counts(self):
        """Implement the category counts behavior exposed by the MockEmailDB test double."""
        return [{"category": "Meeting", "count": 3}]

    def calendar_emails(self, date_from=None, date_to=None, limit=10):
        """Implement the calendar emails behavior exposed by the MockEmailDB test double."""
        return [{"uid": "uid-1", "subject": "Calendar Invite", "date": "2025-06-01"}]

    def thread_by_topic(self, topic, limit=50):
        """Implement the thread by topic behavior exposed by the MockEmailDB test double."""
        return [{"uid": "uid-1", "subject": "Budget Review", "date": "2025-06-01"}]

    def top_senders(self, limit=10):
        """Implement the top senders behavior exposed by the MockEmailDB test double."""
        return [{"sender_email": "employee@example.test", "count": 10}]
