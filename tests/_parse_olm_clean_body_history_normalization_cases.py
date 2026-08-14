"""Reply, forward, and original-message body-normalization cases."""

from __future__ import annotations

import pytest

from ._parse_olm_clean_body_normalization_support import (
    CleanBodyCase,
    CleanBodyExpectation,
    assert_clean_body_normalization,
    email_with_body,
)

_REPLY_HISTORY_CASES = [
    pytest.param(
        CleanBodyCase(
            subject="RE: Project update",
            body_text=(
                "Latest status is below.\n\n----- Original Message -----\nFrom: Alice\nSubject: Project update\n\nPrior body."
            ),
            email_type="reply",
            expectation=CleanBodyExpectation(clean_body="Latest status is below.", tracks_version=True),
        ),
        id="clean_body_strips_reply_quote_tail_before_persistence",
    ),
    pytest.param(
        CleanBodyCase(
            subject="RE: Status",
            body_text=(
                "Latest answer.\n\n"
                "From: Alice <employee@example.test>\n"
                "Sent: Monday, January 1, 2025 10:00 AM\n"
                "To: Bob <bob@example.com>\n"
                "Subject: Status"
            ),
            email_type="reply",
            expectation=CleanBodyExpectation(clean_body="Latest answer.", tracks_version=True),
        ),
        id="clean_body_strips_reply_header_only_tail_before_persistence",
    ),
    pytest.param(
        CleanBodyCase(
            subject="FW: Status",
            body_text=(
                "Please see below.\n\n"
                "From: Alice <employee@example.test>\n"
                "Sent: Monday, January 1, 2025 10:00 AM\n"
                "To: Bob <bob@example.com>\n"
                "Subject: Status\n\n"
                "Prior body content."
            ),
            email_type="forward",
            expectation=CleanBodyExpectation(clean_body="Please see below."),
        ),
        id="clean_body_strips_reply_header_block_after_intro_before_persistence",
    ),
    pytest.param(
        CleanBodyCase(
            subject="AW: Status",
            body_text="",
            body_html=(
                "<div>Aktueller Stand unten.</div><div><br></div>"
                "<div>Von: Alice &lt;employee@example.test&gt;</div>"
                "<div>Gesendet: Montag, 1. Januar 2025 10:00</div>"
                "<div>An: Bob &lt;bob@example.com&gt;</div><div>Betreff: Status</div>"
                "<div><br></div><div>Vorheriger Inhalt.</div>"
            ),
            email_type="reply",
            expectation=CleanBodyExpectation(clean_body="Aktueller Stand unten.", source="body_html"),
        ),
        id="clean_body_strips_html_reply_header_block_after_intro",
    ),
    pytest.param(
        CleanBodyCase(
            subject="AW: Status",
            body_text=(
                "Aktueller Stand unten.\n\n"
                "Von: Alice <employee@example.test>\n"
                "Gesendet: Montag, 1. Januar 2025 10:00\n"
                "An: Bob <bob@example.com>\n"
                "Betreff: Status"
            ),
            email_type="reply",
            expectation=CleanBodyExpectation(clean_body="Aktueller Stand unten.", tracks_version=True),
        ),
        id="clean_body_strips_german_reply_header_tail_before_persistence",
    ),
    pytest.param(
        CleanBodyCase(
            subject="AW: Status",
            body_text=(
                "Aktueller Stand unten.\n\nViele Grüße\nAlice\n\n"
                "Von: Bob <bob@example.com>\nGesendet: Montag, 1. Januar 2025 10:00\n"
                "An: Alice <employee@example.test>\nBetreff: Status\n\nVorheriger Inhalt."
            ),
            expectation=CleanBodyExpectation(clean_body="Aktueller Stand unten."),
        ),
        id="clean_body_strips_reply_header_tail_after_signature_prelude",
    ),
    pytest.param(
        CleanBodyCase(
            subject="AW: Status",
            body_text=(
                "Danke, erledigt.\n\nProf. Beispiel\nLeitung IT\n\n-----Original-Nachricht-----\n"
                "Von: Alice <employee@example.test>\nGesendet: Montag, 1. Januar 2025 10:00\n"
                "An: Bob <bob@example.com>\nBetreff: Status\n\nVoriger Inhalt."
            ),
            expectation=CleanBodyExpectation(clean_body="Danke, erledigt.\n\nProf. Beispiel\nLeitung IT"),
        ),
        id="clean_body_strips_reply_header_tail_from_original_nachricht_separator",
    ),
    pytest.param(
        CleanBodyCase(
            subject="RE: Status",
            body_text=(
                "Erledigt.\n\nDr. employee\nLeitung IT\nBeispielweg 10\n12345 Musterstadt\n\n"
                "Von: Bob <bob@example.com>\nGesendet: Montag, 1. Januar 2025 10:00\n"
                "An: Alice <employee@example.test>\nBetreff: Status\n\nVoriger Inhalt."
            ),
            expectation=CleanBodyExpectation(
                clean_body="Erledigt.\n\nDr. employee\nLeitung IT\nBeispielweg 10\n12345 Musterstadt"
            ),
        ),
        id="clean_body_strips_reply_header_tail_after_long_signature_prelude",
    ),
    pytest.param(
        CleanBodyCase(
            subject="RE: Status",
            body_text=(
                "Resposta atual.\n\nDe: Alice <employee@example.test>\n"
                "Enviado: segunda-feira, 1 de janeiro de 2025 10:00\n"
                "Para: Bob <bob@example.com>\nAssunto: Status"
            ),
            email_type="reply",
            expectation=CleanBodyExpectation(clean_body="Resposta atual.", tracks_version=True),
        ),
        id="clean_body_strips_portuguese_reply_header_tail_before_persistence",
    ),
    pytest.param(
        CleanBodyCase(
            subject="RE: Status",
            body_text=(
                "Aktualna odpowiedz.\n\nOd: Alice <employee@example.test>\n"
                "Wyslano: poniedzialek, 1 stycznia 2025 10:00\n"
                "Do: Bob <bob@example.com>\nTemat: Status"
            ),
            email_type="reply",
            expectation=CleanBodyExpectation(clean_body="Aktualna odpowiedz.", tracks_version=True),
        ),
        id="clean_body_strips_polish_reply_header_tail_before_persistence",
    ),
]


