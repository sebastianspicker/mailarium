from __future__ import annotations

import subprocess  # nosec B404 — test helper, runs git/built-in tools with repo-relative paths; no user input
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _git_ls(relative_path: str) -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files", "--", relative_path],
        check=True,
        capture_output=True,
        cwd=REPO_ROOT,
        text=True,
    )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _is_tracked(relative_path: str) -> bool:
    return bool(_git_ls(relative_path))


def _mcp_tool_count() -> int:
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from src.mcp_server import ToolDeps, mcp; "
                "from src.tools import register_all; "
                "manager = getattr(mcp, '_tool_manager', None); "
                "tools = getattr(manager, '_tools', None); "
                "register_all(mcp, ToolDeps()) if not isinstance(tools, dict) else None; "
                "manager = getattr(mcp, '_tool_manager', None); "
                "tools = getattr(manager, '_tools', None); "
                "print(len(tools))"
            ),
        ],
        check=True,
        capture_output=True,
        cwd=REPO_ROOT,
        text=True,
    )
    return int(completed.stdout.strip())
