# ruff: noqa: I001

"""Attachment degradation, OCR, recovery, and stale-chunk cleanup behavior."""

from typing import Any


from .helpers.ingest_fixtures import (
    _configure_ocr_reparse,
    _make_mock_email,
    _make_mock_image_email,
    _make_reembed_embedder,
    _seed_degraded_image_ingest,
    _seed_ingest_database,
)


def test_ingest_persists_attachment_evidence_metadata(monkeypatch, tmp_path):
    from mailarium.email_db import EmailDatabase

    email = _make_mock_email(1)
    email.has_attachments = True
    email.attachment_names = ["notes.txt"]
    email.attachments = [
        {
            "name": "notes.txt",
            "mime_type": "text/plain",
            "size": 18,
            "content_id": "",
            "is_inline": False,
        }
    ]
    email.attachment_contents = [("notes.txt", b"hello from attachment")]

    monkeypatch.setattr("mailarium.attachment_extractor.image_ocr_available", lambda: False)
    _, sqlite_file, stats = _seed_ingest_database(
        monkeypatch,
        tmp_path,
        [email],
        extract_attachments=True,
        return_stats=True,
    )

    assert stats["sqlite_inserted"] == 1

    db = EmailDatabase(sqlite_file)
    attachments = db.attachments_for_email(email.uid)
    assert len(attachments) == 1
    assert attachments[0]["extraction_state"] == "text_extracted"
    assert attachments[0]["evidence_strength"] == "strong_text"
    assert attachments[0]["ocr_used"] == 0
    assert attachments[0]["failure_reason"] in (None, "")
    assert attachments[0]["text_preview"] == "hello from attachment"
    assert attachments[0]["extracted_text"] == "hello from attachment"
    assert attachments[0]["normalized_text"] == "hello from attachment"
    assert attachments[0]["text_normalization_version"] == 1
    assert attachments[0]["attachment_id"]
    assert attachments[0]["content_sha256"]
    assert attachments[0]["locator_version"] == 2
    assert attachments[0]["text_source_path"] == f"attachment://{email.uid}/0/notes.txt"
    locator = attachments[0]["text_locator"]
    assert locator["kind"] == "mailbox_attachment"
    assert locator["email_uid"] == email.uid
    assert locator["attachment_index"] == 0
    assert locator["filename"] == "notes.txt"
    assert locator["extraction_state"] == "text_extracted"
    assert locator["attachment_id"] == attachments[0]["attachment_id"]
    assert locator["content_sha256"] == attachments[0]["content_sha256"]
    assert locator["locator_version"] == 2
    db.close()


def test_mailbox_attachment_locator_extracts_rich_subdocument_hints() -> None:
    import mailarium.ingest_pipeline as ingest_pipeline

    locator = ingest_pipeline._mailbox_attachment_locator(
        email_uid="uid-locator",
        att_index=0,
        filename="bundle.zip",
        extraction_state="text_extracted",
        attachment_id="att-1",
        content_sha256="sha-1",
        extracted_text="[Member: records/report.xlsx]\n[Sheet: Tabelle1]\nA1:B4\n[Page 2]",
    )

    assert locator["archive_member_path"] == "records/report.xlsx"
    assert locator["sheet_name"] == "Tabelle1"
    assert locator["cell_range"] == "A1:B4"
    assert locator["page_number"] == 2
    assert locator["page_count"] == 2


def test_ingest_binary_only_attachment_stays_degraded_in_ledger(monkeypatch, tmp_path):
    from mailarium.email_db import EmailDatabase

    email = _make_mock_image_email(filename="photo.png")

    monkeypatch.setattr("mailarium.attachment_extractor.image_ocr_available", lambda: False)
    _, sqlite_file, stats = _seed_ingest_database(
        monkeypatch,
        tmp_path,
        [email],
        extract_attachments=True,
        return_stats=True,
    )

    assert stats["sqlite_inserted"] == 1

    db = EmailDatabase(sqlite_file)
    row = db.conn.execute(
        "SELECT vector_status, attachment_status FROM email_ingest_state WHERE email_uid = ?",
        (email.uid,),
    ).fetchone()
    assert row is not None
    assert row["vector_status"] == "completed"
    assert row["attachment_status"] == "degraded"
    attachment = db.attachments_for_email(email.uid)[0]
    assert attachment["extraction_state"] == "binary_only"
    assert attachment["failure_reason"] == "no_text_extracted_ocr_not_available"
    db.close()


