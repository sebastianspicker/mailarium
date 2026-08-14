"""OLM subject-based email-type classification cases."""

from mailarium.parse_olm import Email


def _email_for_subject(message_id: str, subject: str) -> Email:
    """Create the minimal email used to classify standard reply/forward prefixes."""
    return Email(
        message_id=message_id,
        subject=subject,
        sender_name="",
        sender_email="a@example.test",
        to=[],
        cc=[],
        bcc=[],
        date="",
        body_text="",
        body_html="",
        folder="Inbox",
        has_attachments=False,
    )


def test_email_type_original():
    email = _email_for_subject("1", "Hello World")
    assert email.email_type == "original"
    assert email.base_subject == "Hello World"


def test_email_type_reply_re():
    email = _email_for_subject("2", "RE: Hello World")
    assert email.email_type == "reply"
    assert email.base_subject == "Hello World"


def test_email_type_reply_aw():
    email = _email_for_subject("3", "AW: AW: Betreff")
    assert email.email_type == "reply"
    assert email.base_subject == "Betreff"


def test_email_type_forward_fw():
    email = _email_for_subject("4", "FW: Some Message")
    assert email.email_type == "forward"
    assert email.base_subject == "Some Message"


def test_email_type_forward_wg():
    email = _email_for_subject("5", "WG: Weitergeleitete Nachricht")
    assert email.email_type == "forward"
    assert email.base_subject == "Weitergeleitete Nachricht"


def test_base_subject_strips_mixed_prefixes():
    email = _email_for_subject("6", "RE: FW: AW: WG: Deep Thread")
    assert email.base_subject == "Deep Thread"
