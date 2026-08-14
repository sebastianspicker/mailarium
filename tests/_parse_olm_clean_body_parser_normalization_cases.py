"""Line parser parity and performance contracts for body normalization."""

from __future__ import annotations

import time

import pytest

from mailarium.parse_olm_normalization import (
    _has_newsletter_hint,
    _has_normalized_quoted_separator,
    _has_sent_from_footer,
    _is_normalized_quoted_separator,
    _is_normalized_reply_header_line,
    _is_outlook_separator_line,
    _normalized_body_noise_score,
)


@pytest.mark.parametrize(
    ("parser", "value", "expected"),
    [
        pytest.param(_is_normalized_reply_header_line, "From: Alice", True, id="english-reply-header"),
        pytest.param(_is_normalized_reply_header_line, "Envoyée: vendredi", True, id="french-reply-header"),
        pytest.param(_is_normalized_reply_header_line, "Wysłano: poniedziałek", True, id="polish-reply-header"),
        pytest.param(_is_normalized_reply_header_line, "From:", False, id="empty-header-value"),
        pytest.param(
            _is_normalized_quoted_separator,
            "----- Original Message -----",
            True,
            id="english-original-message-separator",
        ),
        pytest.param(
            _is_normalized_quoted_separator,
            "-- Ursprüngliche Nachricht",
            True,
            id="german-original-message-separator",
        ),
        pytest.param(
            _has_normalized_quoted_separator,
            "Lead\n-- Forwarded message --\nBody",
            True,
            id="forwarded-message-in-body",
        ),
        pytest.param(_is_outlook_separator_line, "__________", True, id="outlook-separator"),
        pytest.param(_is_outlook_separator_line, "_________", False, id="short-underscore-run"),
        pytest.param(_has_sent_from_footer, "Body\nSent from my iPhone", True, id="iphone-footer"),
        pytest.param(_has_newsletter_hint, "To stop these messages, unsubscribe here.", True, id="unsubscribe-hint"),
    ],
)
def test_normalization_line_parsers_preserve_regex_parity(parser, value: str, expected: bool) -> None:
    assert parser(value) is expected


def test_normalization_line_parsers_are_linear_on_adversarial_input() -> None:
    adversarial = ("From-not-a-header " * 20_000) + "\n" + ("_-" * 50_000)
    started = time.perf_counter()
    _normalized_body_noise_score(adversarial)
    assert time.perf_counter() - started < 1.0
