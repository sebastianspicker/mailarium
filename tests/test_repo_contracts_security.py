"""Ensures the security policy retains its private-reporting guarantees."""

from __future__ import annotations

from .helpers.repo_contracts import _read


def test_security_policy_tracks_private_reporting() -> None:
    security = _read("SECURITY.md")

    assert "current\n`main` branch" in security
    assert "Do not disclose a suspected vulnerability in a public issue" in security
    assert "private vulnerability reporting" in security or "private reporting" in security
    assert "Mailarium is local-first" in security
