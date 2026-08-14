"""Retriever index-reset and SQLite metadata lifecycle behavior."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from mailarium.retriever import EmailRetriever
from tests.helpers.retriever_cases import _bare_retriever


def test_reset_index(tmp_path):
    r = _bare_retriever()
    r.collection = MagicMock()
    r.image_collection = MagicMock()
    r.reset_index()
    r.collection.reset.assert_called_once()
    r.image_collection.reset.assert_called_once()


def test_email_db_returns_none_when_no_sqlite_path():
    r = EmailRetriever.__new__(EmailRetriever)
    r._email_db_checked = False
    r._email_db = None
    r.settings = MagicMock()
    r.settings.sqlite_path = None

    assert r.email_db is None
    assert r._email_db_checked is True


def test_email_db_returns_none_when_path_doesnt_exist():
    r = EmailRetriever.__new__(EmailRetriever)
    r._email_db_checked = False
    r._email_db = None
    r.settings = MagicMock()
    r.settings.sqlite_path = "/nonexistent/path/db.sqlite"

    assert r.email_db is None
    assert r._email_db_checked is True


def test_email_db_rechecks_when_sqlite_appears_later(tmp_path):
    r = EmailRetriever.__new__(EmailRetriever)
    r._email_db_checked = False
    r._email_db = None
    r.settings = MagicMock()
    r.settings.sqlite_path = str(tmp_path / "email_metadata.db")

    assert r.email_db is None

    db_path = Path(r.settings.sqlite_path)
    db_path.touch()

    with patch("mailarium.email_db.EmailDatabase") as mock_db:
        assert r.email_db is mock_db.return_value

    mock_db.assert_called_once_with(str(db_path))
