# Release Status

Evidence date: 2026-08-14

Candidate version: `0.5.0a1`

Publication status: not ready

## Candidate scope

The candidate provides local Outlook `.olm` ingestion, SQLite-authoritative
storage, rebuildable USearch acceleration, CLI and MCP interfaces, a
trusted-local Streamlit interface, and optional on-premises EWS workflows.

The supported operator runtime is macOS 14 or later on Apple Silicon with
Python 3.14.6. The Ubuntu CI job validates source compatibility but is not an
operator-runtime claim.

EWS remains experimental. Offline fixtures cover the implemented protocol and
action contracts, but live server interoperability and write behavior have not
been verified for this candidate. Offline verified; live EWS writes unverified.

## Current local verification

| Gate | Result |
| --- | --- |
| Lockfile | `uv lock --check` passed with 177 packages |
| Dependency-enabled checks | Blocked in this checkout because its `.venv` does not contain Ruff, mypy, pytest, Bandit, pip-audit, or Streamlit; no dependency installation was performed |
| Python syntax | AST parsing passed for 202 live package and script files |
| Static demo | JavaScript syntax, four local references, three 1440 by 900 screenshots, and loopback HTML/CSS/JavaScript routes passed |
| Public-tree privacy scan | The tracked-only scan fails against the real Git index while the intentional retirement deletions remain unstaged; exact-candidate proof requires a frozen reviewed tree |
| Dependency audit | Not runnable in the current environment. The most recent recorded scan in `AUDIT_LEDGER.md` found 14 advisories across four locked packages after one existing exception |
| Build and installed wheel | Unrun; the current environment lacks the declared setuptools build backend |
| Diff whitespace | `git diff --check` passed |

The audit ledger records the broader 2026-08-09 external-candidate suite. Those
results are useful historical evidence, but they do not replace rerunning the
gates on an exact candidate or resolving its dependency findings.

## Publication requirements

Before publishing `0.5.0a1`:

1. Review and commit the complete package-namespace migration and file
   deletions as one intentional candidate.
2. Update or explicitly disposition all current dependency advisories under an
   authorized lockfile change, then rerun the complete suite.
3. Define the intended Codacy analyzer configuration and obtain a configured
   result instead of the current `MissingConfig` state.
4. Run both configured GitHub Actions jobs against that exact commit.
5. Repeat the tracked-only privacy scan and artifact checks against the exact
   committed tree.
6. Confirm package-name and project-name availability for each publication
   channel.
7. If EWS support is included in release notes, validate a disposable
   authorized server profile or state clearly that only offline protocol
   fixtures were verified.

Do not publish from the current unstaged worktree.