def test_attachment_payload_failure_marks_degraded_not_completed(monkeypatch, tmp_path):
    from mailarium.email_db import EmailDatabase

    email = _make_mock_email(1)
    email.has_attachments = True
    email.attachment_names = ["scan.pdf"]
    email.attachments = [
        {
            "name": "scan.pdf",
            "mime_type": "application/pdf",
            "size": 1024,
            "content_id": "",
            "is_inline": False,
        }
    ]
    email.attachment_contents = []
    email.__dict__["_attachment_payload_extraction_failed"] = True

    _, sqlite_file, stats = _seed_ingest_database(
        monkeypatch,
        tmp_path,
        [email],
        extract_attachments=True,
        return_stats=True,
    )

    assert stats["sqlite_inserted"] == 1

    db = EmailDatabase(sqlite_file)
    row = db.conn.execute(
        "SELECT attachment_status FROM email_ingest_state WHERE email_uid = ?",
        (email.uid,),
    ).fetchone()
    assert row is not None
    assert row["attachment_status"] == "degraded"
    attachment = db.attachments_for_email(email.uid)[0]
    assert attachment["extraction_state"] == "extraction_failed"
    assert attachment["failure_reason"] == "attachment_payload_extraction_failed"
    assert email.uid not in db.completed_ingest_uids(attachment_required=True)
    db.close()


def test_ingest_image_attachment_uses_ocr_when_available(monkeypatch, tmp_path):
    from mailarium.email_db import EmailDatabase

    email = _make_mock_image_email(filename="photo.png")

    monkeypatch.setattr(
        "mailarium.attachment_extractor.extract_image_text_ocr",
        lambda filename, content, **_kw: "Recovered screenshot text",
    )
    _, sqlite_file = _seed_ingest_database(monkeypatch, tmp_path, [email], extract_attachments=True)

    db = EmailDatabase(sqlite_file)
    row = db.conn.execute(
        "SELECT attachment_status FROM email_ingest_state WHERE email_uid = ?",
        (email.uid,),
    ).fetchone()
    attachment = db.attachments_for_email(email.uid)[0]
    assert row["attachment_status"] == "completed"
    assert attachment["extraction_state"] == "ocr_text_extracted"
    assert attachment["evidence_strength"] == "strong_text"
    assert attachment["ocr_used"] == 1
    assert attachment["text_preview"] == "Recovered screenshot text"
    db.close()


def test_textless_pdf_ocr_state_requires_pdf_tooling(monkeypatch):
    from mailarium.attachment_extractor import attachment_ocr_available_for
    from mailarium.ingest_pipeline import _textless_attachment_state_with_ocr

    monkeypatch.setattr("mailarium.attachment_extractor.image_ocr_available", lambda: True)
    monkeypatch.setattr("mailarium.attachment_extractor.pdf_ocr_available", lambda: False)

    state, reason = _textless_attachment_state_with_ocr(
        filename="scan.pdf",
        mime_type="application/pdf",
        ocr_attempted=True,
        ocr_available=attachment_ocr_available_for("scan.pdf", mime_type="application/pdf"),
    )

    assert state == "binary_only"
    assert reason == "no_text_extracted_ocr_not_available"


