"""Shared test records and assertions for OLM body normalization."""

from __future__ import annotations

from dataclasses import dataclass

from mailarium.parse_olm import Email
from mailarium.parse_olm_normalization import BODY_NORMALIZATION_VERSION


@dataclass(frozen=True)
class CleanBodyExpectation:
    clean_body: str | None = None
    source: str | None = None
    tracks_version: bool = False


@dataclass(frozen=True)
class CleanBodyCase:
    body_text: str
    expectation: CleanBodyExpectation = CleanBodyExpectation()
    body_html: str = ""
    subject: str = "Test"
    email_type: str | None = None
    retained_text: str | None = None


def email_with_body(*, body_text: str, body_html: str = "", subject: str = "Test") -> Email:
    """Create a minimal inbox email for body-normalization cases."""
    return Email(
        message_id="<m@test>",
        subject=subject,
        sender_name="",
        sender_email="",
        to=[],
        cc=[],
        bcc=[],
        date="",
        body_text=body_text,
        body_html=body_html,
        folder="Inbox",
        has_attachments=False,
    )


def assert_clean_body_normalization(email: Email, expectation: CleanBodyExpectation) -> None:
    """Check the shared normalized body, source, and version contract."""
    if expectation.clean_body is not None:
        assert email.clean_body == expectation.clean_body
    if expectation.source is not None:
        assert email.clean_body_source == expectation.source
    if expectation.tracks_version:
        assert email.body_normalization_version == BODY_NORMALIZATION_VERSION
