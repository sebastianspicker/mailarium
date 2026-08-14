"""OLM attachment metadata extraction cases."""

from mailarium.parse_olm import _parse_email_xml


class TestExtractAttachments:
    def test_extracts_attachment_metadata(self):
        xml = b"""<?xml version="1.0"?>
<emails><email>
  <OPFMessageCopySentTime>2025-01-01T00:00:00</OPFMessageCopySentTime>
  <OPFMessageCopySubject>Attach test</OPFMessageCopySubject>
  <OPFMessageCopyAttachmentList>
    <messageAttachment>
      <OPFAttachmentName>file.pdf</OPFAttachmentName>
      <OPFAttachmentContentType>application/pdf</OPFAttachmentContentType>
      <OPFAttachmentContentFileSize>2048</OPFAttachmentContentFileSize>
    </messageAttachment>
  </OPFMessageCopyAttachmentList>
</email></emails>"""
        parsed = _parse_email_xml(xml, "Accounts/a/com.microsoft.__Messages/Inbox/msg.xml")
        assert parsed is not None
        assert parsed.has_attachments is True
        assert parsed.attachment_names == ["file.pdf"]
        assert len(parsed.attachments) == 1
        assert parsed.attachments[0]["name"] == "file.pdf"
        assert parsed.attachments[0]["size"] == 2048

    def test_extracts_namespaced_attachment(self):
        xml = b"""<?xml version="1.0"?>
<email xmlns="http://schemas.microsoft.com/outlook/mac/2011">
  <OPFMessageCopySentTime>2025-01-01T00:00:00</OPFMessageCopySentTime>
  <OPFMessageCopySubject>NS Attach</OPFMessageCopySubject>
  <OPFMessageCopyAttachmentList>
    <messageAttachment>
      <OPFAttachmentName>image.png</OPFAttachmentName>
      <OPFAttachmentContentType>image/png</OPFAttachmentContentType>
      <OPFAttachmentContentID>cid123</OPFAttachmentContentID>
    </messageAttachment>
  </OPFMessageCopyAttachmentList>
</email>"""
        parsed = _parse_email_xml(xml, "Accounts/a/com.microsoft.__Messages/Inbox/msg.xml")
        assert parsed is not None
        assert parsed.has_attachments is True
        assert parsed.attachments[0]["content_id"] == "cid123"
        assert parsed.attachments[0]["is_inline"] is True
