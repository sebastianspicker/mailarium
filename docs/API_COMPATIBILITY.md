# API Compatibility Policy

This document defines the automation-facing contract for the `0.5.x` alpha
series.

## Supported Surfaces

The supported public interfaces are:

1. Subcommands and arguments exposed by `python -m mailarium.cli`.
2. MCP tool names and parameter schemas exposed by
   `python -m mailarium.mcp_server`.
3. Environment and constructor settings documented in the public guides.

Streamlit is an exploratory interface. Its layout is not a stable automation
contract.

## Deliberate Breaks In 0.5

The `0.5.0a1` Mailarium rebrand is an intentional hard cutover:

- `src` and `ews_inbox_assistant` are no longer importable packages. The Python
  namespace is `mailarium`, and EWS helpers now live below `mailarium.ews`.
- Installed commands are `mailarium` and `mailarium-ingest`; the former
  `email-rag*` commands are not installed as aliases.
- The four former `EMAIL_RAG_*` product variables were replaced by their
  `MAILARIUM_*` equivalents. Supplying a removed name fails with migration
  guidance instead of being ignored.
- Installed per-user runtime homes use a `mailarium` directory. Runtime data is
  migrated manually; Mailarium never moves, deletes, or falls back to the old
  directory automatically.
- The EWS proposal-correlation extended property is now
  `MailariumProposalId`. Resolve or reject outstanding pre-0.5 proposals before
  upgrading because their former correlation property is not read as an alias.
- MCP tool names and parameter schemas remain unchanged.

The canonical GitHub repository URL intentionally remains
`sebastianspicker/outlook-email-rag`.

## Governing 0.5 Retirement Decision

Status: accepted for the `0.5.0a1` candidate design. This decision does not
make the current dirty tree publishable; the exact frozen candidate must still
pass every gate in `RELEASING.md` and both configured CI jobs.

The supported product is the general local mailbox archive described under
Supported Surfaces. The former case, matter, investigation, behavioral, and
legal-support code was a domain-specific compatibility pack layered over that
archive. Keeping it in 0.5 would advertise specialized schemas, tools, reports,
and workflows that are no longer part of the supported product contract.

The current retirement inventory has these explicit dispositions:

- Move and retain: 169 of the 299 deleted `src/` entries have a live
  same-relative-path implementation under `mailarium/`. Their supported public
  entry points move to the `mailarium` namespace.
- Retire: the other 130 `src/` entries have no `mailarium/` counterpart. They
  comprise 51 case-analysis and orchestration entries; 28 matter,
  investigation, chronology, and report entries; 20 legal and employment
  support entries; 27 behavioral, comparative, and rhetoric-analysis entries;
  and 4 legacy CLI or model-backend compatibility entries.
- Retire verification material with the retired product: 145 deleted test
  paths comprise 96 top-level legacy tests, 9 case-workflow tests, 39
  full-pack fixture files, and 1 case-analysis fixture helper.
- Retire internal working material: all 97 deleted `docs/agent/` paths are
  non-public agent and evaluation material. They are not product documentation
  or a supported runtime input.
- Retire coupled helpers: `scripts/prepare_case_inputs.py` and
  `scripts/wave_workflow_smoke.py` depend on the removed domain pack;
  `sitecustomize.py` only enabled the removed FlagEmbedding compatibility
  shim; and `scripts/topology_inventory.sh` only produced historical audit
  notes that referenced the retired internal documentation tree.

This is a hard retirement, not a hidden compatibility mode. Mailarium does not
load the deleted modules, translate their request or response schemas, retain
their CLI routes or MCP tools, or migrate their derived case-workspace data.
The original mailbox and attachment sources remain the recovery authority for
the supported archive. Operators who need a retired domain workflow must keep
its exports and a backup of its pre-0.5 runtime state before upgrading.

Rollback is version rollback, not an in-place schema downgrade: stop all
Mailarium processes, preserve the original mailbox sources and runtime backup,
and restore the pre-0.5 application and its matching runtime state in a
separate environment. Do not point a pre-0.5 process at a runtime already
advanced by 0.5. Re-entering 0.5 requires a fresh archive or a separately
verified migration.

`tests/test_repo_contracts_docs.py` pins this decision and
`tests/test_repo_contracts_public_surface.py` checks representative removed
paths and the publication boundary. Before the retirement is integrated, the
latter contract must be included in the frozen candidate, the complete deleted
path inventory must be reviewed again, and the source, test, coverage,
security, privacy, artifact, installed-wheel, and offline EWS gates must pass.
Live EWS interoperability remains a separately disclosed release limitation.

## Earlier 0.4 Breaks

The following compatibility surfaces were removed:

- ChromaDB storage and the `CHROMADB_PATH` / `COLLECTION_NAME` settings.
- FlagEmbedding-specific model, fine-tuning, and ColBERT compatibility paths.
- The legal-domain compatibility pack and all case-, matter-, investigation-,
  behavioral-analysis-, and legal-support-specific schemas and tools.
- Flat legacy CLI flags and their dispatch shims.

Old backend environment variables fail explicitly instead of being silently
ignored. Re-index existing archives into a new `VECTOR_INDEX_PATH`; SQLite is
the authoritative vector store and USearch files are derived acceleration
artifacts.

## CLI Contract

The supported CLI is subcommand based:

- `search`
- `browse`
- `export`
- `evidence`
- `analytics`
- `training`
- `admin`
- `topics`
- `mailbox`

Run `python -m mailarium.cli <subcommand> --help` for its current arguments. Removed
flat flags and removed domain commands are parser errors.

MCP local-read paths, runtime storage paths, and output paths are validated
against their configured roots. The ingest CLI accepts an explicit `.olm`
source path, and training commands accept explicit local input paths. Date
filters use ISO `YYYY-MM-DD`; score and count inputs are range checked.

## MCP Contract

The MCP server exposes the general archive, retrieval, evidence, analytics,
thread, topic, reporting, and operational tools documented in
[MCP_TOOLS.md](MCP_TOOLS.md).

Compatibility rules:

- Do not rename a tool or change a parameter's type or requiredness within the
  `0.5.x` series without documenting the break.
- Additive optional fields are allowed.
- Response payloads may add diagnostic fields.
- Removed domain-specific schemas are not accepted through generic models.
- Retrieval scope is explicit user input and is never inferred from query text.

## Storage And Model Contract

- `SQLITE_PATH` identifies the authoritative relational and vector data.
- `VECTOR_INDEX_PATH` contains rebuildable USearch acceleration files.
- Text and image vectors use separate embedding spaces.
- Dense embedding, optional learned-sparse encoding, late interaction, and
  cross-encoder reranking are independent capabilities with explicit fallback
  behavior.
- Offline operation requires local-only embedding settings and
  `SPACY_AUTO_DOWNLOAD_DURING_INGEST=0` when entity extraction is enabled.

## Alpha Change Policy

Breaking changes remain possible between prereleases, but each break must:

1. fail clearly rather than silently changing meaning;
2. update source, tests, public docs, and release notes together;
3. include a migration or re-index instruction when stored data is affected;
4. be verified on Python 3.14.6.
