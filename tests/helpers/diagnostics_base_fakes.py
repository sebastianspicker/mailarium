"""Base dependency doubles shared by diagnostics-tool tests."""

from __future__ import annotations

import json
import sqlite3
from unittest.mock import MagicMock

from mailarium.mcp_server import _offload
from mailarium.sanitization import sanitize_untrusted_text


class SqliteConnectionOwner:
    """Own an optional SQLite test connection and close it safely."""

    conn = None

    def close(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:  # pylint: disable=broad-exception-caught
            pass


class ToolDependencyAnnotations:
    """Supply the standard offline ToolDeps annotations for test doubles."""

    offload = staticmethod(_offload)
    DB_UNAVAILABLE = json.dumps({"error": "SQLite database not available."})
    sanitize = staticmethod(sanitize_untrusted_text)

    @staticmethod
    def tool_annotations(title):
        return {"title": title}

    @staticmethod
    def write_tool_annotations(title):
        return {"title": title}

    @staticmethod
    def idempotent_write_annotations(title):
        return {"title": title}


class MockRetriever:
    """Minimal retriever stub with embedder attribute for diagnostics."""

    def __init__(self):
        """Implement the init behavior exposed by the MockRetriever test double."""
        self.embedder = MagicMock()
        self.embedder.device = "cpu"
        self.embedder._model = MagicMock()
        self.embedder.has_sparse = False
        self.embedder.runtime_summary.return_value = {
            "backend": "fake",
            "device": "cpu",
            "batch_size": 16,
            "load_mode": "local_only",
            "has_sparse": False,
        }


class MockEmailDB(SqliteConnectionOwner):
    """Test double carrying deterministic MockEmailDB state for focused unit tests."""

    def __init__(self):
        """Implement the init behavior exposed by the MockEmailDB test double."""
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def sparse_vector_count(self):
        """Implement the sparse vector count behavior exposed by the MockEmailDB test double."""
        return 42


class MockDeps(ToolDependencyAnnotations):
    """Test double carrying deterministic MockDeps state for focused unit tests."""

    _retriever = MockRetriever()
    _email_db = MockEmailDB()

    @staticmethod
    def get_retriever():
        """Implement the get retriever behavior exposed by the MockDeps test double."""
        return MockDeps._retriever

    @staticmethod
    def get_email_db():
        """Implement the get email db behavior exposed by the MockDeps test double."""
        return MockDeps._email_db
