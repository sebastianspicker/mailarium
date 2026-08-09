# ruff: noqa: I001
"""Reingestion and re-embedding ingestion edge cases."""

from mailarium.ingest import reembed, reingest_analytics, reingest_bodies, reingest_metadata

from .helpers.ingest_extended_fixtures import _MockEmbedder, _make_email
from .helpers.ingest_fixtures import _seed_ingest_database


class TestReingestBodiesEdgeCases:
    def test_force_empty_db(self, monkeypatch, tmp_path):
        from mailarium.email_db import EmailDatabase

        sqlite_file = str(tmp_path / "test.db")
        db = EmailDatabase(sqlite_file)
        db.close()

        result = reingest_bodies("mock.olm", sqlite_path=sqlite_file, force=True)
        assert result["updated"] == 0
        assert "No emails" in result["message"]

    def test_non_force_with_missing_bodies(self, monkeypatch, tmp_path):
        """Non-force reingest should update only emails with NULL body_text."""
        from mailarium.email_db import EmailDatabase

        email = _make_email(1)
        ingest_mod, sqlite_file = _seed_ingest_database(monkeypatch, tmp_path, [email], embedder_cls=_MockEmbedder)
        db = EmailDatabase(sqlite_file)
        db.conn.execute("UPDATE emails SET body_text = NULL")
        db.conn.commit()
        db.close()

        monkeypatch.setattr(ingest_mod, "parse_olm", lambda _path, **_kw: [email])
        result = reingest_bodies("mock.olm", sqlite_path=sqlite_file, force=False)
        assert result["updated"] == 1

    def test_force_with_progress_logging(self, monkeypatch, tmp_path):
        """Force reingest with >100 emails should trigger progress logging."""
        emails = [_make_email(i) for i in range(1, 5)]
        ingest_mod, sqlite_file = _seed_ingest_database(monkeypatch, tmp_path, emails, embedder_cls=_MockEmbedder)
        monkeypatch.setattr(ingest_mod, "parse_olm", lambda _path, **_kw: emails)
        result = reingest_bodies("mock.olm", sqlite_path=sqlite_file, force=True)
        assert result["updated"] == 4


class TestReingestMetadataEdgeCases:
    def test_empty_db(self, tmp_path):
        from mailarium.email_db import EmailDatabase

        sqlite_file = str(tmp_path / "test.db")
        db = EmailDatabase(sqlite_file)
        db.close()

        result = reingest_metadata("mock.olm", sqlite_path=sqlite_file)
        assert result["updated"] == 0
        assert "No emails" in result["message"]


class TestReingestAnalyticsEdgeCases:
    def test_all_already_have_analytics(self, tmp_path):
        """reingest_analytics should return early when nothing is missing."""
        from mailarium.email_db import EmailDatabase

        sqlite_file = str(tmp_path / "test.db")
        db = EmailDatabase(sqlite_file)
        db.close()

        result = reingest_analytics(sqlite_path=sqlite_file)
        assert result["updated"] == 0
        assert "already have" in result["message"]


class TestReembedEdgeCases:
    def test_reembed_progress_logging(self, monkeypatch, tmp_path):
        """reembed with many emails should trigger progress logging."""
        emails = [_make_email(i) for i in range(1, 4)]
        _, sqlite_file = _seed_ingest_database(monkeypatch, tmp_path, emails, embedder_cls=_MockEmbedder)

        monkeypatch.setattr("mailarium.embedder.EmailEmbedder", _MockEmbedder)

        result = reembed(sqlite_path=sqlite_file)
        assert result["reembedded"] >= 1
        assert result["chunks_added"] >= 1
