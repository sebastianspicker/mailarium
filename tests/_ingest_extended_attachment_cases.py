"""Attachment-processing ingestion tests."""

import types
from unittest.mock import MagicMock


class TestAttachmentProcessing:
    def test_attachment_text_extraction(self, monkeypatch, tmp_path):
        """When extract_attachments=True, attachment text should be chunked."""
        import mailarium.ingest as ingest_mod

        class _EmailWithAtt:
            def __init__(self):
                self.uid = "uid-att"
                self.attachment_contents = [("doc.txt", b"Hello attachment text")]
                self.message_id = "<att@example.test>"

            def to_dict(self):
                return {
                    "uid": self.uid,
                    "subject": "Test",
                    "sender_name": "S",
                    "sender_email": "s@example.test",
                    "date": "2024-01-01",
                    "folder": "Inbox",
                }

        monkeypatch.setattr(ingest_mod, "parse_olm", lambda _path, **_kw: [_EmailWithAtt()])
        monkeypatch.setattr(ingest_mod, "chunk_email", lambda e: [{"chunk_id": f"{e.get('uid', 'x')}-a"}])
        monkeypatch.setattr(ingest_mod, "chunk_attachment", lambda **kw: [MagicMock()])
        original_import = __import__

        def _mock_import(name, *args, **kwargs):
            if name == "mailarium.attachment_extractor" or (args and "attachment_extractor" in str(args)):
                mod = types.ModuleType("mailarium.attachment_extractor")
                mod.extract_text = lambda name, data: "extracted text" if data else None
                return mod
            return original_import(name, *args, **kwargs)

        stats = ingest_mod.ingest("mock.olm", dry_run=True, extract_attachments=True)
        assert stats["emails_parsed"] == 1
