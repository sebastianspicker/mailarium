# ruff: noqa: I001
"""Public ingestion facade option edge cases."""

from .helpers.ingest_extended_fixtures import _MockEmbedder, _make_email
from .helpers.ingest_fixtures import _make_minimal_ingest_email, _seed_ingest_database


class TestIngestEdgeCases:
    def test_timing_flag_adds_detailed_breakdown(self, monkeypatch, tmp_path):
        emails = [_make_email(i) for i in range(1, 4)]
        _, _, stats = _seed_ingest_database(
            monkeypatch, tmp_path, emails, embedder_cls=_MockEmbedder, return_stats=True, ingest_kwargs={"timing": True}
        )
        timing = stats["timing"]
        assert "parse_seconds" in timing
        assert "queue_wait_seconds" in timing
        assert "sqlite_seconds" in timing
        assert "entity_seconds" in timing
        assert "analytics_seconds" in timing

    def test_max_emails_limits_parsing(self, monkeypatch):
        import mailarium.ingest as ingest_mod

        monkeypatch.setattr(ingest_mod, "parse_olm", lambda _path, **_kw: [_make_minimal_ingest_email(i) for i in range(1, 11)])
        monkeypatch.setattr(ingest_mod, "chunk_email", lambda e: [{"chunk_id": f"{e.get('uid', 'x')}-a"}])

        stats = ingest_mod.ingest("mock.olm", dry_run=True, max_emails=5)
        assert stats["emails_parsed"] == 5

    def test_batch_flushing_during_loop(self, monkeypatch, tmp_path):
        """When pending chunks exceed batch_size, they should be flushed."""
        import mailarium.embedder as embedder_mod
        import mailarium.ingest as ingest_mod

        emails = [_make_email(i) for i in range(1, 6)]
        monkeypatch.setattr(ingest_mod, "parse_olm", lambda _path, **_kw: emails)
        monkeypatch.setattr(
            ingest_mod,
            "chunk_email",
            lambda e: [{"chunk_id": f"{e.get('uid', 'x')}-{j}", "uid": e.get("uid", "x")} for j in range(3)],
        )
        monkeypatch.setattr(embedder_mod, "EmailEmbedder", _MockEmbedder)

        sqlite_file = str(tmp_path / "test.db")
        stats = ingest_mod.ingest("mock.olm", dry_run=False, sqlite_path=sqlite_file, batch_size=5)
        assert stats["chunks_created"] == 15
        assert stats["batches_written"] >= 1

    def test_hundred_email_progress_logging(self, monkeypatch):
        """100th email should trigger progress logging."""
        import mailarium.ingest as ingest_mod

        monkeypatch.setattr(ingest_mod, "parse_olm", lambda _path, **_kw: [_make_minimal_ingest_email(i) for i in range(1, 102)])
        monkeypatch.setattr(ingest_mod, "chunk_email", lambda e: [{"chunk_id": f"{e.get('uid', 'x')}-a"}])

        stats = ingest_mod.ingest("mock.olm", dry_run=True, max_emails=101)
        assert stats["emails_parsed"] == 101

    def test_ingest_records_olm_hash(self, monkeypatch, tmp_path):
        """Non-dry ingest should compute OLM file hash and size."""
        import mailarium.embedder as embedder_mod
        import mailarium.ingest as ingest_mod

        olm_file = tmp_path / "test.olm"
        olm_file.write_bytes(b"fake olm content")
        monkeypatch.setattr(ingest_mod, "parse_olm", lambda _path, **_kw: [])
        monkeypatch.setattr(embedder_mod, "EmailEmbedder", _MockEmbedder)

        sqlite_file = str(tmp_path / "test.db")
        stats = ingest_mod.ingest(str(olm_file), dry_run=False, sqlite_path=sqlite_file)
        assert stats["emails_parsed"] == 0
