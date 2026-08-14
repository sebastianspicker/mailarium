"""SQLite database fixtures shared by diagnostics-tool tests."""

from __future__ import annotations

import sqlite3

from .diagnostics_base_fakes import SqliteConnectionOwner


def diagnostics_database(email_schema, email_rows):
    """Create a closed-by-default diagnostics DB with common segment fixtures."""
    database = SqliteConnectionOwner()
    database.conn = sqlite3.connect(":memory:", check_same_thread=False)
    database.conn.row_factory = sqlite3.Row
    database.conn.execute(f"CREATE TABLE emails ({email_schema})")
    database.conn.execute("CREATE TABLE message_segments (email_uid TEXT)")
    placeholders = ", ".join("?" for _ in email_rows[0])
    database.conn.executemany(f"INSERT INTO emails VALUES ({placeholders})", email_rows)
    database.conn.executemany("INSERT INTO message_segments VALUES (?)", [("u1",), ("u1",), ("u2",)])
    database.sparse_vector_count = lambda: 0
    return database
