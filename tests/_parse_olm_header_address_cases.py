# pylint: disable=no-member,c-extension-no-member

"""OLM source-header and structured-address parsing cases."""

from lxml import etree

from mailarium.parse_olm import (
    _extract_email_from_header,
    _extract_header,
    _extract_name_from_header,
    _parse_address_element,
    _parse_address_list,
    _parse_email_xml,
)


def test_extract_header_simple():
    source = "Subject: Hello World\nFrom: test@example.com\n\nBody"
    assert _extract_header(source, "Subject") == "Hello World"


def test_extract_header_with_continuation():
    source = "Subject: This is\n a long subject\nFrom: test@example.com\n\nBody"
    assert _extract_header(source, "Subject") == "This is a long subject"


def test_extract_email_from_header_angle_brackets():
    source = 'From: "Alice Bob" <employee@example.test>\nSubject: Test\n\nBody'
    assert _extract_email_from_header(source, "From") == "employee@example.test"


def test_extract_email_from_header_html_encoded():
    source = 'From: "Alice" &lt;employee@example.test&gt;\nSubject: Test\n\nBody'
    assert _extract_email_from_header(source, "From") == "employee@example.test"


def test_extract_name_from_header_quoted():
    source = 'From: "John, Petra" <petra@example.com>\nSubject: Test\n\nBody'
    assert _extract_name_from_header(source, "From") == "John, Petra"


def test_parse_address_list():
    raw = '"Alice" <alice@example.test>, bob@example.test, "Carol D" <carol@example.test>'
    result = _parse_address_list(raw)
    assert result == ["alice@example.test", "bob@example.test", "carol@example.test"]


def test_parse_address_element_child_elements():
    """_parse_address_element handles child-element format (older OLM)."""
    xml = b"""<emailAddress>
      <OPFContactEmailAddressName>Alice</OPFContactEmailAddressName>
      <OPFContactEmailAddressAddress>employee@example.test</OPFContactEmailAddressAddress>
    </emailAddress>"""
    el = etree.fromstring(xml)
    name, email = _parse_address_element(el)
    assert name == "Alice"
    assert email == "employee@example.test"


def test_parse_address_element_attributes():
    """_parse_address_element handles attribute format (newer OLM / Sent Items)."""
    xml = b"""<emailAddress xml:space="preserve"
      OPFContactEmailAddressAddress="bob@example.com"
      OPFContactEmailAddressName="Bob Smith"
      OPFContactEmailAddressType="0">
    </emailAddress>"""
    el = etree.fromstring(xml)
    name, email = _parse_address_element(el)
    assert name == "Bob Smith"
    assert email == "bob@example.com"


def test_parse_address_element_fuzzy_child_tags():
    """Fuzzy matching works for non-standard child element names."""
    xml = b"""<recipient>
      <displayName>Charlie</displayName>
      <emailAddress>charlie@example.com</emailAddress>
    </recipient>"""
    el = etree.fromstring(xml)
    name, email = _parse_address_element(el)
    assert name == "Charlie"
    assert email == "charlie@example.com"


def test_extract_name_from_header_escaped_quotes():
    source = 'From: "John \\"Johnny\\" Smith" <john@example.com>\n\nBody'
    name = _extract_name_from_header(source, "From")
    assert "Johnny" in name
    assert "John" in name


def test_extract_name_from_header_unquoted():
    source = "From: John Smith <john@example.com>\n\nBody"
    name = _extract_name_from_header(source, "From")
    assert name == "John Smith"


def test_sender_email_normalized_lowercase():
    """Sender email from OLM XML should be lowercased."""
    xml = b"""<?xml version="1.0"?>
    <email>
      <OPFMessageCopySubject>Test</OPFMessageCopySubject>
      <OPFMessageCopySentTime>2024-01-01T00:00:00</OPFMessageCopySentTime>
      <OPFMessageCopySenderAddress>John.Smith@Example.COM</OPFMessageCopySenderAddress>
      <OPFMessageCopySenderName>John Smith</OPFMessageCopySenderName>
      <OPFMessageCopyBody>Body</OPFMessageCopyBody>
    </email>"""
    email = _parse_email_xml(xml, "test.xml")
    assert email.sender_email == "john.smith@example.com"
