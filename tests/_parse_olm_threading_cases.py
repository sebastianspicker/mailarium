"""OLM message-linkage and reference-chain parsing cases."""

from mailarium.olm_xml_helpers import _parse_references
from mailarium.parse_olm import _parse_email_xml


def test_parse_email_xml_threading_fields():
    """Parse conversation_id, in_reply_to, references, priority, is_read from XML."""
    xml = b"""<?xml version="1.0"?>
<emails><email>
  <OPFMessageCopySentTime>2025-01-01T00:00:00</OPFMessageCopySentTime>
  <OPFMessageCopySubject>RE: Thread test</OPFMessageCopySubject>
  <OPFMessageCopyExchangeConversationId>AAQkADc1NjJk</OPFMessageCopyExchangeConversationId>
  <OPFMessageCopyInReplyTo>&lt;parent-msg-id@example.com&gt;</OPFMessageCopyInReplyTo>
  <OPFMessageCopyReferences>&lt;root@example.com&gt; &lt;parent@example.com&gt;</OPFMessageCopyReferences>
  <OPFMessageGetPriority>2</OPFMessageGetPriority>
  <OPFMessageGetIsRead>false</OPFMessageGetIsRead>
</email></emails>"""

    parsed = _parse_email_xml(xml, "Accounts/a/com.microsoft.__Messages/Inbox/msg.xml")
    assert parsed is not None
    assert parsed.conversation_id == "AAQkADc1NjJk"
    assert parsed.in_reply_to == "<parent-msg-id@example.com>"
    assert parsed.references == ["root@example.com", "parent@example.com"]
    assert parsed.priority == 2
    assert parsed.is_read is False
    assert parsed.email_type == "reply"
    assert parsed.base_subject == "Thread test"


def test_parse_email_xml_defaults_for_new_fields():
    """New fields default sensibly when not present in XML."""
    xml = b"""<?xml version="1.0"?>
<emails><email>
  <OPFMessageCopySentTime>2025-01-01T00:00:00</OPFMessageCopySentTime>
  <OPFMessageCopySubject>Simple email</OPFMessageCopySubject>
</email></emails>"""

    parsed = _parse_email_xml(xml, "Accounts/a/com.microsoft.__Messages/Inbox/msg.xml")
    assert parsed is not None
    assert parsed.conversation_id == ""
    assert parsed.in_reply_to == ""
    assert parsed.references == []
    assert parsed.priority == 0
    assert parsed.is_read is True
    assert parsed.email_type == "original"


def test_parse_email_xml_threading_from_source_headers():
    """Extract In-Reply-To and References from raw RFC 2822 source as fallback."""
    xml = b"""<?xml version="1.0"?>
<emails><email>
  <OPFMessageCopySentTime>2025-01-01T00:00:00</OPFMessageCopySentTime>
  <OPFMessageCopySource>Subject: RE: From source
In-Reply-To: &lt;parent-id@example.com&gt;
References: &lt;root-id@example.com&gt; &lt;parent-id@example.com&gt;

Body text.</OPFMessageCopySource>
</email></emails>"""

    parsed = _parse_email_xml(xml, "Accounts/a/com.microsoft.__Messages/Inbox/msg.xml")
    assert parsed is not None
    assert parsed.in_reply_to == "parent-id@example.com"
    assert parsed.references == ["root-id@example.com", "parent-id@example.com"]


def test_parse_references_angle_brackets():
    assert _parse_references("<a@example.test> <c@example.test>") == ["a@example.test", "c@example.test"]


def test_parse_references_empty():
    assert _parse_references("") == []
    assert _parse_references("   ") == []


def test_parse_references_mixed_bracketed_and_bare():
    raw = "<id1@example.test> bare@example.test <id3@example.test>"
    result = _parse_references(raw)
    assert "id1@example.test" in result
    assert "bare@example.test" in result
    assert "id3@example.test" in result
    assert len(result) == 3


def test_parse_references_bare_only():
    raw = "id1@example.test id2@example.test"
    result = _parse_references(raw)
    assert result == ["id1@example.test", "id2@example.test"]


def test_parse_references_no_duplicates():
    raw = "<id1@example.test> id1@example.test"
    result = _parse_references(raw)
    assert result == ["id1@example.test"]
