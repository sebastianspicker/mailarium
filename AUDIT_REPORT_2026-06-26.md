# outlook-email-rag — Audit Report (2026-06-26)

Audit-only. No production code was changed. This file is intentionally placed in
the repo root per request; the repo's usual home for such docs is `docs/agent/`.

## Scope & Method

- Checkout: branch `local-state-docs-quality-sync`, **dirty working tree** (see F1).
- Tooling run from `.venv` (Python 3.12.12): `ruff`, `ruff format`, `mypy`,
  pattern greps, an import-reachability scan, and import smoke checks.
- Inspected: entry points (`cli`, `ingest`, `mcp_server`, `web_app`), the
  DB/SQL layer, ingest pipeline, the `tools/` MCP registry, dependency
  manifests, and the working-tree refactor in flight.
- **Not** inspected line-by-line: all 277 modules / ~92.7k LOC. Findings below
  are from full-tree static analysis + targeted reads. Absence of a module from
  this report is not a clean bill of health.

## Snapshot

| Signal | Value |
|---|---|
| `src/` modules (incl. `src/tools/`) | 277 |
| `src/` LOC | ~92,700 |
| Test files | ~374 |
| MCP tools (`@mcp.tool`) | 68 |
| `mypy src` | ✅ clean (277 files) |
| `ruff check src/ tests/` | ✅ clean |
| `ruff check .` | ❌ 50 errors — **all in 6 untracked root scratch files** |
| `ruff format --check .` | ❌ 21 files would reformat (incl. 11 tracked `src/`) |
| Bare `except:` / `== None` / mutable defaults / `eval`/`exec` / `shell=True` | 0 |

**Headline:** the *committed* codebase is unusually disciplined — typed, mypy-clean,
parameterised SQL behind a validation layer, narrow typed exceptions. The real
problems are (1) an **incomplete in-flight refactor that will break the package if
committed as-is**, (2) **repo hygiene debris**, and (3) **scope/structure
over-engineering**.

---

## Findings (severity-ranked)

| ID | Severity | Area | One-line |
|----|----------|------|----------|
| F1 | **High** | Build/hygiene | `src/_utils.py` is untracked but imported by 52 modules — committing the worktree breaks all entry points |
| F2 | Medium | Hygiene | 6 untracked dev scratch scripts in repo root (the only source of 50 ruff errors) |
| F3 | Medium | Refactor debt | `_utils` consolidation is incomplete + exposes dual public/private names |
| F4 | Medium | Style gate | `ruff format --check .` fails on 11 tracked `src/` files — CI format gate is red |
| F5 | Medium | Supply chain | Production pin on a **release candidate**: `transformers>=5.0.0rc3` |
| F6 | Low | Architecture | Severe module fan-out (e.g. one feature = 19 files / 6.8k LOC); 68 MCP tools |
| F7 | Low | Robustness | A handful of best-effort `except … : pass` blocks swallow errors silently |
| F8 | Low | Tracked artifact | `sitecustomize.py` applies a process-wide monkeypatch at interpreter start |

---

### F1 — Untracked `src/_utils.py` imported by 52 modules (High)

#### F1 Evidence

- `git ls-files --error-unmatch src/_utils.py` → **UNTRACKED**.
- `grep -rl "from ._utils import" src` → **52 modules** import it.
- `git cat-file -e HEAD:src/_utils.py` → *missing*; `git grep -l "from ._utils" HEAD` → **0**.
- Working tree imports fine (`import src.cli, src.mcp_server, src.web_app` → OK) only
  because the file exists on disk.
- Same pattern: `src/qa_eval_scoring_utils.py` (untracked) imported by the
  modified `src/qa_eval_scoring_behavior_metrics.py`.

**Impact** — HEAD is self-consistent and *not* broken. But the worktree has 52
modified importers plus this new helper. If someone `git commit -am` without
`git add src/_utils.py` (easy: `-a` ignores untracked files), the pushed tree
raises `ModuleNotFoundError: src._utils` on import → CLI, MCP server, Streamlit,
and ingest all fail to start, and CI import/collection dies immediately.

#### F1 Remediation

- `git add src/_utils.py src/qa_eval_scoring_utils.py` before any commit of the
  importing modules, or revert the refactor entirely if not ready.
- Add a guard test that fails when a tracked module imports an untracked sibling
  (or rely on CI collecting on a clean checkout — see Verification).

#### F1 Verification

```bash
# from a clean clone / fresh worktree of the commit:
python -c "import src.cli, src.mcp_server, src.web_app, src.ingest"
git ls-files --others --exclude-standard -- 'src/*.py'   # must be empty pre-commit
```
**Risk of fix:** trivial.  **Confidence:** High (reproduced via git + import check).

---

### F2 — Dev scratch scripts committed to repo root (Medium)

