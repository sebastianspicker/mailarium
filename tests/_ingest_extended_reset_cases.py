"""Derived vector-index reset tests."""

import argparse

from mailarium.email_db import EmailDatabase


class TestResetIndex:
    def test_reset_index_preserves_sqlite_and_deletes_derived_index(self, tmp_path, monkeypatch):
        from mailarium.ingest import _reset_index

        sqlite_file = tmp_path / "test.db"
        EmailDatabase(str(sqlite_file)).close()
        vector_index_dir = tmp_path / "vector-index"
        vector_index_dir.mkdir()
        (vector_index_dir / "data.bin").write_text("dummy", encoding="utf-8")
        args = argparse.Namespace(sqlite_path=str(sqlite_file), vector_index_path=str(vector_index_dir))
        _reset_index(args)
        assert sqlite_file.exists()
        assert not vector_index_dir.exists()

    def test_reset_index_handles_missing_files(self, tmp_path):
        from mailarium.ingest import _reset_index

        args = argparse.Namespace(
            sqlite_path=str(tmp_path / "nonexistent.db"), vector_index_path=str(tmp_path / "nonexistent_dir")
        )
        _reset_index(args)
