# pylint: disable=no-member,c-extension-no-member

"""OLM attachment-field lookup cases."""

from lxml import etree

from mailarium.olm_xml_helpers import _extract_attachment_field
from mailarium.parse_olm import _NS_OUTLOOK


class TestExtractAttachmentFieldNamespaced:
    def test_attachment_field_namespaced_child(self):
        xml = b"""<messageAttachment xmlns="http://schemas.microsoft.com/outlook/mac/2011">
  <OPFAttachmentName>report.pdf</OPFAttachmentName>
  <OPFAttachmentContentType>application/pdf</OPFAttachmentContentType>
  <OPFAttachmentContentFileSize>1024</OPFAttachmentContentFileSize>
</messageAttachment>"""
        el = etree.fromstring(xml)
        ns = _NS_OUTLOOK
        name = _extract_attachment_field(el, ns, "OPFAttachmentName", attr_hint="name")
        assert name == "report.pdf"

    def test_attachment_field_attribute_fallback(self):
        """When child element is missing, fall back to attribute matching."""
        xml = b'<messageAttachment OPFAttachmentName="doc.docx"></messageAttachment>'
        el = etree.fromstring(xml)
        name = _extract_attachment_field(el, {}, "OPFAttachmentName", attr_hint="name")
        assert name == "doc.docx"