**Evidence** — untracked at root: `test_imports.py`, `test_imports_direct.py`,
`verify_utils.py`, `fix_duplicates.py`, `check_top_level.py`,
`check_docstrings.py`. These 6 files are the **entire** source of `ruff check .`'s
50 errors (`F401`, `E402`, `E501`, `W293`, `I001`, …). `fix_duplicates.py` is the
one-off codemod behind the F1/F3 refactor; `check_*`/`test_imports*` are ad-hoc
probes with hardcoded absolute paths (e.g.
`/Users/sebastian/git/outlook-email-rag/src/tools/legal_support.py`).

**Impact** — Repo-root noise; if accidentally committed they ship dead/broken code,
leak a local path, and turn `ruff check .` red. They duplicate real tooling
(`pytest`, `check_docstrings.py` overlaps with linting).

**Remediation** — Delete them, or move reusable bits under `scripts/` and lint
them. Add their names to `.gitignore` if they recur. Do **not** `git add` them.

**Verification** — `ruff check .` drops to 0 errors once removed.
**Risk:** none (they are not imported by `src/`/`tests/`).  **Confidence:** High.

---

### F3 — `_utils` consolidation incomplete + dual naming (Medium)

#### F3 Evidence

- `src/_utils.py` docstring: *"Consolidated from 52 files with duplicate
  implementations"*, yet 5 modules still define their own `_compact`
  (`src/tools/browse.py`, `evidence.py`, `search_answer_context_budget.py`,
  `search_answer_context_case_payloads.py`,
  `search_answer_context_evidence_payloads.py`), and 24 `_as_dict/_as_list/_compact`
  defs remain across `src`.
- `_utils.py` exports both public (`as_dict`) and private aliases (`_as_dict`),
  and callers import *both* styles (e.g. `from src._utils import as_dict` vs
  `from src._utils import _as_dict`). One concept, two public names.

**Impact** — DRY goal only half-met; future readers can't tell which name is
canonical; the duplicate `_compact` copies can drift from the shared one.

**Remediation** — Finish the codemod for the remaining `_compact`/`_as_*`
definitions, pick one public name set (drop the `_`-prefixed aliases or keep only
them), and delete `fix_duplicates.py` afterward. Keep this as one reviewable slice.

**Verification** — `grep -rn "def _compact\|def _as_dict\|def _as_list" src` → only
`src/_utils.py`.  **Risk:** low (pure rename/move).  **Confidence:** High.

---

### F4 — `ruff format --check .` is red on tracked source (Medium)

**Evidence** — 21 files would reformat; 11 are tracked `src/` modules
(`case_analysis_transform.py`, `case_full_pack.py`, `case_material_intake.py`,
`case_operator_intake.py`, `case_prompt_context_actors.py`,
`case_prompt_intake_helpers.py`, `case_prompt_preflight_normalization.py`,
`evidence_harvest.py`, `lawyer_briefing_memo.py`, `matter_file_ingestion.py`,
`matter_workspace.py`). `AGENTS.md` lists `ruff format --check .` as a core check
and CI runs it (`.github/workflows/ci.yml`).

**Impact** — These are the files touched by the in-flight refactor; the format
gate currently fails locally. (CI passes today because the changes are
uncommitted.) Committing as-is turns CI red.

**Remediation** — `ruff format src/` (or the listed files) as part of the refactor
commit.  **Verification** — `ruff format --check .` exits 0.
**Risk:** none (formatting only).  **Confidence:** High.

---

### F5 — Production dependency pinned to a release candidate (Medium)

**Evidence** — `pyproject.toml` / `requirements.txt`:
`transformers>=5.0.0rc3,<6` with comment *"patched for CVE-2026-1839; repo shims
FlagEmbedding's removed FX helper"*.

**Impact** — `>=…rc3` allows pre-release resolution as a runtime floor. RCs can be
yanked or change behavior before GA; `sitecustomize.py` already monkeypatches
`transformers.utils.import_utils` to survive a removed helper (F8). This couples
install stability to an unreleased line. The CVE rationale is legitimate, so this
is a *risk to track*, not necessarily to revert.

**Remediation** — Move to the GA `transformers==5.x` as soon as it ships and drop
the shim; meanwhile pin a tested exact RC (`==5.0.0rcN`) rather than `>=rc3` to
avoid surprise upgrades, and add a `pip-audit`/resolution test in the release
matrix (already partly present via `scripts/dependency_audit.py`).
**Risk:** medium (model-loading regressions possible on bump).  **Confidence:** High (manifest).

---

### F6 — Module fan-out / surface area over-engineering (Low, structural)

#### F6 Evidence

- One feature, `search_answer_context`, spans **19 files / ~6,813 LOC** in
  `src/tools/` (`…_runtime_single_lane`, `_multi_lane`, `_lanes`, `_ranking`,
  `_builder`, `_payload`, `_budgeting`, `_candidate_rows`, `_search`, plus
  `evidence_*`, `case_payloads`, `budget`, `rendering`, `impl`).
