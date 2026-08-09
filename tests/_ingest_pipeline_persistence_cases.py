"""Ingestion persistence, dry-run behavior, and storage diagnostics."""

from .helpers.ingest_fixtures import _make_mock_email, _seed_ingest_database


def test_ingest_dry_run_reports_qol_stats(monkeypatch):
    import mailarium.ingest as ingest_mod

    class _Email:
        def __init__(self, idx):
            self.idx = idx

        def to_dict(self):
            return {"id": self.idx}

    monkeypatch.setattr(ingest_mod, "parse_olm", lambda _path, **_kw: [_Email(1), _Email(2), _Email(3)])
    monkeypatch.setattr(
        ingest_mod,
        "chunk_email",
        lambda email: [{"chunk_id": f"{email['id']}-a"}, {"chunk_id": f"{email['id']}-b"}],
    )

    stats = ingest_mod.ingest("data/mock.olm", dry_run=True, batch_size=2)

    assert stats["emails_parsed"] == 3
    assert stats["chunks_created"] == 6
    assert stats["chunks_added"] == 0
    assert stats["chunks_skipped"] == 0
    assert stats["batches_written"] == 0


def test_ingest_populates_sqlite(monkeypatch, tmp_path):
    emails = [_make_mock_email(i) for i in range(1, 4)]
    _, sqlite_file, stats = _seed_ingest_database(monkeypatch, tmp_path, emails, return_stats=True)

    assert stats["sqlite_inserted"] == 3

    from mailarium.email_db import EmailDatabase

    db = EmailDatabase(sqlite_file)
    assert db.email_count() == 3
    db.close()


def test_ingest_surfaces_sparse_storage_diagnostics_in_stats(monkeypatch, tmp_path):
    import mailarium.ingest as ingest_mod

    email = _make_mock_email(1)
    monkeypatch.setattr(ingest_mod, "parse_olm", lambda _path, **_kw: [email])
    monkeypatch.setattr(ingest_mod, "chunk_email", lambda email_dict: [{"chunk_id": f"{email_dict.get('uid', 'x')}-a"}])

    class _SparseDiagnosticsEmbedder:
        def __init__(self, **_kw):
            self._count = 0
            self.sparse_store_failures = 2
            self.sparse_vectors_stored = 7

        def count(self):
            return self._count

        def add_chunks(self, chunks, **_kw):
            self._count += len(chunks)
            return len(chunks)

        def set_sparse_db(self, db):
            return None

        def warmup(self):
            return None

    monkeypatch.setattr("mailarium.embedder.EmailEmbedder", _SparseDiagnosticsEmbedder)

    sqlite_file = str(tmp_path / "test.db")
    stats = ingest_mod.ingest("mock.olm", dry_run=False, sqlite_path=sqlite_file)

    assert stats["sparse_store_failures"] == 2
    assert stats["sparse_vectors_stored"] == 7


def test_ingest_dry_run_skips_sqlite(monkeypatch, tmp_path):
    import mailarium.ingest as ingest_mod

    emails = [_make_mock_email(1)]
    monkeypatch.setattr(ingest_mod, "parse_olm", lambda _path, **_kw: emails)
    monkeypatch.setattr(
        ingest_mod,
        "chunk_email",
        lambda email: [{"chunk_id": "x"}],
    )

    sqlite_file = str(tmp_path / "test.db")
    stats = ingest_mod.ingest("mock.olm", dry_run=True, sqlite_path=sqlite_file)

    assert stats["sqlite_inserted"] == 0
    import os

    assert not os.path.exists(sqlite_file)
