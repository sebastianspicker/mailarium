"""Parser and trusted-terminal tests for the unified mailbox CLI."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from mailarium.cli import parse_args
from mailarium.cli_commands_mailbox import _confirm_approval, _run


def test_mailbox_configure_parser_accepts_only_external_credential_reference() -> None:
    args = parse_args(
        [
            "mailbox",
            "accounts",
            "configure",
            "--account",
            "local",
            "--mailbox",
            "mailbox@example.test",
            "--endpoint",
            "https://exchange.example.test/EWS/Exchange.asmx",
            "--auth",
            "ntlm",
            "--credential-ref",
            "basic-env:EWS_USER:EWS_PASSWORD",
            "--folder",
            "inbox",
        ]
    )

    assert args.subcommand == "mailbox"
    assert args.mailbox_accounts_action == "configure"
    assert args.credential_ref == "basic-env:EWS_USER:EWS_PASSWORD"
    assert not hasattr(args, "password")


def test_mailbox_folder_discovery_and_full_sync_parser_contracts_are_explicit() -> None:
    discover = parse_args(["mailbox", "folders", "discover", "--account", "local", "--select"])
    sync = parse_args(["mailbox", "sync", "--account", "local", "--until-complete", "--defer-indexing"])

    assert discover.mailbox_action == "folders"
    assert discover.mailbox_folders_action == "discover"
    assert discover.account_id == "local"
    assert discover.select is True
    assert sync.until_complete is True
    assert sync.defer_indexing is True


def test_mailbox_cli_routes_discovery_and_opt_in_completion_to_the_service() -> None:
    class Service:
        @staticmethod
        def discover_folders(account_id, *, select):
            return {"account_id": account_id, "selected": select}

        @staticmethod
        def sync(account_id, *, folders, include_attachment_content, until_complete, defer_indexing):
            return {
                "account_id": account_id,
                "folders": tuple(folders),
                "include_attachment_content": include_attachment_content,
                "until_complete": until_complete,
                "defer_indexing": defer_indexing,
            }

    discovered = _run(
        SimpleNamespace(mailbox_action="folders", mailbox_folders_action="discover", account_id="account", select=True),
        Service(),
    )
    synced = _run(
        SimpleNamespace(
            mailbox_action="sync",
            account_id="account",
            folders=("inbox",),
            include_attachment_content=False,
            until_complete=True,
            defer_indexing=True,
        ),
        Service(),
    )

    assert discovered == {"account_id": "account", "selected": True}
    assert synced["until_complete"] is True
    assert synced["defer_indexing"] is True


def test_approval_requires_tty_and_proposal_suffix() -> None:
    proposal = {"proposal_id": "00000000-0000-0000-0000-12345678", "operation": "send_item"}
    with patch("sys.stdin.isatty", return_value=False), pytest.raises(PermissionError, match="interactive"):
        _confirm_approval(proposal)
    with (
        patch("sys.stdin.isatty", return_value=True),
        patch("builtins.input", return_value="wrong"),
        pytest.raises(PermissionError, match="did not match"),
    ):
        _confirm_approval(proposal)


def test_readiness_preserves_the_exact_ews_verification_boundary() -> None:
    class Service:
        @staticmethod
        def readiness(account_id):
            return {
                "account_id": account_id,
                "status": "Offline verified; live EWS writes unverified.",
            }

    result = _run(
        SimpleNamespace(mailbox_action="readiness", account_id="account"),
        Service(),
    )

    assert result["status"] == "Offline verified; live EWS writes unverified."
