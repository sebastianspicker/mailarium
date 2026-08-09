"""OLM attachment-content extraction cases."""

from __future__ import annotations

import base64
import zipfile
from pathlib import Path

from mailarium.olm_xml_helpers import _extract_attachment_contents
from mailarium.parse_olm import parse_olm


def _extract_from_archive(tmp_path: Path, archive_name: str, xml_content: bytes, *, attachments=None):
    """Write an OLM fixture, then extract attachment content from its message XML."""
    archive = tmp_path / archive_name
    xml_path = "Accounts/a/com.microsoft.__Messages/Inbox/msg.xml"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(xml_path, xml_content)
        for path, content in ({} if attachments is None else attachments).items():
            zf.writestr(path, content)
    with zipfile.ZipFile(archive, "r") as zf:
        return _extract_attachment_contents(xml_content, xml_path, zf)


class TestExtractAttachmentContents:
    def test_extract_inline_base64_attachment(self, tmp_path: Path):
        """Extract attachment content from inline base64 data."""
        content = b"Hello World!"
        b64 = base64.b64encode(content).decode()
        xml_content = f"""<?xml version="1.0"?>
<emails><email>
  <OPFMessageCopySentTime>2025-01-01T00:00:00</OPFMessageCopySentTime>
  <OPFMessageCopySubject>Attach content</OPFMessageCopySubject>
  <OPFMessageCopyAttachmentList>
    <messageAttachment>
      <OPFAttachmentName>hello.txt</OPFAttachmentName>
      <OPFAttachmentContentData>{b64}</OPFAttachmentContentData>
    </messageAttachment>
  </OPFMessageCopyAttachmentList>
</email></emails>""".encode()

        archive = tmp_path / "attach.olm"
        xml_path = "Accounts/a/com.microsoft.__Messages/Inbox/msg.xml"
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr(xml_path, xml_content)

        with zipfile.ZipFile(archive, "r") as zf:
            result = _extract_attachment_contents(xml_content, xml_path, zf)

        assert len(result) == 1
        assert result[0][0] == "hello.txt"
        assert result[0][1] == content

    def test_extract_attachment_from_zip_path(self, tmp_path: Path):
        """Extract attachment content via relative path in ZIP."""
        xml_content = b"""<?xml version="1.0"?>
<emails><email>
  <OPFMessageCopySentTime>2025-01-01T00:00:00</OPFMessageCopySentTime>
  <OPFMessageCopySubject>Attach file</OPFMessageCopySubject>
  <OPFMessageCopyAttachmentList>
    <messageAttachment>
      <OPFAttachmentName>data.bin</OPFAttachmentName>
      <OPFAttachmentURL>data.bin</OPFAttachmentURL>
    </messageAttachment>
  </OPFMessageCopyAttachmentList>
</email></emails>"""
        att_path = "Accounts/a/com.microsoft.__Messages/Inbox/data.bin"
        result = _extract_from_archive(
            tmp_path,
            "attach_url.olm",
            xml_content,
            attachments={att_path: b"binary data here"},
        )

        assert len(result) == 1
        assert result[0][0] == "data.bin"
        assert result[0][1] == b"binary data here"

    def test_extract_attachment_from_zip_path_ignores_xml_space_name_collision(self, tmp_path: Path):
        """Attachment filenames from attributes must not resolve to xml:space='preserve'."""
        xml_content = b"""<?xml version="1.0"?>
<emails xml:space="preserve"><email xml:space="preserve">
  <OPFMessageCopySentTime>2025-01-01T00:00:00</OPFMessageCopySentTime>
  <OPFMessageCopySubject>Attach file</OPFMessageCopySubject>
  <OPFMessageCopyAttachmentList xml:space="preserve">
    <messageAttachment xml:space="preserve"
      OPFAttachmentName="data.bin"
      OPFAttachmentURL="data.bin" />
  </OPFMessageCopyAttachmentList>
</email></emails>"""
        att_path = "Accounts/a/com.microsoft.__Messages/Inbox/data.bin"
        result = _extract_from_archive(
            tmp_path,
            "attach_url_collision.olm",
            xml_content,
            attachments={att_path: b"binary data here"},
        )

        assert len(result) == 1
        assert result[0][0] == "data.bin"
        assert result[0][1] == b"binary data here"

    def test_extract_attachment_skips_unnamed(self, tmp_path: Path):
        """Attachments without a name are skipped."""
        xml_content = b"""<?xml version="1.0"?>
<emails><email>
  <OPFMessageCopySentTime>2025-01-01T00:00:00</OPFMessageCopySentTime>
  <OPFMessageCopyAttachmentList>
    <messageAttachment>
      <OPFAttachmentContentData>dGVzdA==</OPFAttachmentContentData>
    </messageAttachment>
  </OPFMessageCopyAttachmentList>
</email></emails>"""
        result = _extract_from_archive(tmp_path, "noname.olm", xml_content)
        assert result == []

    def test_extract_attachment_invalid_xml(self, tmp_path: Path):
        """Malformed XML returns empty list."""
        result = _extract_from_archive(tmp_path, "badxml.olm", b"<email")
        assert result == []

    def test_extract_attachment_invalid_base64(self, tmp_path: Path):
        """Invalid base64 is handled gracefully; fallback to URL path."""
        xml_content = b"""<?xml version="1.0"?>
<emails><email>
  <OPFMessageCopySentTime>2025-01-01T00:00:00</OPFMessageCopySentTime>
  <OPFMessageCopyAttachmentList>
    <messageAttachment>
      <OPFAttachmentName>bad.txt</OPFAttachmentName>
      <OPFAttachmentContentData>!!!not_base64!!!</OPFAttachmentContentData>
    </messageAttachment>
  </OPFMessageCopyAttachmentList>
</email></emails>"""
        result = _extract_from_archive(tmp_path, "badb64.olm", xml_content)
        # Invalid base64 should be logged but not crash; no URL fallback so empty
        assert result == []

    def test_parse_olm_with_extract_attachments(self, tmp_path: Path):
        """parse_olm with extract_attachments=True populates attachment_contents."""
        content = b"attachment data"
        b64 = base64.b64encode(content).decode()
        xml_content = f"""<?xml version="1.0"?>
<emails><email>
  <OPFMessageCopySentTime>2025-01-01T00:00:00</OPFMessageCopySentTime>
  <OPFMessageCopySubject>With attach</OPFMessageCopySubject>
  <OPFMessageCopyAttachmentList>
    <messageAttachment>
      <OPFAttachmentName>file.dat</OPFAttachmentName>
      <OPFAttachmentContentData>{b64}</OPFAttachmentContentData>
    </messageAttachment>
  </OPFMessageCopyAttachmentList>
</email></emails>""".encode()
        archive = tmp_path / "with_attach.olm"
        xml_path = "Accounts/a/com.microsoft.__Messages/Inbox/msg.xml"
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr(xml_path, xml_content)

        emails = list(parse_olm(str(archive), extract_attachments=True))
        assert len(emails) == 1
        assert len(emails[0].attachment_contents) == 1
        assert emails[0].attachment_contents[0][0] == "file.dat"
        assert emails[0].attachment_contents[0][1] == content
