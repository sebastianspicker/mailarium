"""Retriever archive-summary and SQLite aggregate behavior."""

from unittest.mock import MagicMock

import pytest

from tests.helpers.retriever_cases import _bare_retriever


class TestListSendersSqlite:
    def test_uses_sqlite_when_available(self):
        r = _bare_retriever()
        mock_db = MagicMock()
        mock_db.top_senders.return_value = [
            {"sender_name": "Alice", "sender_email": "alice@example.test", "message_count": 10},
        ]
        r._email_db = mock_db
        r._email_db_checked = True

        senders = r.list_senders(limit=5)
        assert senders == [{"name": "Alice", "email": "alice@example.test", "count": 10}]

    def test_falls_back_to_vector_collection_when_sqlite_fails(self):
        r = _bare_retriever()
        mock_db = MagicMock()
        mock_db.top_senders.side_effect = RuntimeError("db error")
        r._email_db = mock_db
        r._email_db_checked = True

        class FakeCollection:
            def get(self, include, limit, offset):
                if offset == 0:
                    return {
                        "metadatas": [
                            {"uid": "u1", "sender_email": "bob@example.test", "sender_name": "Bob"},
                        ]
                    }
                return {"metadatas": []}

        r.collection = FakeCollection()

        senders = r.list_senders(limit=5)
        assert len(senders) == 1
        assert senders[0]["email"] == "bob@example.test"

    def test_rejects_too_large_limit(self):
        r = _bare_retriever()
        with pytest.raises(ValueError, match="10000"):
            r.list_senders(limit=10001)

    def test_empty_collection_returns_empty(self):
        r = _bare_retriever()

        class FakeCollection:
            def get(self, include, limit, offset):
                return {"metadatas": []}

        r.collection = FakeCollection()

        senders = r.list_senders(limit=5)
        assert senders == []


def test_list_folders_returns_folder_counts():
    r = _bare_retriever()
    r.stats = MagicMock(return_value={"folders": {"Inbox": 10, "Sent": 5}})
    folders = r.list_folders()
    assert {"folder": "Inbox", "count": 10} in folders
    assert {"folder": "Sent", "count": 5} in folders


class TestStatsSqlite:
    def test_uses_sqlite_when_available(self):
        r = _bare_retriever()
        r.collection = MagicMock()
        r.collection.count.return_value = 100

        mock_db = MagicMock()
        mock_db.email_count.return_value = 50
        mock_db.date_range.return_value = ("2023-01-01T00:00:00", "2024-12-31T00:00:00")
        mock_db.unique_sender_count.return_value = 15
        mock_db.folder_counts.return_value = {"Inbox": 30, "Sent": 20}
        r._email_db = mock_db
        r._email_db_checked = True

        stats = r.stats()
        assert stats["total_chunks"] == 100
        assert stats["total_emails"] == 50
        assert stats["unique_senders"] == 15
        assert stats["date_range"]["earliest"] == "2023-01-01"
        assert stats["date_range"]["latest"] == "2024-12-31"
        assert stats["folders"]["Inbox"] == 30

    def test_falls_back_when_sqlite_raises(self):
        r = _bare_retriever()
        r.collection = MagicMock()
        r.collection.count.return_value = 0

        mock_db = MagicMock()
        mock_db.email_count.side_effect = RuntimeError("db error")
        r._email_db = mock_db
        r._email_db_checked = True

        stats = r.stats()
        assert stats["total_emails"] == 0

    def test_falls_back_when_sqlite_email_count_zero(self):
        r = _bare_retriever()
        r.collection = MagicMock()
        r.collection.count.return_value = 0

        mock_db = MagicMock()
        mock_db.email_count.return_value = 0
        r._email_db = mock_db
        r._email_db_checked = True

        stats = r.stats()
        assert stats["total_emails"] == 0


def test_stats_empty_collection_without_db():
    r = _bare_retriever()
    r.collection = MagicMock()
    r.collection.count.return_value = 0

    stats = r.stats()
    assert stats == {
        "total_chunks": 0,
        "total_emails": 0,
        "unique_senders": 0,
        "date_range": {},
        "folders": {},
        "metadata_source": "vector_collection_fallback",
    }


def test_stats_vector_collection_counts_unknown_uid_rows():
    r = _bare_retriever()

    class FakeCollection:
        def count(self):
            return 3

        def get(self, include, limit, offset):
            if offset == 0:
                return {
                    "metadatas": [
                        {"sender_email": "a@example.test", "date": "2023-01-01", "folder": "Inbox"},
                        {"sender_email": "b@example.test", "date": "2023-06-01", "folder": "Sent"},
                        {"sender_email": "a@example.test", "date": "2023-12-01", "folder": "Inbox"},
                    ]
                }
            return {"metadatas": []}

    r.collection = FakeCollection()

    stats = r.stats()
    assert stats["total_emails"] == 3
    assert stats["unique_senders"] == 2
    assert stats["folders"]["Inbox"] == 2
    assert stats["folders"]["Sent"] == 1
