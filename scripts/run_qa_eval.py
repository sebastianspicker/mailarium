#!/usr/bin/env python3
"""Run a minimal answer-context evaluation against labeled mailbox questions."""

from __future__ import annotations

import subprocess  # nosec B404
from pathlib import Path

try:
    from scripts._bootstrap import add_repository_root as _add_repository_root
except ModuleNotFoundError:  # Direct execution resolves helpers from the script directory.
    from _bootstrap import add_repository_root as _add_repository_root  # type: ignore[no-redef]

ROOT = _add_repository_root(__file__)


def _project_venv_python() -> Path:
    """Return the repository interpreter path used for embedding-backed re-execution."""
    return ROOT / ".venv" / "bin" / "python"


def _interpreter_has_module(module_name: str) -> bool:
    """Probe an optional module without leaking its import failure to CLI selection logic."""
    try:
        __import__(module_name)
    except ImportError, ModuleNotFoundError:
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    """Delegate QA evaluation while retaining direct-execution and re-exec seams."""
    from scripts.qa_eval_runner import main as run_qa_eval

    return run_qa_eval(
        argv,
        script_path=Path(__file__).resolve(),
        interpreter_has_module=_interpreter_has_module,
        project_venv_python=_project_venv_python,
        run_subprocess=subprocess.run,
        repository_root=ROOT,
    )


if __name__ == "__main__":
    raise SystemExit(main())
