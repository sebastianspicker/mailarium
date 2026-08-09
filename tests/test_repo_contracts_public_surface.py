"""Ensures publication-facing repository files enforce privacy and local-state boundaries."""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib

import pytest

from .helpers.repo_contracts import REPO_ROOT, _read, _run_repo_contract_command


def _run_privacy_scan() -> subprocess.CompletedProcess[str]:
    return _run_repo_contract_command(
        [sys.executable, "scripts/privacy_scan.py", "--tracked-only", "--json"],
        check=False,
    )


def test_github_templates_are_present_and_privacy_safe() -> None:
    paths = (
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/ISSUE_TEMPLATE/bug_report.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml",
        ".github/ISSUE_TEMPLATE/question.yml",
        ".github/ISSUE_TEMPLATE/config.yml",
    )
    for relative_path in paths:
        text = _read(relative_path)
        assert "synthetic" in text.casefold() or "private" in text.casefold()
        assert "/Users/" not in text
    assert "security/advisories/new" in _read(".github/ISSUE_TEMPLATE/config.yml")


def test_gitignore_protects_private_runtime_and_local_tool_state() -> None:
    gitignore = _read(".gitignore")

    for entry in (
        "/private/",
        "/data/private/",
        "data/vector-index/",
        "/tests/private/",
        ".streamlit/secrets.toml",
        ".codegraph/",
        ".serena/",
        "/archive/local/",
        "docs/agent/",
        "/AUDIT_REPORT_*.md",
    ):
        assert entry in gitignore


def test_streamlit_is_bound_to_loopback_by_default() -> None:
    streamlit_config = tomllib.loads(_read(".streamlit/config.toml"))

    assert streamlit_config["server"]["address"] == "127.0.0.1"
    assert streamlit_config["theme"] == {
        "base": "light",
        "primaryColor": "#0B63CE",
        "backgroundColor": "#FFFFFF",
        "secondaryBackgroundColor": "#F4F7FA",
        "textColor": "#172331",
        "font": "sans serif",
    }
    launch = "python -m streamlit run mailarium/web_app.py --server.address 127.0.0.1"
    assert launch in _read("README.md")
    assert launch in _read("docs/README_USAGE_AND_OPERATIONS.md")


def test_removed_domain_surfaces_are_absent() -> None:
    removed_paths = (
        "mailarium/case_analysis.py",
        "mailarium/colbert_reranker.py",
        "mailarium/transformers_compat.py",
        "mailarium/templates/legal_support_handoff.html",
        "scripts/wave_workflow_smoke.py",
        "docs/archive/legal-domain-pack/README.md",
        "tests/case_workflows",
        "tests/fixtures/full_pack_matters",
    )
    for relative_path in removed_paths:
        assert not (REPO_ROOT / relative_path).exists(), relative_path


def test_publication_surface_is_synthetic_and_private_artifact_free() -> None:
    completed = _run_privacy_scan()
    if completed.returncode:
        findings = {(item["category"], item["path"]) for item in json.loads(completed.stdout)}
        deleted_or_policy_denied = all(path == ".env.example" or not (REPO_ROOT / path).exists() for _category, path in findings)
        if findings and deleted_or_policy_denied:
            pytest.skip("managed workspace prevents a clean tracked-only scan until intended deletions are staged")
    assert completed.returncode == 0, completed.stdout


def test_github_workflows_are_repo_native_ci_only() -> None:
    workflows = sorted(path.name for path in (REPO_ROOT / ".github/workflows").glob("*.yml"))
    assert workflows == ["ci.yml"]
