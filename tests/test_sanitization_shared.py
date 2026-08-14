"""Exercises shared text sanitization and privacy guardrails for terminal controls and sensitive content.

It removes display-manipulation characters and applies stricter redaction according to the selected mode.
"""

from mailarium.sanitization import apply_privacy_guardrails, sanitize_untrusted_text


def test_sanitize_untrusted_text_strips_ansi_and_control_chars():
    raw = "normal\x1b[31mRED\x1b[0m\x07\x1ftext"
    clean = sanitize_untrusted_text(raw)

    assert "\x1b" not in clean
    assert "\x07" not in clean
    assert "\x1f" not in clean
    assert "normal" in clean
    assert "RED" in clean


def test_sanitize_untrusted_text_strips_osc_sequences():
    raw = "safe\x1b]8;;https://evil.test\x07click\x1b]8;;\x07end"
    clean = sanitize_untrusted_text(raw)

    assert "\x1b]" not in clean
    assert "evil.test" not in clean
    assert "safe" in clean
    assert "click" in clean


def test_sanitize_untrusted_text_strips_carriage_return():
    raw = "hello\rworld"
    clean = sanitize_untrusted_text(raw)

    assert "\r" not in clean


def test_sanitize_untrusted_text_strips_del_and_c1_controls():
    raw = "ok\x7f\x85text"
    clean = sanitize_untrusted_text(raw)

    assert "\x7f" not in clean
    assert "\x85" not in clean
    assert clean == "oktext"


def test_sanitize_untrusted_text_strips_bidi_controls():
    raw = "abc\u202edef\u2066ghi\u2069"
    clean = sanitize_untrusted_text(raw)

    assert "\u202e" not in clean.lower()
    assert "\u2066" not in clean.lower()
    assert "\u2069" not in clean.lower()
    assert clean == "abcdefghi"


def test_apply_privacy_guardrails_redacts_contact_data_in_contact_redacted_mode():
    payload = {
        "summary": "Please contact employee@example.test at +49 221 1234567 about the process update.",
    }

    redacted, guardrails = apply_privacy_guardrails(payload, privacy_mode="contact_redacted")

    assert redacted["summary"] == "Please contact [REDACTED: email] at [REDACTED: phone] about the process update."
    assert guardrails["privacy_mode"] == "contact_redacted"
    assert guardrails["redaction_summary"]["category_counts"] == {
        "contact": 2,
        "medical": 0,
        "privileged": 0,
        "structured_identity": 0,
    }


def test_apply_privacy_guardrails_redacts_medical_and_privileged_text_in_strict_mode():
    payload = {
        "name": "employee",
        "note": "Medical diagnosis from the physician should stay private.",
        "memo": "Privileged attorney-client strategy note.",
    }

    redacted, guardrails = apply_privacy_guardrails(payload, privacy_mode="strict_redaction")

    assert redacted["name"] == "[REDACTED: participant_identity]"
    assert redacted["note"] == "[REDACTED: sensitive_medical_content]"
    assert redacted["memo"] == "[REDACTED: privileged_content]"
    assert guardrails["redaction_summary"]["category_counts"]["medical"] == 1
    assert guardrails["redaction_summary"]["category_counts"]["privileged"] == 1


def test_apply_privacy_guardrails_prioritizes_structured_identity_over_sensitive_content():
    payload = {"name": "Privileged diagnosis for employee@example.test"}

    redacted, guardrails = apply_privacy_guardrails(payload, privacy_mode="strict_redaction")

    assert redacted["name"] == "[REDACTED: participant_identity]"
    assert guardrails["redaction_summary"]["category_counts"] == {
        "contact": 0,
        "medical": 0,
        "privileged": 0,
        "structured_identity": 1,
    }


def test_apply_privacy_guardrails_prioritizes_privileged_over_medical_content():
    payload = {"memo": "Privileged medical diagnosis for employee@example.test"}

    redacted, guardrails = apply_privacy_guardrails(payload, privacy_mode="strict_redaction")

    assert redacted["memo"] == "[REDACTED: privileged_content]"
    assert guardrails["redaction_summary"]["category_counts"] == {
        "contact": 0,
        "medical": 0,
        "privileged": 1,
        "structured_identity": 0,
    }


def test_apply_privacy_guardrails_prioritizes_medical_content_over_contact_data():
    payload = {"note": "Medical diagnosis for employee@example.test at +49 221 1234567"}

    redacted, guardrails = apply_privacy_guardrails(payload, privacy_mode="strict_redaction")

    assert redacted["note"] == "[REDACTED: sensitive_medical_content]"
    assert guardrails["redaction_summary"]["category_counts"] == {
        "contact": 0,
        "medical": 1,
        "privileged": 0,
        "structured_identity": 0,
    }


def test_apply_privacy_guardrails_sanitizes_before_medical_classification():
    payload = {"note": "med\x1b[31mical\x1b[0m update for employee@example.test"}

    redacted, guardrails = apply_privacy_guardrails(payload, privacy_mode="strict_redaction")

    assert redacted["note"] == "[REDACTED: sensitive_medical_content]"
    assert guardrails["redaction_summary"]["category_counts"]["medical"] == 1
    assert guardrails["redaction_summary"]["category_counts"]["contact"] == 0


def test_apply_privacy_guardrails_redacts_digit_leading_email_before_phone_data():
    payload = {"summary": "Reach 12345678@example.test at +49 221 1234567."}

    redacted, guardrails = apply_privacy_guardrails(payload, privacy_mode="contact_redacted")

    assert redacted["summary"] == "Reach [REDACTED: email] at [REDACTED: phone]."
    assert "@example.test" not in redacted["summary"]
    assert guardrails["redaction_summary"]["category_counts"]["contact"] == 2