- Other clusters: `case_analysis*` 15 files, `qa_eval*` ~20, `investigation_report*`
  9, `mcp_models*` ~13, `multi_source_case_bundle*` 8, `master_chronology*` 5.
- 68 MCP tools for a "search my email archive" product.

These are *not* 1-line facade modules (most are 250–700 LOC), so this is
breadth/depth sprawl, not micro-splitting. Much of it is the legal-support product
pillar, which is intentional per README — but the ratio of legal-support apparatus
to the email-RAG core is high, and the per-feature file explosion raises the cost
of every change (imports, navigation, test fan-out).

**Impact** — High cognitive load, slow onboarding, large blast radius for edits,
heavy test maintenance. Not a bug; a maintainability tax.

#### F6 Remediation (only where it pays off; no big-bang rewrite)

- Treat `search_answer_context_runtime_*` as one cohesive package and ask, per
  split, whether it earns its file boundary; collapse the thinnest siblings.
- Before adding the 69th MCP tool, confirm an existing tool + params can't cover it.
- Track this as deliberate debt rather than churning it now.

**Verification** — n/a (judgment).  **Confidence:** Medium (structure is measured;
"too much" is a judgment call given the stated product scope).

---

### F7 — Silent best-effort `except … : pass` (Low)

**Evidence** — 7 blocks swallow exceptions without logging, e.g.
`src/config.py` (`ImportError`), `src/attachment_extractor.py:267,313`
(`OSError` on temp cleanup), `src/ingest_pipeline.py` (`ImportError`/`OSError`),
`src/email_db.py:174` (`OSError, sqlite3.Error`), `src/mcp_server.py:157`
(`OSError` on lock release). All are narrow and typed (no bare `except`).

**Impact** — Mostly defensible (optional deps, best-effort fd/temp cleanup, lock
release on shutdown). Risk is low but `AGENTS.md` says "do not swallow errors" —
silent cleanup failures (temp files, lock fds) can mask leaks.

**Remediation** — Add `logger.debug(..., exc_info=True)` to the cleanup/lock
blocks so failures are observable; leave the optional-dependency `ImportError`
passes as-is (idiomatic).  **Risk:** none.  **Confidence:** High.

---

### F8 — `sitecustomize.py` global import-time monkeypatch (Low)

**Evidence** — tracked `sitecustomize.py` calls
`ensure_flagembedding_transformers_compat()` at interpreter startup, which patches
`transformers.utils.import_utils` to restore a helper FlagEmbedding expects.

**Impact** — `sitecustomize` runs for *every* Python process using this repo's
site (incl. tooling/tests), not just the app. It is a process-wide side effect to
work around F5. Correct today, but invisible coupling that will surprise future
maintainers and may interfere with unrelated processes sharing the venv.

**Remediation** — When `transformers` GA lands (F5), delete the shim. Until then,
keep it but document the trigger condition in the module docstring (it partly
does) and ensure it is a no-op when the helper already exists (it guards on
`hasattr` — good).  **Risk:** low.  **Confidence:** Medium.

---

## Quick wins (do first)

1. `git add src/_utils.py src/qa_eval_scoring_utils.py` (or revert refactor) — **F1**.
2. Delete the 6 root scratch scripts — **F2** (zeroes out `ruff check .`).
3. `ruff format src/` on the 11 touched files — **F4**.
4. Finish the `_compact`/`_as_*` codemod, then delete `fix_duplicates.py` — **F3**.

## Suggested verification gate before any commit of this worktree

```bash
# in .venv
ruff check .                 # expect 0 after F2
ruff format --check .        # expect 0 after F4
mypy src                     # currently clean
python -c "import src.cli, src.mcp_server, src.web_app, src.ingest"   # F1
git status --porcelain | grep '^??' || true   # no untracked src/* before commit
pytest -q --tb=short         # full suite (not run in this audit — see below)
```

## Checks NOT run in this audit (be explicit)

- **Full `pytest` suite / coverage** — not executed (large suite; out of scope for
  a read-only audit and time-bound). `mypy`, `ruff`, and import smoke were run.
- **`bandit` / `pip-audit`** — not run here; prior memory notes a separate Codacy
  lane exists for this repo. Re-run `bandit -r src -q -ll -ii` and
  `python scripts/dependency_audit.py` for the security/dep gate.
- **Per-module correctness review** of the ~270 modules not opened. No claim is
  made about their internal logic.

## Remaining uncertainty

- Findings reflect the **current dirty working tree**, not a committed state. HEAD
  itself was verified self-consistent for the `_utils` refactor (0 importers, no
  file) — i.e. the F1/F3/F4 risks are introduced by the *uncommitted* changes.
- "Over-engineering" (F6) is a judgment given the declared legal-support scope; the
  structural measurements are objective, the "too much" verdict is not.
