# ruff: noqa: I001

"""Ingestion lifecycle, idempotency, resume, checkpoints, batching, and producer-abort behavior."""

from typing import Any


import pytest


from mailarium.ingest import _EmbedPipeline


from .helpers.ingest_fixtures import _MockEmbedder, _make_mock_email, _seed_ingest_database


def test_ingest_zero_chunk_email_marks_ledger_completed(monkeypatch, tmp_path):
    import mailarium.embedder as embedder_mod
    import mailarium.ingest as ingest_mod
    from mailarium.email_db import EmailDatabase

    email = _make_mock_email(1)

    monkeypatch.setattr(ingest_mod, "parse_olm", lambda _path, **_kw: [email])
    monkeypatch.setattr(ingest_mod, "chunk_email", lambda _email: [])
    monkeypatch.setattr(embedder_mod, "EmailEmbedder", _MockEmbedder)

    sqlite_file = str(tmp_path / "test.db")
    stats = ingest_mod.ingest("mock.olm", dry_run=False, sqlite_path=sqlite_file)

    assert stats["sqlite_inserted"] == 1

    db = EmailDatabase(sqlite_file)
    row = db.conn.execute(
        "SELECT vector_status, vector_chunk_count, attachment_status, image_status FROM email_ingest_state WHERE email_uid = ?",
        (email.uid,),
    ).fetchone()
    assert row is not None
    assert row["vector_status"] == "completed"
    assert row["vector_chunk_count"] == 0
    assert row["attachment_status"] == "not_requested"
    assert row["image_status"] == "not_requested"
    db.close()


def test_reingest_is_idempotent(monkeypatch, tmp_path):
    emails = [_make_mock_email(i) for i in range(1, 3)]
    ingest_mod, sqlite_file, stats1 = _seed_ingest_database(monkeypatch, tmp_path, emails, return_stats=True)
    assert stats1["sqlite_inserted"] == 2

    stats2 = ingest_mod.ingest("mock.olm", dry_run=False, sqlite_path=sqlite_file)
    assert stats2["sqlite_inserted"] == 0

    from mailarium.email_db import EmailDatabase

    db = EmailDatabase(sqlite_file)
    assert db.email_count() == 2
    db.close()


def test_ingest_resume_skips_previously_parsed_emails(monkeypatch, tmp_path):
    import mailarium.embedder as embedder_mod
    import mailarium.ingest as ingest_mod
    from mailarium.email_db import EmailDatabase

    emails = [_make_mock_email(i) for i in range(1, 4)]
    monkeypatch.setattr(ingest_mod, "parse_olm", lambda _path, **_kw: emails)
    monkeypatch.setattr(
        ingest_mod,
        "chunk_email",
        lambda email: [{"chunk_id": f"{email.get('uid', 'x')}-a"}],
    )
    monkeypatch.setattr(embedder_mod, "EmailEmbedder", _MockEmbedder)

    sqlite_file = str(tmp_path / "resume.db")
    db = EmailDatabase(sqlite_file)
    run_id = db.record_ingestion_start("mock.olm")
    db.update_ingest_checkpoint(
        run_id=run_id,
        olm_path="mock.olm",
        last_batch_ordinal=1,
        emails_parsed=2,
        emails_inserted=0,
        last_email_uid=emails[1].uid,
        status="failed",
        commit=True,
    )
    db.record_ingestion_failure(run_id, error_message="interrupted", stats={"emails_parsed": 2, "emails_inserted": 0})
    db.close()

    stats = ingest_mod.ingest(
        "mock.olm",
        dry_run=False,
        sqlite_path=sqlite_file,
        resume=True,
    )

    assert stats["resumed_from_checkpoint"] is True
    assert stats["skipped_resume"] == 2
    assert stats["sqlite_inserted"] == 1


