#!/usr/bin/env python3
"""Run PR-scoped checks that mirror the Codacy Cloud analyzer surface."""

from __future__ import annotations

import argparse
import json
import os
import subprocess  # nosec B404
import sys
from pathlib import Path

DEFAULT_BASE_REF = "origin/main"
DEFAULT_OUTPUT_DIR = Path("/private/tmp/outlook-email-rag-codacy-preflight")
CODACY_CLI = Path(".codacy/cli.sh")
CODACY_TOOLS = ("pylint", "lizard", "opengrep", "trivy")
EXCLUDED_PARTS = (".codacy", "private")
EXCLUDED_PREFIXES = ("docs/archive/", "docs/agent/")
EXCLUDED_NAME_MARKERS = ("ledger", "status")
TOOL_EXTENSIONS = {
    "lizard": {".py"},
    "opengrep": {".bash", ".env", ".py", ".sh", ".yaml", ".yml"},
    "pylint": {".py"},
    "trivy": {".env", ".json", ".lock", ".txt", ".yaml", ".yml"},
}
TRIVY_FILENAMES = {"Pipfile.lock", "poetry.lock", "requirements.txt", "uv.lock"}


def _run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # nosemgrep
        command,
        check=False,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def _git_lines(args: list[str]) -> list[str]:
    completed = _run(["git", *args], capture=True)
    if completed.returncode != 0:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _changed_paths(base_ref: str) -> list[Path]:
    paths = set(_git_lines(["diff", "--name-only", "--diff-filter=ACMRTUXB", f"{base_ref}...HEAD"]))
    paths.update(_git_lines(["diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB"]))
    paths.update(_git_lines(["diff", "--name-only", "--diff-filter=ACMRTUXB"]))
    return sorted(Path(path) for path in paths if Path(path).is_file())


def _is_excluded(path: Path) -> bool:
    normalized = path.as_posix()
    name = path.name.lower()
    return (
        any(part in EXCLUDED_PARTS for part in path.parts)
        or normalized.startswith(EXCLUDED_PREFIXES)
        or any(marker in name for marker in EXCLUDED_NAME_MARKERS)
    )


def _tool_files(tool: str, paths: list[Path]) -> list[Path]:
    extensions = TOOL_EXTENSIONS[tool]
    if tool == "trivy":
        return [path for path in paths if (path.suffix in extensions or path.name in TRIVY_FILENAMES) and not _is_excluded(path)]
    return [path for path in paths if path.suffix in extensions and not _is_excluded(path)]


def _sarif_results(path: Path) -> list[dict[str, object]]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    results: list[dict[str, object]] = []
    for run in payload.get("runs", []):
        results.extend(run.get("results", []))
    return results


def _safe_output_name(tool: str, path: Path) -> str:
    return f"{tool}-{path.as_posix().replace('/', '__')}.sarif"


def _run_codacy_command(tool: str, files: list[Path], output: Path) -> tuple[int, int]:
    command = [
        str(CODACY_CLI),
        "analyze",
        "--tool",
        tool,
        "--format",
        "sarif",
        "--output",
        str(output),
        *(path.as_posix() for path in files),
    ]
    completed = _run(command)
    if completed.returncode != 0:
        return completed.returncode, 0
    return 0, len(_sarif_results(output))


def _run_codacy_tool(tool: str, files: list[Path], output_dir: Path, *, fail_on_findings: bool) -> int:
    if not files:
        print(f"codacy {tool}: skipped, no changed matching files")
        return 0

    if tool == "trivy":
        total_results = 0
        for path in files:
            output = output_dir / _safe_output_name(tool, path)
            returncode, result_count = _run_codacy_command(tool, [path], output)
            if returncode:
                return returncode
            total_results += result_count
    else:
        output = output_dir / f"{tool}.sarif"
        returncode, total_results = _run_codacy_command(tool, files, output)
        if returncode:
            return returncode

    print(f"codacy {tool}: {total_results} SARIF result(s), {len(files)} file(s)")
    if total_results and fail_on_findings:
        print(f"codacy {tool}: findings present; inspect SARIF under {output_dir}", file=sys.stderr)
        return 1
    return 0


def _run_ruff(paths: list[Path]) -> int:
    files = [path for path in paths if path.suffix == ".py" and not _is_excluded(path)]
    if not files:
        print("ruff: skipped, no changed Python files")
        return 0
    completed = _run(["ruff", "check", *(path.as_posix() for path in files)])
    if completed.returncode != 0:
        return completed.returncode
    completed = _run(["ruff", "format", "--check", *(path.as_posix() for path in files)])
    return completed.returncode


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", default=os.getenv("BASE_REF", DEFAULT_BASE_REF))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Exit nonzero when any local Codacy SARIF result is present.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if not CODACY_CLI.exists():
        print("Missing .codacy/cli.sh; install Codacy Guardrails/CLI v2 before running.", file=sys.stderr)
        return 2

    paths = _changed_paths(args.base_ref)
    if not paths:
        print("No changed files found for Codacy PR preflight.")
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Changed files considered: {len(paths)}")
    failures = 1 if _run_ruff(paths) else 0
    for tool in CODACY_TOOLS:
        failures += (
            1
            if _run_codacy_tool(
                tool,
                _tool_files(tool, paths),
                args.output_dir,
                fail_on_findings=args.fail_on_findings,
            )
            else 0
        )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
