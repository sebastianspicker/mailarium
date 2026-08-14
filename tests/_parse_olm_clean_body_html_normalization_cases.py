"""HTML source detection and representation-selection normalization cases."""

from __future__ import annotations

import pytest

from ._parse_olm_clean_body_normalization_support import (
    CleanBodyCase,
    CleanBodyExpectation,
    assert_clean_body_normalization,
    email_with_body,
)

_HTML_CASES = [
    pytest.param(
        CleanBodyCase(
            body_text="<html><body><p>Hello</p></body></html>",
            expectation=CleanBodyExpectation(clean_body="Hello", source="body_text_html"),
        ),
        id="clean_body_html_in_body_text_field",
    ),
    pytest.param(
        CleanBodyCase(
            body_text=(
                "Visible summary.\n\n"
                "From: Alice <employee@example.test>\n"
                "Sent: Monday, January 1, 2025 10:00 AM\n"
                "To: Bob <bob@example.com>\n"
                "Subject: RE: Test\n\n"
                "> Prior content"
            ),
            body_html="<div><p>Visible summary.</p></div>",
            expectation=CleanBodyExpectation(clean_body="Visible summary.", source="body_html", tracks_version=True),
        ),
        id="clean_body_prefers_cleaner_html_representation",
    ),
]


class TestCleanBodyHtml:
    @pytest.mark.parametrize("case", _HTML_CASES)
    def test_clean_body_html_source_selection(self, case: CleanBodyCase) -> None:
        email = email_with_body(body_text=case.body_text, body_html=case.body_html)
        assert_clean_body_normalization(email, case.expectation)
