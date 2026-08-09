"""OLM recipient extraction and source-header fallback cases."""

from mailarium.parse_olm import _parse_email_xml


def test_extract_addresses_includes_display_name():
    """Addresses include display name in 'Name <email>' format."""
    xml = b"""<?xml version="1.0"?>
<emails><email>
  <OPFMessageCopySentTime>2025-01-01T00:00:00</OPFMessageCopySentTime>
  <OPFMessageCopySubject>Name test</OPFMessageCopySubject>
  <OPFMessageCopyToAddresses>
    <emailAddress>
      <OPFContactEmailAddressName>Alice Wonderland</OPFContactEmailAddressName>
      <OPFContactEmailAddressAddress>employee@example.test</OPFContactEmailAddressAddress>
    </emailAddress>
  </OPFMessageCopyToAddresses>
</email></emails>"""

    parsed = _parse_email_xml(xml, "Accounts/a/com.microsoft.__Messages/Inbox/msg.xml")
    assert parsed is not None
    assert parsed.to == ["Alice Wonderland <employee@example.test>"]


def test_extract_addresses_fuzzy_tags():
    """Address extraction works even with non-standard child element names."""
    xml = b"""<?xml version="1.0"?>
<emails><email>
  <OPFMessageCopySentTime>2025-01-01T00:00:00</OPFMessageCopySentTime>
  <OPFMessageCopySubject>Fuzzy test</OPFMessageCopySubject>
  <OPFMessageCopyToAddresses>
    <recipient>
      <recipientName>Charlie Brown</recipientName>
      <recipientAddress>charlie@example.com</recipientAddress>
    </recipient>
  </OPFMessageCopyToAddresses>
</email></emails>"""

    parsed = _parse_email_xml(xml, "Accounts/a/com.microsoft.__Messages/Sent Items/msg.xml")
    assert parsed is not None
    assert parsed.to == ["Charlie Brown <charlie@example.com>"]


def test_sent_items_sender_from_from_addresses():
    """Sent Items without SenderAddress/SenderName get sender from FromAddresses."""
    xml = b"""<?xml version="1.0"?>
<emails><email>
  <OPFMessageCopySentTime>2025-01-01T00:00:00</OPFMessageCopySentTime>
  <OPFMessageCopySubject>Sent item</OPFMessageCopySubject>
  <OPFMessageCopyFromAddresses>
    <emailAddress>
      <OPFContactEmailAddressName>Target Person</OPFContactEmailAddressName>
      <OPFContactEmailAddressAddress>sender.one@example.com</OPFContactEmailAddressAddress>
    </emailAddress>
  </OPFMessageCopyFromAddresses>
  <OPFMessageCopyToAddresses>
    <emailAddress>
      <OPFContactEmailAddressName>Recipient</OPFContactEmailAddressName>
      <OPFContactEmailAddressAddress>recipient@example.com</OPFContactEmailAddressAddress>
    </emailAddress>
  </OPFMessageCopyToAddresses>
</email></emails>"""

    parsed = _parse_email_xml(xml, "Accounts/a/com.microsoft.__Messages/Sent Items/msg.xml")
    assert parsed is not None
    assert parsed.sender_name == "Target Person"
    assert parsed.sender_email == "sender.one@example.com"
    assert parsed.to == ["Recipient <recipient@example.com>"]


