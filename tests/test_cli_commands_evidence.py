"""Exercises evidence-oriented CLI routes for provenance, custody checks, and exportable audit material."""

import builtins
from unittest.mock import MagicMock

from mailarium.cli_commands_evidence import (
    run_evidence_stats_impl,
    run_evidence_verify_impl,
    run_provenance_impl,
)

from ._cli_commands_cases import (
    TestCmdEvidence,
    TestRunCustodyChain,
    TestRunDossier,
    TestRunEvidenceExport,
    TestRunEvidenceList,
    TestRunEvidenceStats,
    TestRunEvidenceVerify,
    TestRunProvenance,
)

_COLLECTED_TESTS = (
    TestCmdEvidence,
    TestRunCustodyChain,
    TestRunDossier,
    TestRunEvidenceExport,
    TestRunEvidenceList,
    TestRunEvidenceStats,
    TestRunEvidenceVerify,
    TestRunProvenance,
)


def _block_rich_imports(monkeypatch) -> None:
    """Force the public commands through their supported plain-output fallback."""
    original_import = builtins.__import__

    def blocked_import(name, *args, **kwargs):
        if name.startswith("rich"):
            raise ImportError("Rich unavailable for characterization")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked_import)


def test_evidence_stats_plain_fallback_preserves_callback_output(monkeypatch, capsys) -> None:
    stats = {"total": 2, "verified": 1, "unverified": 1}
    mock_db = MagicMock()
    mock_db.evidence_stats.return_value = stats
    _block_rich_imports(monkeypatch)

    def print_rich_or_plain(*, rich_fn, plain_fn) -> None:
        plain_fn()

    run_evidence_stats_impl(lambda: mock_db, print_rich_or_plain)

    assert capsys.readouterr().out == '{\n  "total": 2,\n  "verified": 1,\n  "unverified": 1\n}\n'
    mock_db.evidence_stats.assert_called_once_with()


def test_evidence_verify_plain_fallback_preserves_failure_order(monkeypatch, capsys) -> None:
    mock_db = MagicMock()
    mock_db.verify_evidence_quotes.return_value = {
        "verified": 1,
        "failed": 1,
        "failures": [{"evidence_id": 7, "key_quote_preview": "misquoted", "email_uid": "mail-abcdef012345"}],
    }
    _block_rich_imports(monkeypatch)

    run_evidence_verify_impl(lambda: mock_db)

    assert capsys.readouterr().out == (
        '\nVerification complete: 1 verified, 1 failed\n\nFailed quotes:\n  ID 7: "misquoted" (email: mail-abcdef0)\n'
    )
    mock_db.verify_evidence_quotes.assert_called_once_with()


def test_provenance_plain_fallback_preserves_database_result(monkeypatch, capsys) -> None:
    result = {
        "email": {"subject": "Test"},
        "source": {"olm_source_hash": "sha256:abc"},
        "custody_events": [{"action": "evidence_added"}],
    }
    mock_db = MagicMock()
    mock_db.email_provenance.return_value = result
    _block_rich_imports(monkeypatch)

    run_provenance_impl(lambda: mock_db, "uid-xyz")

    assert capsys.readouterr().out == (
        '{\n  "email": {\n    "subject": "Test"\n  },\n'
        '  "source": {\n    "olm_source_hash": "sha256:abc"\n  },\n'
        '  "custody_events": [\n    {\n      "action": "evidence_added"\n    }\n  ]\n}\n'
    )
    mock_db.email_provenance.assert_called_once_with("uid-xyz")