def test_ingest_image_chunks_use_normalized_attachment_metadata(monkeypatch, tmp_path):
    import mailarium.ingest as ingest_mod

    email = _make_mock_image_email(filename="photo.png")

    monkeypatch.setattr(ingest_mod, "parse_olm", lambda _path, **_kw: [email])
    monkeypatch.setattr(ingest_mod, "chunk_email", lambda email_dict: [{"chunk_id": f"{email_dict.get('uid', 'x')}-a"}])
    monkeypatch.setattr(ingest_mod, "should_enable_image_embedding", lambda: True)
    monkeypatch.setattr("mailarium.attachment_extractor._get_image_embedder", lambda: type("Probe", (), {"is_available": True})())
    monkeypatch.setattr("mailarium.attachment_extractor.extract_image_embedding", lambda *_args, **_kwargs: [0.1, 0.2, 0.3])

    class _TrackingEmbedder:
        last_instance: Any | None = None

        def __init__(self, **_kw):
            type(self).last_instance = self
            self._count = 0
            self.added_chunks = []

        def count(self):
            return self._count

        def add_chunks(self, chunks, **_kw):
            self.added_chunks.extend(chunks)
            self._count += len(chunks)
            return len(chunks)

        def set_sparse_db(self, db):
            return None

        def warmup(self):
            return None

    monkeypatch.setattr("mailarium.embedder.EmailEmbedder", _TrackingEmbedder)

    sqlite_file = str(tmp_path / "test.db")
    ingest_mod.ingest("mock.olm", dry_run=False, sqlite_path=sqlite_file, embed_images=True)

    instance = _TrackingEmbedder.last_instance
    assert instance is not None
    image_chunks = [c for c in instance.added_chunks if c.metadata.get("chunk_type") == "image"]
    assert len(image_chunks) == 1
    metadata = image_chunks[0].metadata
    assert metadata["candidate_kind"] == "attachment"
    assert metadata["is_attachment"] == "True"
    assert metadata["attachment_filename"] == "photo.png"
    assert metadata["attachment_name"] == "photo.png"
    assert metadata["attachment_type"] == "png"


def test_reprocess_degraded_attachments_recovers_image_text(tmp_path, monkeypatch):
    from mailarium.email_db import EmailDatabase

    ingest_mod, sqlite_file, image_email = _seed_degraded_image_ingest(monkeypatch, tmp_path)
    email_uid = image_email.uid
    _configure_ocr_reparse(monkeypatch, ingest_mod)
    result = ingest_mod.reprocess_degraded_attachments(
        "mock.olm",
        sqlite_path=sqlite_file,
        batch_size=10,
    )

    assert result["updated"] == 1
    assert result["ocr_recovered"] == 1
    db = EmailDatabase(sqlite_file)
    row = db.conn.execute(
        "SELECT attachment_status FROM email_ingest_state WHERE email_uid = ?",
        (email_uid,),
    ).fetchone()
    attachment = db.attachments_for_email(email_uid)[0]
    assert row["attachment_status"] == "completed"
    assert attachment["extraction_state"] == "ocr_text_extracted"
    assert attachment["ocr_used"] == 1
    db.close()


def test_reprocess_degraded_attachments_deletes_stale_attachment_chunks(tmp_path, monkeypatch):
    from mailarium.ingest_reingest import _attachment_chunk_prefix

    ingest_mod, sqlite_file, image_email = _seed_degraded_image_ingest(monkeypatch, tmp_path)
    email_uid = image_email.uid

    stale_prefix = _attachment_chunk_prefix(email_uid, "photo.png", 0)
    delete_calls = []

    monkeypatch.setattr(
        "mailarium.embedder.EmailEmbedder",
        _make_reembed_embedder(
            existing_ids={f"{stale_prefix}0", f"{stale_prefix}1", f"{stale_prefix}2"},
            delete_calls=delete_calls,
        ),
    )
    _configure_ocr_reparse(monkeypatch, ingest_mod)

    result = ingest_mod.reprocess_degraded_attachments(
        "mock.olm",
        sqlite_path=sqlite_file,
        batch_size=10,
    )

    assert result["chunks_deleted"] == 3
    assert len(delete_calls) == 1
    assert set(delete_calls[0]) == {f"{stale_prefix}0", f"{stale_prefix}1", f"{stale_prefix}2"}
