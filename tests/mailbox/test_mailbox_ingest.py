"""Focused source-neutral ingestion tests that need no model runtime."""

from __future__ import annotations

import hashlib
import json
import unittest

from mailarium.email_db import EmailDatabase
from mailarium.mailbox_ingest import _mailbox_chunks, mailbox_record_to_email, persist_mailbox_record
from mailarium.mailbox_models import MailboxMessageRecord
from mailarium.mailbox_store import MailboxStore
from mailarium.mailbox_visibility import active_mailbox_uids
from mailarium.parse_olm import Email


class _DeleteRecorder:
    def __init__(self) -> None:
        self.deleted: list[str] = []

    def delete(self, *, ids) -> None:
        self.deleted.extend(ids)


class _RecordingEmbedder:
    def __init__(self, *, existing_ids=(), fail_add: bool = False) -> None:
        self.existing_ids = set(existing_ids)
        self.fail_add = fail_add
        self.add_calls = 0
        self.upserted_ids: list[str] = []
        self.upserted_metadata: list[dict] = []
        self.collection = _DeleteRecorder()
        self.image_collection = _DeleteRecorder()

    def add_chunks(self, chunks, *, show_progress: bool) -> int:
        self.add_calls += 1
        if self.fail_add:
            self.fail_add = False
            raise RuntimeError("transient vector failure")
        return len(chunks)

    def upsert_chunks(self, chunks) -> int:
        self.upserted_ids = [chunk.chunk_id for chunk in chunks]
        self.upserted_metadata = [dict(chunk.metadata) for chunk in chunks]
        return len(chunks)

    def get_existing_ids(self, *, refresh: bool):
        return self.existing_ids

    def checkpoint(self) -> None:
        return None


class MailboxIngestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db = EmailDatabase(":memory:")
        self.store = MailboxStore(self.db.conn)
        self.store.configure_account("account", "ews")
        self.store.set_folders("account", {"inbox": "Inbox"}, source="ews")

    def tearDown(self) -> None:
        self.db.close()

    def record(self, **changes) -> MailboxMessageRecord:
        values = {
            "account_id": "account",
            "folder_id": "inbox",
            "source": "ews",
            "source_identity": "item-1",
            "remote_item_id": "item-1",
            "change_key": "ck-1",
            "internet_message_id": "<message@example.test>",
            "subject": "Subject",
            "received_at": "2026-07-17T10:00:00+00:00",
            "sender_email": "sender@example.test",
            "to": ("recipient@example.test",),
            "body_text": "Original body",
        }
        values.update(changes)
        return MailboxMessageRecord(**values)

    def local_email(self, **changes) -> Email:
        values = {
            "message_id": "<message@example.test>",
            "subject": "Subject",
            "sender_name": "",
            "sender_email": "sender@example.test",
            "to": ["recipient@example.test"],
            "cc": [],
            "bcc": [],
            "date": "2026-07-17T10:00:00+00:00",
            "body_text": "Original body",
            "body_html": "",
            "folder": "local",
            "has_attachments": False,
            "raw_source": "olm",
        }
        values.update(changes)
        return Email(**values)

    def test_insert_then_content_update_reuses_canonical_uid(self) -> None:
        first = persist_mailbox_record(self.record(), db=self.db, store=self.store)
        second = persist_mailbox_record(
            self.record(body_text="Updated body", change_key="ck-2"),
            db=self.db,
            store=self.store,
        )

        self.assertTrue(first.inserted)
        self.assertTrue(second.content_changed)
        self.assertEqual(first.canonical_email_uid, second.canonical_email_uid)
        row = self.db.conn.execute("SELECT body_text FROM emails WHERE uid=?", (first.canonical_email_uid,)).fetchone()
        self.assertEqual("Updated body", row[0])
        source = self.store.conn.execute(
            "SELECT canonical_preexisting FROM email_sources WHERE remote_item_id='item-1'"
        ).fetchone()
        self.assertEqual(0, source[0])

    def test_ews_full_body_is_retained_as_forensic_text_and_segments(self) -> None:
        full_body = (
            "Liebe Petra,\n\nich kuemmere mich darum.\n\n"
            "Von: Anabel Derlam <derlam@example.test>\n"
            "Gesendet: Mittwoch, 13. Mai 2026 15:00\n"
            "An: Petra John <john@example.test>\n"
            "Betreff: eSignatur\n\n"
            "Warum hat sich Sebastian hier mit dem Verteiler eingeschaltet?"
        )

        result = persist_mailbox_record(
            self.record(subject="AW: eSignatur", body_text=full_body),
            db=self.db,
            store=self.store,
        )

        row = self.db.conn.execute(
            "SELECT raw_body_text,forensic_body_text,forensic_body_source FROM emails WHERE uid=?",
            (result.canonical_email_uid,),
        ).fetchone()
        self.assertEqual(full_body, row["raw_body_text"])
        self.assertEqual(full_body, row["forensic_body_text"])
        self.assertEqual("ews_raw_body_text", row["forensic_body_source"])
        segments = self.db.conn.execute(
            "SELECT segment_type,text FROM message_segments WHERE email_uid=? ORDER BY ordinal",
            (result.canonical_email_uid,),
        ).fetchall()
        self.assertTrue(segments)
        self.assertTrue(any("Warum hat sich Sebastian" in segment["text"] for segment in segments))
        email = mailbox_record_to_email(self.record(subject="AW: eSignatur", body_text=full_body), "canonical")
        chunks, _preserved = _mailbox_chunks(email)
        forensic_chunks = [chunk for chunk in chunks if "__forensic_" in chunk.chunk_id]
        self.assertTrue(forensic_chunks)
        self.assertTrue(any("Warum hat sich Sebastian" in chunk.text for chunk in forensic_chunks))
        self.assertTrue(all(chunk.metadata["source_scope"] == "forensic_body_text" for chunk in forensic_chunks))

    def test_recovered_ews_history_updates_forensic_surface_when_clean_body_is_unchanged(self) -> None:
        authored = "Liebe Petra,\n\nich kuemmere mich darum."
        full_body = (
            f"{authored}\n\n"
            "On Wednesday, 13 May 2026, Anabel Derlam wrote:\n"
            "> Warum hat sich Sebastian hier mit dem Verteiler eingeschaltet?"
        )
        first = persist_mailbox_record(
            self.record(subject="AW: eSignatur", body_text=authored),
            db=self.db,
            store=self.store,
        )

        recovered = persist_mailbox_record(
            self.record(subject="AW: eSignatur", body_text=full_body, change_key="ck-2"),
            db=self.db,
            store=self.store,
        )

        self.assertEqual(first.canonical_email_uid, recovered.canonical_email_uid)
        self.assertTrue(recovered.content_changed)
        row = self.db.conn.execute(
            "SELECT body_text,raw_body_text,forensic_body_text FROM emails WHERE uid=?",
            (recovered.canonical_email_uid,),
        ).fetchone()
        self.assertEqual(authored, row["body_text"])
        self.assertEqual(full_body, row["raw_body_text"])
        self.assertEqual(full_body, row["forensic_body_text"])

    def test_conflicting_message_id_uses_source_specific_uid(self) -> None:
        first = persist_mailbox_record(self.record(), db=self.db, store=self.store)
        self.store.set_folders("other", {"inbox": "Inbox"}, source="ews")
        conflicting = self.record(
            account_id="other",
            source_identity="other-item",
            remote_item_id="other-item",
            sender_email="different@example.test",
        )
        second = persist_mailbox_record(conflicting, db=self.db, store=self.store)

        self.assertNotEqual(first.canonical_email_uid, second.canonical_email_uid)
        self.assertTrue(second.possible_duplicate)

    def test_preexisting_archive_email_remains_visible_after_ews_tombstone(self) -> None:
        local = self.local_email(
            raw_body_text="Archive forensic body",
            forensic_body_text="Archive forensic body",
            forensic_body_source="raw_body_text",
        )
        self.assertTrue(self.db.insert_email(local))
        linked = persist_mailbox_record(self.record(), db=self.db, store=self.store)
        self.assertEqual(local.uid, linked.canonical_email_uid)
        source = self.store.conn.execute(
            "SELECT canonical_preexisting FROM email_sources WHERE remote_item_id='item-1'"
        ).fetchone()
        self.assertEqual(1, source[0])
        stored = self.db.conn.execute(
            "SELECT raw_body_text,forensic_body_text FROM emails WHERE uid=?",
            (local.uid,),
        ).fetchone()
        self.assertEqual("Archive forensic body", stored["raw_body_text"])
        self.assertEqual("Archive forensic body", stored["forensic_body_text"])

        self.store.tombstone_source(
            account_id="account",
            folder_id="inbox",
            source="ews",
            source_identity="item-1",
            change_key="ck-2",
        )

        self.assertEqual({local.uid}, active_mailbox_uids(self.db.conn, (local.uid,)))

    def test_opted_in_attachment_content_uses_stable_identity_and_text_chunks(self) -> None:
        attachment = {
            "remote_attachment_id": "ews-att-1",
            "name": "notes.txt",
            "mime_type": "text/plain",
            "size": 11,
        }
        metadata_only = mailbox_record_to_email(
            self.record(attachments=(attachment,)),
            "canonical",
        )
        with_content = mailbox_record_to_email(
            self.record(
                attachments=(attachment,),
                attachment_contents=(("notes.txt", b"hello world"),),
            ),
            "canonical",
        )

        self.assertEqual(
            metadata_only.attachments[0]["attachment_id"],
            with_content.attachments[0]["attachment_id"],
        )
        self.assertEqual("hello world", with_content.attachments[0]["extracted_text"])
        chunks, _preserved = _mailbox_chunks(with_content)
        self.assertTrue(any("__att_" in chunk.chunk_id for chunk in chunks))

    def test_vector_failure_leaves_projection_retryable_without_orphan(self) -> None:
        embedder = _RecordingEmbedder(fail_add=True)

        with self.assertRaisesRegex(RuntimeError, "transient vector failure"):
            persist_mailbox_record(
                self.record(),
                db=self.db,
                store=self.store,
                embedder=embedder,
            )

        source = self.store.conn.execute(
            "SELECT canonical_email_uid,metadata_json FROM email_sources WHERE remote_item_id='item-1'"
        ).fetchone()
        self.assertIsNotNone(source)
        self.assertNotIn("projection_hash", json.loads(source["metadata_json"]))
        self.assertTrue(json.loads(source["metadata_json"])["projection_pending"])
        self.assertEqual(
            1,
            self.db.conn.execute("SELECT COUNT(*) FROM emails e JOIN email_sources s ON s.canonical_email_uid=e.uid").fetchone()[
                0
            ],
        )
        replay = persist_mailbox_record(
            self.record(
                change_key="ck-2",
                metadata={"safe_diagnostic": "replayed", "credential_value": "must-not-persist"},
            ),
            db=self.db,
            store=self.store,
            embedder=embedder,
        )
        self.assertTrue(replay.metadata_changed)
        self.assertTrue(embedder.upserted_ids)
        source = self.store.conn.execute(
            "SELECT change_key,metadata_json FROM email_sources WHERE remote_item_id='item-1'"
        ).fetchone()
        source_metadata = json.loads(source["metadata_json"])
        self.assertEqual("ck-2", source["change_key"])
        self.assertEqual("replayed", source_metadata["safe_diagnostic"])
        self.assertEqual("[REDACTED]", source_metadata["credential_value"])
        self.assertIn("projection_hash", source_metadata)
        self.assertNotIn("projection_pending", source_metadata)
        self.assertEqual(1, self.store.conn.execute("SELECT COUNT(*) FROM email_source_identity_history").fetchone()[0])

    def test_metadata_only_ews_refresh_preserves_richer_canonical_attachment(self) -> None:
        content = b"canonical attachment evidence"
        content_sha256 = hashlib.sha256(content).hexdigest()
        attachment = {
            "name": "notes.txt",
            "mime_type": "text/plain",
            "size": len(content),
            "attachment_id": f"sha256:{content_sha256}",
            "content_sha256": content_sha256,
            "extracted_text": content.decode(),
            "normalized_text": content.decode(),
            "text_normalization_version": 1,
            "extraction_state": "text_extracted",
            "evidence_strength": "strong_text",
        }
        local = self.local_email(
            has_attachments=True,
            attachment_names=["notes.txt"],
            attachments=[attachment],
        )
        old_attachment_chunks = {chunk.chunk_id for chunk in _mailbox_chunks(local)[0] if "__att_" in chunk.chunk_id}
        self.assertTrue(self.db.insert_email(local))
        embedder = _RecordingEmbedder(existing_ids=old_attachment_chunks)

        result = persist_mailbox_record(
            self.record(
                attachments=(
                    {
                        "remote_attachment_id": "ews-att-1",
                        "name": "notes.txt",
                        "mime_type": "text/plain",
                        "size": len(content),
                    },
                )
            ),
            db=self.db,
            store=self.store,
            embedder=embedder,
        )

        self.assertTrue(result.metadata_changed)
        stored = self.db.attachments_for_email(local.uid)[0]
        self.assertEqual(f"sha256:{content_sha256}", stored["attachment_id"])
        self.assertEqual(content.decode(), stored["extracted_text"])
        self.assertLessEqual(old_attachment_chunks, set(embedder.upserted_ids))
        self.assertEqual([], embedder.collection.deleted)

    def test_copied_message_projects_both_active_source_folders(self) -> None:
        original = persist_mailbox_record(self.record(), db=self.db, store=self.store)
        self.store.set_folders("account", {"archive": "Archive"}, source="ews")
        self.store.record_remote_identity_change(
            account_id="account",
            source="ews",
            old_remote_item_id="item-1",
            new_remote_item_id="item-copy",
            new_change_key="copy-ck",
            destination_folder_id="archive",
            copy=True,
        )
        embedder = _RecordingEmbedder()

        copied = persist_mailbox_record(
            self.record(
                folder_id="archive",
                source_identity="item-copy",
                remote_item_id="item-copy",
                change_key="copy-ck",
            ),
            db=self.db,
            store=self.store,
            embedder=embedder,
        )

        self.assertEqual(original.canonical_email_uid, copied.canonical_email_uid)
        self.assertTrue(embedder.upserted_metadata)
        self.assertTrue(all(metadata["source_folders"] == ["archive", "inbox"] for metadata in embedder.upserted_metadata))
        folder = self.db.conn.execute(
            "SELECT folder FROM emails WHERE uid=?",
            (original.canonical_email_uid,),
        ).fetchone()[0]
        self.assertEqual("archive", folder)


if __name__ == "__main__":
    unittest.main()