def test_sent_items_attribute_format_addresses():
    """Sent Items with addresses in XML attributes (real-world OLM format)."""
    xml = b"""<?xml version="1.0"?>
<emails xml:space="preserve" elementCount="1"><email xml:space="preserve">
  <OPFMessageCopySentTime>2025-12-05T12:51:03</OPFMessageCopySentTime>
  <OPFMessageCopySubject>Sprachkurs Lautstaerke</OPFMessageCopySubject>
  <OPFMessageCopyCCAddresses xml:space="preserve">
    <emailAddress xml:space="preserve"
      OPFContactEmailAddressAddress="cc.one@example.com"
      OPFContactEmailAddressName="CC, One"
      OPFContactEmailAddressType="0"></emailAddress>
  </OPFMessageCopyCCAddresses>
  <OPFMessageCopyDisplayTo xml:space="preserve">Kobler, Sabrina</OPFMessageCopyDisplayTo>
  <OPFMessageCopyFromAddresses xml:space="preserve">
    <emailAddress xml:space="preserve"
      OPFContactEmailAddressAddress="sender.one@example.com"
      OPFContactEmailAddressName="Sender, One"
      OPFContactEmailAddressType="0"></emailAddress>
  </OPFMessageCopyFromAddresses>
  <OPFMessageCopyToAddresses xml:space="preserve">
    <emailAddress xml:space="preserve"
      OPFContactEmailAddressAddress="sabrina@example.com"
      OPFContactEmailAddressName="Kobler, Sabrina"
      OPFContactEmailAddressType="0"></emailAddress>
  </OPFMessageCopyToAddresses>
</email></emails>"""

    parsed = _parse_email_xml(xml, "Accounts/a/com.microsoft.__Messages/Sent Items/msg.xml")
    assert parsed is not None
    assert parsed.sender_name == "Sender, One"
    assert parsed.sender_email == "sender.one@example.com"
    assert parsed.to == ["Kobler, Sabrina <sabrina@example.com>"]
    assert parsed.cc == ["CC, One <cc.one@example.com>"]


def test_display_to_fallback_when_no_to_addresses():
    """Falls back to OPFMessageCopyDisplayTo when ToAddresses is missing."""
    xml = b"""<?xml version="1.0"?>
<emails><email>
  <OPFMessageCopySentTime>2025-01-01T00:00:00</OPFMessageCopySentTime>
  <OPFMessageCopySubject>Display To test</OPFMessageCopySubject>
  <OPFMessageCopyDisplayTo>Mueller, Hans</OPFMessageCopyDisplayTo>
  <OPFMessageCopyFromAddresses xml:space="preserve">
    <emailAddress xml:space="preserve"
      OPFContactEmailAddressAddress="sender@example.com"
      OPFContactEmailAddressName="Sender Name"
      OPFContactEmailAddressType="0"></emailAddress>
  </OPFMessageCopyFromAddresses>
</email></emails>"""

    parsed = _parse_email_xml(xml, "Accounts/a/com.microsoft.__Messages/Sent Items/msg.xml")
    assert parsed is not None
    assert parsed.to == ["Mueller, Hans"]
    assert parsed.sender_email == "sender@example.com"


def test_display_to_fallback_multiple_recipients():
    """OPFMessageCopyDisplayTo with semicolon-separated names."""
    xml = b"""<?xml version="1.0"?>
<emails><email>
  <OPFMessageCopySentTime>2025-01-01T00:00:00</OPFMessageCopySentTime>
  <OPFMessageCopySubject>Multi recipient</OPFMessageCopySubject>
  <OPFMessageCopyDisplayTo>Alice; Bob; Carol</OPFMessageCopyDisplayTo>
</email></emails>"""

    parsed = _parse_email_xml(xml, "Accounts/a/com.microsoft.__Messages/Sent Items/msg.xml")
    assert parsed is not None
    assert parsed.to == ["Alice", "Bob", "Carol"]


def test_display_to_preserves_names_but_recovers_identity_from_source_header():
    xml = b"""<?xml version="1.0"?>
<emails><email>
  <OPFMessageCopySentTime>2025-01-01T00:00:00</OPFMessageCopySentTime>
  <OPFMessageCopySubject>Display To plus source</OPFMessageCopySubject>
  <OPFMessageCopyDisplayTo>Mueller, Hans</OPFMessageCopyDisplayTo>
  <OPFMessageCopySource>From: Sender Name &lt;sender@example.com&gt;
To: "Mueller, Hans" &lt;colleague@example.test&gt;
Subject: Display To plus source

Body.</OPFMessageCopySource>
</email></emails>"""

    parsed = _parse_email_xml(xml, "Accounts/a/com.microsoft.__Messages/Sent Items/msg.xml")
    assert parsed is not None
    assert parsed.to == ["Mueller, Hans"]
    assert parsed.to_identities == ["colleague@example.test"]
    assert parsed.recipient_identity_source == "source_header"
