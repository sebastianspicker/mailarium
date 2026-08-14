"""Signature, footer, and legal-disclaimer body-normalization cases."""

from __future__ import annotations

import pytest

from ._parse_olm_clean_body_normalization_support import (
    CleanBodyCase,
    CleanBodyExpectation,
    assert_clean_body_normalization,
    email_with_body,
)

_SIGNATURE_CASES = [
    pytest.param(
        CleanBodyCase(
            body_text="See you tomorrow.\n\nSent from my iPhone",
            expectation=CleanBodyExpectation(clean_body="See you tomorrow.", source="body_text", tracks_version=True),
        ),
        id="clean_body_strips_mobile_signature_in_normalized_body",
    ),
    pytest.param(
        CleanBodyCase(
            body_text="I'll handle it.\n\nBest regards,\nAlice Smith\nManager",
            expectation=CleanBodyExpectation(clean_body="I'll handle it."),
        ),
        id="clean_body_strips_closing_signature_in_normalized_body",
    ),
    pytest.param(
        CleanBodyCase(
            body_text="Just a regular email without a signature.",
            expectation=CleanBodyExpectation(clean_body="Just a regular email without a signature."),
        ),
        id="clean_body_keeps_regular_prose_without_signature_marker",
    ),
    pytest.param(
        CleanBodyCase(
            body_text="Please see the attached file.\n\nGet Outlook for iOS",
            expectation=CleanBodyExpectation(clean_body="Please see the attached file.", tracks_version=True),
        ),
        id="clean_body_strips_get_outlook_ios_footer_in_normalized_body",
    ),
]


_LEGAL_DISCLAIMER_CASES = [
    pytest.param(
        CleanBodyCase(
            body_text=(
                "Action items are attached.\n\n"
                "This email and any attachments are confidential and intended only for the named recipient.\n"
                "If you are not the intended recipient, please notify the sender and delete this email.\n"
                "Any unauthorized review, use, disclosure, or distribution is prohibited."
            ),
            expectation=CleanBodyExpectation(clean_body="Action items are attached.", tracks_version=True),
        ),
        id="clean_body_strips_multiline_legal_disclaimer_tail",
    ),
    pytest.param(
        CleanBodyCase(
            body_text="Status report attached.\n\nConfidentiality notice: This email may contain privileged information.",
            retained_text="Confidentiality notice",
        ),
        id="clean_body_keeps_single_line_confidentiality_notice",
    ),
]


class TestCleanBodySignatures:
    @pytest.mark.parametrize("case", _SIGNATURE_CASES)
    def test_clean_body_signature_and_footer_handling(self, case: CleanBodyCase) -> None:
        email = email_with_body(body_text=case.body_text)
        assert_clean_body_normalization(email, case.expectation)


class TestCleanBodyLegalDisclaimers:
    @pytest.mark.parametrize("case", _LEGAL_DISCLAIMER_CASES)
    def test_clean_body_legal_disclaimer_handling(self, case: CleanBodyCase) -> None:
        email = email_with_body(body_text=case.body_text)
        assert_clean_body_normalization(email, case.expectation)
        if case.retained_text is not None:
            assert case.retained_text in email.clean_body