_LEADING_FORWARD_CASES = [
    pytest.param(
        CleanBodyCase(
            subject="FW: Status",
            body_text=(
                "From: Alice <employee@example.test>\nSent: Monday, January 1, 2025 10:00 AM\n"
                "To: Bob <bob@example.com>\nSubject: Status\n\nForwarded content starts here."
            ),
            expectation=CleanBodyExpectation(clean_body="Forwarded content starts here."),
        ),
        id="clean_body_strips_leading_forward_header_block_and_keeps_forwarded_content",
    ),
    pytest.param(
        CleanBodyCase(
            subject="FW: Status",
            body_text=(
                "________________________________\nFrom: Alice <employee@example.test>\n"
                "Sent: Monday, January 1, 2025 10:00 AM\nTo: Bob <bob@example.com>\n"
                "Subject: Status\n\nForwarded content starts here."
            ),
            expectation=CleanBodyExpectation(clean_body="Forwarded content starts here."),
        ),
        id="clean_body_strips_leading_forward_header_block_after_outlook_separator",
    ),
]


_ORIGINAL_CONTENT_CASES = [
    pytest.param(
        CleanBodyCase(
            subject="Project archive note",
            body_text="Reference below.\n\n----- Original Message -----\nThis separator is part of the saved note.",
            email_type="original",
            retained_text="----- Original Message -----",
        ),
        id="clean_body_keeps_separator_text_for_original_email",
    ),
    pytest.param(
        CleanBodyCase(
            subject="Archive note",
            body_text=(
                "Reference block below.\n\nFrom: Alice <employee@example.test>\n"
                "Sent: Monday, January 1, 2025 10:00 AM\nTo: Bob <bob@example.com>\nSubject: Status"
            ),
            email_type="original",
            retained_text="From: Alice <employee@example.test>",
        ),
        id="clean_body_keeps_headerish_tail_for_original_email",
    ),
    pytest.param(
        CleanBodyCase(
            subject="Archivnotiz",
            body_text=(
                "Referenzblock unten.\n\nVon: Alice <employee@example.test>\n"
                "Gesendet: Montag, 1. Januar 2025 10:00\nAn: Bob <bob@example.com>\nBetreff: Status"
            ),
            email_type="original",
            retained_text="Von: Alice <employee@example.test>",
        ),
        id="clean_body_keeps_german_headerish_tail_for_original_email",
    ),
]


class TestCleanBodyEnglishReplyHeaders:
    @pytest.mark.parametrize("case", _REPLY_HISTORY_CASES[:4])
    def test_clean_body_strips_recognized_reply_and_forward_history(self, case: CleanBodyCase) -> None:
        email = email_with_body(body_text=case.body_text, body_html=case.body_html, subject=case.subject)
        assert email.email_type == case.email_type
        assert_clean_body_normalization(email, case.expectation)

    @pytest.mark.parametrize("case", _LEADING_FORWARD_CASES)
    def test_clean_body_keeps_forwarded_content_after_leading_headers(self, case: CleanBodyCase) -> None:
        email = email_with_body(body_text=case.body_text, subject=case.subject)
        assert_clean_body_normalization(email, case.expectation)

    @pytest.mark.parametrize("case", _ORIGINAL_CONTENT_CASES[:2])
    def test_clean_body_conservatively_retains_original_message_content(self, case: CleanBodyCase) -> None:
        email = email_with_body(body_text=case.body_text, subject=case.subject)
        assert email.email_type == case.email_type
        assert case.retained_text in email.clean_body


class TestCleanBodyGermanReplyHeaders:
    @pytest.mark.parametrize("case", _REPLY_HISTORY_CASES[4:8])
    def test_clean_body_strips_recognized_reply_history(self, case: CleanBodyCase) -> None:
        email = email_with_body(body_text=case.body_text, body_html=case.body_html, subject=case.subject)
        if case.email_type is not None:
            assert email.email_type == case.email_type
        assert_clean_body_normalization(email, case.expectation)

    @pytest.mark.parametrize("case", _ORIGINAL_CONTENT_CASES[2:])
    def test_clean_body_conservatively_retains_original_message_content(self, case: CleanBodyCase) -> None:
        email = email_with_body(body_text=case.body_text, subject=case.subject)
        assert email.email_type == case.email_type
        assert case.retained_text in email.clean_body


class TestCleanBodyNonEnglishReplyHeaders:
    @pytest.mark.parametrize("case", _REPLY_HISTORY_CASES[8:])
    def test_clean_body_strips_recognized_reply_history(self, case: CleanBodyCase) -> None:
        email = email_with_body(body_text=case.body_text, body_html=case.body_html, subject=case.subject)
        assert email.email_type == case.email_type
        assert_clean_body_normalization(email, case.expectation)