def test_update_ingest_checkpoint_safe_skips_locked_checkpoint(monkeypatch):
    import logging
    import sqlite3

    import mailarium.ingest_pipeline as ingest_pipeline_mod

    class _CheckpointStore:
        def update_ingest_checkpoint(self, **_kwargs):
            raise sqlite3.OperationalError("database is locked")

    messages: list[str] = []

    class _Handler(logging.Handler):
        def emit(self, record):
            messages.append(record.getMessage())

    handler = _Handler()
    logger = logging.getLogger(ingest_pipeline_mod.__name__)
    logger.addHandler(handler)
    previous_level = logger.level
    logger.setLevel(logging.DEBUG)
    try:
        updated = ingest_pipeline_mod._update_ingest_checkpoint_safe(
            checkpoint_store=_CheckpointStore(),
            run_id=1,
            olm_path="archive.olm",
            last_batch_ordinal=2,
            emails_parsed=42,
            emails_inserted=40,
            last_email_uid="uid-42",
            status="running",
            allow_locked_skip=True,
            stage="mid_run_batch_submit",
        )
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous_level)

    assert updated is False
    assert any("Skipping ingest checkpoint update during mid_run_batch_submit" in message for message in messages)


def test_embed_pipeline_subbatches_large_chunk_groups():
    from typing import cast

    from mailarium.chunker import EmailChunk

    calls: list[int] = []

    class _FakeEmbedder:
        def add_chunks(self, chunks, batch_size=500, skip_existing_check=False):
            calls.append(len(chunks))
            return len(chunks)

    pipeline = _EmbedPipeline(
        embedder=cast(Any, _FakeEmbedder()),
        email_db=None,
        entity_extractor_fn=None,
        batch_size=10,
    )

    chunks = [EmailChunk(uid="u1", chunk_id=f"u1__{idx}", text=f"chunk {idx}", metadata={}) for idx in range(25)]
    pipeline._process_batch(chunks, [])

    assert calls == [10, 10, 5]
    assert pipeline.chunks_added == 25


class _AbortFakeEmbedder:
    def count(self):
        return 0

    def set_sparse_db(self, _db):
        return None

    def warmup(self):
        return None


class _AbortFakeEmailDB:
    def __init__(self, events: list[str]):
        self.events = events

    def record_ingestion_start(self, *_args, **_kwargs):
        self.events.append("db.record_start")
        return 1

    def record_ingestion_failure(self, *_args, **_kwargs):
        self.events.append("db.record_failure")

    def close(self):
        self.events.append("db.close")


class _AbortFakePipeline:
    def __init__(self, *, events: list[str], **_kwargs):
        self.events = events
        self.chunks_added = 0
        self.batches_written = 0
        self.sqlite_inserted = 0
        self._timing = {
            "embed_seconds": 0.0,
            "write_seconds": 0.0,
            "sqlite_seconds": 0.0,
            "entity_seconds": 0.0,
            "analytics_seconds": 0.0,
        }

    def start(self):
        self.events.append("pipeline.start")

    def submit(self, _chunks, _emails):
        self.events.append("pipeline.submit")

    def finish(self):
        self.events.append("pipeline.finish")

    def abort(self):
        self.events.append("pipeline.abort")
        return None


def _parse_then_fail(_path, **_kwargs):
    yield _make_mock_email(1)
    raise RuntimeError("parse exploded")


def _build_abort_pipeline_fakes(events: list[str]) -> tuple:
    class _BoundAbortFakePipeline(_AbortFakePipeline):
        def __init__(self, **kwargs):
            super().__init__(events=events, **kwargs)

    return _AbortFakeEmbedder, lambda: _AbortFakeEmailDB(events), _BoundAbortFakePipeline, _parse_then_fail


def test_producer_parse_exception_aborts_pipeline_before_db_close(monkeypatch, tmp_path):
    import mailarium.ingest as ingest_mod
    import mailarium.ingest_pipeline as ingest_pipeline_mod

    events: list[str] = []
    _FakeEmbedder, _FakeEmailDB, _FakePipeline, _parse_then_fail = _build_abort_pipeline_fakes(events)

    monkeypatch.setattr(ingest_pipeline_mod, "_build_runtime", lambda **_kwargs: (_FakeEmbedder(), _FakeEmailDB()))
    monkeypatch.setattr(ingest_mod, "parse_olm", _parse_then_fail)
    monkeypatch.setattr(
        ingest_mod,
        "chunk_email",
        lambda email_dict: [{"chunk_id": f"{email_dict.get('uid', 'x')}__0"}],
    )
    monkeypatch.setattr(ingest_mod, "_EmbedPipeline", _FakePipeline)

    with pytest.raises(RuntimeError, match="parse exploded"):
        ingest_mod.ingest("mock.olm", dry_run=False, sqlite_path=str(tmp_path / "test.db"), batch_size=1)

    assert "pipeline.abort" in events
    assert "db.close" in events
    assert events.index("pipeline.abort") < events.index("db.close")
