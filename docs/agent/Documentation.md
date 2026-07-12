# Documentation Log

Status: `public-synthetic`

Purpose:

- record verification and cleanup checkpoints that are safe for a public repository
- avoid storing local-only case facts, local absolute paths, personal names, or generated counsel artifacts
- keep detailed private run logs in the local private workspace, not in tracked docs

## 2026-06-28 Codacy whole-corpus remediation progress

### Scope

- Started whole-corpus Codacy remediation from
  `docs/agent/codacy_whole_corpus_remediation_prep_2026-06-27.md`
- Fixed local Codacy Ruff slice `CODACY-WC-001`
  (`Ruff_UP038_non-pep604-isinstance`)
- Wrote local ignored ledger `docs/agent/codacy_remediation_ledger.md`
- Fixed local Codacy Prospector slice `CODACY-WC-020` in
  `src/tools/search_answer_context_runtime_builder.py`; focused Prospector
  improved 7 -> 0 and latest full Prospector improved 559 -> 552 findings.
- Fixed local Codacy Prospector slice `CODACY-WC-021` across multi-source
  split modules and `tests/test_investigation_report.py`; focused Prospector
  improved 12 -> 0 and latest full Prospector improved 552 -> 535 findings.
- Fixed local Codacy Prospector slice `CODACY-WC-022` in
  `src/tools/search_answer_context_runtime_budgeting.py`; focused Prospector
  improved 20 -> 0 and latest full Prospector improved 535 -> 515 findings.
- Fixed local Codacy Prospector slice `CODACY-WC-023` in
  `src/tools/search_answer_context_runtime_lanes.py` and
  `src/tools/search_answer_context_runtime_ranking.py`; focused Prospector
  improved 37 -> 0 and latest full Prospector improved 515 -> 478 findings.
- Fixed local Codacy Prospector slice `CODACY-WC-024` in
  `src/case_analysis_harvest_quality.py` and
  `src/case_analysis_harvest_coverage.py`; focused Prospector improved
  17 -> 0 and latest full Prospector improved 478 -> 461 findings.
- Fixed local Codacy Prospector slice `CODACY-WC-025` in
  `src/case_analysis_harvest_bundle.py`; focused Prospector improved
  6 -> 0 and latest full Prospector improved 461 -> 455 findings.
- Fixed local Codacy Prospector slice `CODACY-WC-026` across
  `tests/_cli_commands_cases.py` and parse-OLM helper files; focused
  Prospector improved 33 -> 0 and latest full Prospector improved 455 -> 422 findings.
- Fixed local Codacy Prospector slice `CODACY-WC-027` across
  `tests/_mcp_tools_cases.py`, MCP thread helpers, and parse-OLM
  normalization helpers; focused Prospector improved 21 -> 0 and latest full
  Prospector improved 422 -> 401 findings.
- Fixed local Codacy Prospector slice `CODACY-WC-028` across ingest/email-db
  aggregate and helper files; focused Prospector improved 24 -> 0 and latest
  full Prospector improved 401 -> 377 findings.
- Fixed local Codacy Prospector slice `CODACY-WC-029` across MCP
  answer-context helpers, diagnostics helpers, and harvest common; focused
  Prospector improved 29 -> 0 and latest full Prospector improved 377 -> 348 findings.
- Fixed local Codacy Prospector slice `CODACY-WC-030` across case-analysis
  transform payload tests, MCP reporting/browse helpers, and parse attachment
  metadata helpers; focused Prospector improved 33 -> 0 and latest full
  Prospector improved 348 -> 315 findings.

- Fixed local Codacy Prospector slice `CODACY-WC-031` across ingest,
  diagnostics, CLI case parse, MCP search aggregate, and shared test-helper
  stale imports; focused Prospector improved 50 -> 0 and latest full Prospector
  improved 315 -> 265 findings.

### Verification

- `rtk codacy-analysis analyze --tool Prospector --files src/tools/search_answer_context_runtime_builder.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-runtime-builder-after-ruff-2026-06-28.json --tool-timeout 600000`
- Why: verify `CODACY-WC-020` runtime-builder helper import restoration.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile src/tools/search_answer_context_runtime_builder.py`
- Why: syntax-check edited runtime-builder module.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/tools/search_answer_context_runtime_builder.py`
- Why: lint edited runtime-builder module after Ruff import cleanup.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-runtime-builder-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after `CODACY-WC-020`.
- Gate type: full local Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 559 -> 552 findings; 0 analyzer errors.
- `rtk codacy-analysis analyze --tool Prospector --files src/multi_source_case_bundle_reliability.py src/multi_source_case_bundle_common.py src/multi_source_case_bundle_chronology.py tests/test_investigation_report.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-mscb-undefined-final-clean-2026-06-28.json --tool-timeout 600000`
- Why: verify `CODACY-WC-021` remaining undefined-name remediation.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile src/multi_source_case_bundle_reliability.py src/multi_source_case_bundle_common.py src/multi_source_case_bundle_chronology.py tests/test_investigation_report.py`
- Why: syntax-check edited multi-source/test modules.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/multi_source_case_bundle_reliability.py src/multi_source_case_bundle_common.py src/multi_source_case_bundle_chronology.py tests/test_investigation_report.py`
- Why: lint edited multi-source/test modules.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-mscb-undefined-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after `CODACY-WC-021`.
- Gate type: full local Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 552 -> 535 findings; 0 analyzer errors.
- `rtk codacy-analysis analyze --tool Prospector --files src/tools/search_answer_context_runtime_budgeting.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-runtime-budgeting-final-clean-2026-06-28.json --tool-timeout 600000`
- Why: verify `CODACY-WC-022` runtime-budgeting stale import cleanup.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile src/tools/search_answer_context_runtime_budgeting.py`
- Why: syntax-check edited runtime-budgeting module.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/tools/search_answer_context_runtime_budgeting.py`
- Why: lint edited runtime-budgeting module after import cleanup.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-runtime-budgeting-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after `CODACY-WC-022`.
- Gate type: full local Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 535 -> 515 findings; 0 analyzer errors.
- `rtk codacy-analysis analyze --tool Prospector --files src/tools/search_answer_context_runtime_lanes.py src/tools/search_answer_context_runtime_ranking.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-runtime-lanes-ranking-clean-2026-06-28.json --tool-timeout 600000`
- Why: verify `CODACY-WC-023` runtime lanes/ranking stale import cleanup.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile src/tools/search_answer_context_runtime_lanes.py src/tools/search_answer_context_runtime_ranking.py`
- Why: syntax-check edited runtime lanes/ranking modules.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/tools/search_answer_context_runtime_lanes.py src/tools/search_answer_context_runtime_ranking.py`
- Why: lint edited runtime lanes/ranking modules after import cleanup.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-runtime-lanes-ranking-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after `CODACY-WC-023`.
- Gate type: full local Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 515 -> 478 findings; 0 analyzer errors.
- `rtk codacy-analysis analyze --tool Prospector --files src/case_analysis_harvest_quality.py src/case_analysis_harvest_coverage.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-harvest-quality-coverage-final-2026-06-28.json --tool-timeout 600000`
- Why: verify `CODACY-WC-024` harvest quality/coverage stale import cleanup.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile src/case_analysis_harvest_quality.py src/case_analysis_harvest_coverage.py`
- Why: syntax-check edited harvest quality/coverage modules.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/case_analysis_harvest_quality.py src/case_analysis_harvest_coverage.py`
- Why: lint edited harvest quality/coverage modules after import cleanup.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-harvest-quality-coverage-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after `CODACY-WC-024`.
- Gate type: full local Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 478 -> 461 findings; 0 analyzer errors.
- `rtk codacy-analysis analyze --tool Prospector --files src/case_analysis_harvest_bundle.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-harvest-bundle-clean-2026-06-28.json --tool-timeout 600000`
- Why: verify `CODACY-WC-025` harvest bundle stale import cleanup.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile src/case_analysis_harvest_bundle.py`
- Why: syntax-check edited harvest bundle module.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/case_analysis_harvest_bundle.py`
- Why: lint edited harvest bundle module after import cleanup.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-harvest-bundle-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after `CODACY-WC-025`.
- Gate type: full local Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 461 -> 455 findings; 0 analyzer errors.
- `rtk codacy-analysis analyze --tool Prospector --files tests/_cli_commands_cases.py tests/_parse_olm_email_type_cases.py tests/_parse_olm_uid_fallback_cases.py tests/_parse_olm_clean_body_recovery_cases.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-tests-cli-parse-final-2026-06-28.json --tool-timeout 600000`
- Why: verify `CODACY-WC-026` CLI aggregate and parse-OLM helper cleanup.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile tests/_cli_commands_cases.py tests/_parse_olm_email_type_cases.py tests/_parse_olm_uid_fallback_cases.py tests/_parse_olm_clean_body_recovery_cases.py`
- Why: syntax-check edited test helper modules.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check tests/_cli_commands_cases.py tests/_parse_olm_email_type_cases.py tests/_parse_olm_uid_fallback_cases.py tests/_parse_olm_clean_body_recovery_cases.py`
- Why: lint edited test helper modules.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk .venv/bin/pytest -q --tb=short tests/test_parse_olm_extended.py tests/test_cli_command_families.py`
- Why: verify parent parse-OLM and CLI command test behavior.
- Gate type: targeted pytest.
- Result: PASS; 43 passed.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-tests-cli-parse-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after `CODACY-WC-026`.
- Gate type: full local Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 455 -> 422 findings; 0 analyzer errors.
- `rtk codacy-analysis analyze --tool Prospector --files tests/_mcp_tools_extended_thread_cases.py tests/_mcp_tools_cases.py tests/_parse_olm_clean_body_normalization_cases.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-tests-mcp-parse-normalization-final-check-2026-06-28.json --tool-timeout 600000`
- Why: verify `CODACY-WC-027` MCP aggregate/thread and parse normalization helper cleanup.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile tests/_mcp_tools_extended_thread_cases.py tests/_mcp_tools_cases.py tests/_parse_olm_clean_body_normalization_cases.py`
- Why: syntax-check edited MCP/parse helper modules.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check tests/_mcp_tools_extended_thread_cases.py tests/_mcp_tools_cases.py tests/_parse_olm_clean_body_normalization_cases.py`
- Why: lint edited MCP/parse helper modules.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk .venv/bin/pytest -q --tb=short tests/test_mcp_tools_extended_search.py tests/test_parse_olm_extended.py`
- Why: verify parent MCP extended and parse-OLM behavior.
- Gate type: targeted pytest.
- Result: PASS; 46 passed.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-tests-mcp-parse-normalization-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after `CODACY-WC-027`.
- Gate type: full local Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 422 -> 401 findings; 0 analyzer errors.
- `rtk codacy-analysis analyze --tool Prospector --files tests/_ingest_cases.py tests/_ingest_image_cases.py tests/_email_db_cases.py tests/_ingest_summary_cases.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-tests-ingest-emaildb-final-check-2026-06-29.json --tool-timeout 600000`
- Why: verify `CODACY-WC-028` ingest/email-db aggregate and helper cleanup.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile tests/_ingest_cases.py tests/_ingest_image_cases.py tests/_email_db_cases.py tests/_ingest_summary_cases.py`
- Why: syntax-check edited ingest/email-db helper modules.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check tests/_ingest_cases.py tests/_ingest_image_cases.py tests/_email_db_cases.py tests/_ingest_summary_cases.py`
- Why: lint edited ingest/email-db helper modules.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk .venv/bin/pytest -q --tb=short tests/test_ingest_cli.py tests/test_ingest_pipeline.py tests/test_ingest_reembed.py tests/test_email_db_refactor_seams.py`
- Why: verify parent ingest and email DB behavior after helper cleanup.
- Gate type: targeted pytest.
- Result: PASS; 38 passed.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-tests-ingest-emaildb-2026-06-29.json --tool-timeout 600000`
- Why: refresh full Prospector count after `CODACY-WC-028`.
- Gate type: full local Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 401 -> 377 findings; 0 analyzer errors.
- `rtk codacy-analysis analyze --tool Prospector --files tests/_mcp_tools_extended_search_answer_context_threading_cases.py tests/_mcp_tools_extended_search_answer_context_body_cases.py tests/_tools_diagnostics_readiness_cases.py tests/_tools_diagnostics_benchmark_cases.py src/case_analysis_harvest_common.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-mcp-diagnostics-harvest-common-final-check-2026-06-29.json --tool-timeout 600000`
- Why: verify `CODACY-WC-029` MCP/diagnostics/harvest-common cleanup.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile tests/_mcp_tools_extended_search_answer_context_threading_cases.py tests/_mcp_tools_extended_search_answer_context_body_cases.py tests/_tools_diagnostics_readiness_cases.py tests/_tools_diagnostics_benchmark_cases.py src/case_analysis_harvest_common.py`
- Why: syntax-check edited MCP/diagnostics/harvest-common modules.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check tests/_mcp_tools_extended_search_answer_context_threading_cases.py tests/_mcp_tools_extended_search_answer_context_body_cases.py tests/_tools_diagnostics_readiness_cases.py tests/_tools_diagnostics_benchmark_cases.py src/case_analysis_harvest_common.py`
- Why: lint edited MCP/diagnostics/harvest-common modules.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk .venv/bin/pytest -q --tb=short tests/test_mcp_tools_extended_search.py tests/test_tools_diagnostics.py tests/test_case_analysis_transform_payload.py`
- Why: verify parent MCP, diagnostics, and case-analysis transform behavior.
- Gate type: targeted pytest.
- Result: PASS; 43 passed.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-mcp-diagnostics-harvest-common-2026-06-29.json --tool-timeout 600000`
- Why: refresh full Prospector count after `CODACY-WC-029`.
- Gate type: full local Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 377 -> 348 findings; 0 analyzer errors.
- `rtk codacy-analysis analyze --tool Prospector --files tests/test_case_analysis_transform_payload_core_quality.py tests/test_case_analysis_transform_payload_core_compaction.py tests/test_case_analysis_transform_payload_wave_local_views.py tests/_mcp_tools_extended_reporting_cases.py tests/_mcp_tools_extended_browse_scan_cases.py tests/_parse_olm_attachment_metadata_cases.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-case-mcp-parse-final-check-2026-06-29.json --tool-timeout 600000`
- Why: verify `CODACY-WC-030` case-analysis/MCP/parse metadata helper cleanup.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile tests/test_case_analysis_transform_payload_core_quality.py tests/test_case_analysis_transform_payload_core_compaction.py tests/test_case_analysis_transform_payload_wave_local_views.py tests/_mcp_tools_extended_reporting_cases.py tests/_mcp_tools_extended_browse_scan_cases.py tests/_parse_olm_attachment_metadata_cases.py`
- Why: syntax-check edited case-analysis/MCP/parse metadata modules.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check tests/test_case_analysis_transform_payload_core_quality.py tests/test_case_analysis_transform_payload_core_compaction.py tests/test_case_analysis_transform_payload_wave_local_views.py tests/_mcp_tools_extended_reporting_cases.py tests/_mcp_tools_extended_browse_scan_cases.py tests/_parse_olm_attachment_metadata_cases.py`
- Why: lint edited case-analysis/MCP/parse metadata modules.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk .venv/bin/pytest -q --tb=short tests/test_case_analysis_transform_payload_core.py tests/test_case_analysis_transform_payload_wave_local_views.py tests/test_mcp_tools_extended_search.py tests/test_parse_olm_threading.py tests/test_parse_olm_metadata.py`
- Why: verify parent case-analysis transform, MCP extended, and parse metadata/threading behavior.
- Gate type: targeted pytest.
- Result: PASS; 80 passed.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-case-mcp-parse-2026-06-29.json --tool-timeout 600000`
- Why: refresh full Prospector count after `CODACY-WC-030`.
- Gate type: full local Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 348 -> 315 findings; 0 analyzer errors.

- `rtk codacy-analysis analyze --tool Ruff --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-ruff-2026-06-28.json`
- Why: reproduce current local Ruff findings before remediation.
- Gate type: focused Codacy tool baseline.
- Result: FAIL expected; 16 Ruff findings reproduced.
- `rtk python3 -m py_compile src/case_analysis.py src/case_campaign_workflow.py src/chunker.py src/report_generator.py src/result_filters.py src/trigger_retaliation_helpers.py src/wave_local_views.py src/web_app_search.py tests/_mcp_tools_extended_reporting_cases.py`
- Why: syntax-compile edited files after UP038 changes and `chunker.py` indentation repair.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Ruff --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-ruff-clean-2026-06-28.json`
- Why: verify Codacy Ruff findings closed locally.
- Gate type: focused Codacy tool rerun.
- Result: PASS; 0 issues, 0 errors.
- `rtk .venv/bin/ruff check src/case_analysis.py src/case_campaign_workflow.py src/chunker.py src/report_generator.py src/result_filters.py src/trigger_retaliation_helpers.py src/wave_local_views.py src/web_app_search.py tests/_mcp_tools_extended_reporting_cases.py`
- Why: repository venv Ruff syntax/lint check for edited files.
- Gate type: targeted lint check.
- Result: PASS; all checks passed.
- `rtk codacy-analysis analyze --tool Semgrep --files src/case_prompt_intake_helpers.py src/promise_contradiction_analysis.py src/db_evidence_queries.py src/chunker.py src/conversation_segments.py src/multi_source_case_bundle_common.py src/writing_analyzer.py src/thread_summarizer.py src/reply_context.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-semgrep-errors-2026-06-28.json --tool-timeout 600000`
- Why: recheck prior Semgrep tool-error files before code remediation.
- Gate type: focused Codacy tool availability check.
- Result: NOT RUN BY TOOL; 0 tools ran because Opengrep binary was missing.
- `find <workspace>/.codacy -name opengrep`
- Why: verify whether Codacy-managed Opengrep binary exists locally.
- Gate type: local runtime check.
- Result: no Opengrep binary found.
- `rtk codacy-analysis analyze --tool Semgrep --install-dependencies --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-semgrep-install-2026-06-28.json --tool-timeout 600000`
- Why: retry Semgrep through Codacy-managed dependency path.
- Gate type: focused Codacy tool baseline.
- Result: ISSUES FOUND; Opengrep 1.22.0 ran globally, 56 issues and 9 errors.
- `rtk codacy-analysis analyze --tool Semgrep --files tests/_ingest_pipeline_core_cases.py tests/_ingest_pipeline_reembed_cases.py tests/_ingest_pipeline_reprocess_cases.py --install-dependencies --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-semgrep-return-init-after-2026-06-28.json --tool-timeout 600000`
- Why: verify the `return-in-init` fake collection remediation.
- Gate type: focused Codacy Semgrep rerun.
- Result: PASS; 0 issues and 0 errors on edited files.
- `rtk python3 -m py_compile tests/_ingest_pipeline_core_cases.py tests/_ingest_pipeline_reembed_cases.py tests/_ingest_pipeline_reprocess_cases.py`
- Why: syntax-compile edited ingest pipeline tests.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check tests/_ingest_pipeline_core_cases.py tests/_ingest_pipeline_reembed_cases.py tests/_ingest_pipeline_reprocess_cases.py`
- Why: lint edited ingest pipeline tests.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk .venv/bin/pytest -q --tb=short tests/_ingest_pipeline_cases.py`
- Why: targeted behavior test for edited helper files.
- Gate type: targeted pytest.
- Result: INITIALLY FAIL; 3 adjacent ingest-pipeline failures surfaced and were remediated.
- `rtk .venv/bin/pytest -q --tb=short tests/_ingest_pipeline_cases.py::test_reprocess_degraded_attachments_deletes_only_obsolete_chunk_ids`
- Why: verify stale recovered-attachment chunk deletion expectation after assertion correction.
- Gate type: targeted pytest.
- Result: PASS.
- `rtk .venv/bin/pytest -vv --tb=short tests/_ingest_pipeline_cases.py`
- Why: verify all ingest pipeline helper cases after Semgrep test-fake cleanup.
- Gate type: targeted pytest module.
- Result: PASS; 43 passed.
- `rtk codacy-analysis analyze --tool Semgrep --files tests/_ingest_pipeline_core_cases.py tests/_ingest_pipeline_reembed_cases.py tests/_ingest_pipeline_reprocess_cases.py --install-dependencies --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-semgrep-ingest-tests-clean-2026-06-28.json --tool-timeout 600000`
- Why: reverify edited ingest helper tests after behavior-test fixes.
- Gate type: focused Codacy Semgrep rerun.
- Result: PASS; 0 issues, 0 errors.
- `rtk codacy-analysis analyze --tool Semgrep --install-dependencies --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-semgrep-after-return-init-2026-06-28.json --tool-timeout 600000`
- Why: verify full Semgrep count after remediation.
- Gate type: full Semgrep rerun.
- Result: ISSUES FOUND; dropped from 56 to 51 issues, 9 parser/tool errors remain, `return-in-init` count is 0.
- `rtk codacy-analysis analyze --tool Semgrep --install-dependencies --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-semgrep-after-ingest-test-fixes-2026-06-28.json --tool-timeout 600000`
- Why: verify full Semgrep count after behavior-test fixes.
- Gate type: full Semgrep rerun.
- Result: ISSUES FOUND; still 51 issues and 9 parser/tool errors.
- `rtk .venv/bin/pytest -q --tb=short tests/_parse_olm_uid_fallback_cases.py tests/test_attachment_identity.py`
- Why: verify SHA-256 deterministic UID/hash changes.
- Gate type: targeted pytest.
- Result: PASS; 5 passed.
- `rtk python3 -m py_compile src/attachment_identity.py src/parse_olm.py tests/_parse_olm_uid_fallback_cases.py tests/test_attachment_identity.py`
- Why: syntax-compile edited hash/UID files.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/attachment_identity.py src/parse_olm.py tests/_parse_olm_uid_fallback_cases.py tests/test_attachment_identity.py`
- Why: lint edited hash/UID files.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Semgrep --files src/attachment_identity.py src/parse_olm.py --install-dependencies --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-semgrep-hash-clean-2026-06-28.json --tool-timeout 600000`
- Why: verify insecure-hash Semgrep findings closed locally.
- Gate type: focused Codacy Semgrep rerun.
- Result: PASS; 0 issues, 0 errors.
- `rtk codacy-analysis analyze --tool Semgrep --install-dependencies --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-semgrep-after-hash-fix-2026-06-28.json --tool-timeout 600000`
- Why: verify full Semgrep count after insecure-hash remediation.
- Gate type: full Semgrep rerun.
- Result: ISSUES FOUND; dropped from 51 to 48 issues, 9 parser/tool errors remain, `hash-md5` count is 0.
- `rtk .venv/bin/pytest -q --tb=short tests/test_formatting.py`
- Why: verify regex-free metadata header stripping behavior.
- Gate type: targeted pytest.
- Result: PASS; 19 passed.
- `rtk python3 -m py_compile src/formatting.py tests/test_formatting.py`
- Why: syntax-compile regex replacement and regression test.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/formatting.py tests/test_formatting.py`
- Why: lint regex replacement and regression test.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Semgrep --files src/formatting.py --install-dependencies --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-semgrep-formatting-clean-2026-06-28.json --tool-timeout 600000`
- Why: verify regex DoS Semgrep finding closed locally.
- Gate type: focused Codacy Semgrep rerun.
- Result: PASS; 0 issues, 0 errors.
- `rtk codacy-analysis analyze --tool Semgrep --install-dependencies --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-semgrep-after-regex-fix-2026-06-28.json --tool-timeout 600000`
- Why: verify full Semgrep count after regex DoS remediation.
- Gate type: full Semgrep rerun.
- Result: ISSUES FOUND; dropped from 48 to 47 issues, 9 parser/tool errors remain, `regex-dos` count is 0.

### 2026-06-28 current Codacy checkpoint

- Wrote `docs/agent/codacy_whole_corpus_current_checkpoint_2026-06-28.md`.
- `rtk codacy-analysis analyze --inspect --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-inspect-current-2026-06-28.json`
- Why: refresh current local Codacy analyzer capability before next whole-corpus remediation slice.
- Gate type: local Codacy inspect.
- Result: 13 configured tools; Semgrep still unavailable in inspect because `opengrep` is not discovered.
- `rtk codacy-analysis analyze --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-full-current-2026-06-28.json --parallel-tools 4 --tool-timeout 600000`
- Why: refresh current non-Semgrep whole-corpus findings after existing local remediation.
- Gate type: local Codacy full analysis.
- Result: ISSUES FOUND; 1,364 findings, 1 Checkov stderr warning, 10 tools ran, Ruff/Bandit/PyLintPython3 clean.
- `rtk codacy-analysis analyze --tool Semgrep --install-dependencies --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-semgrep-current-2026-06-28.json --tool-timeout 600000`
- Why: refresh Semgrep separately because inspect/full analysis skips Semgrep unless dependencies are installed/discovered.
- Gate type: focused local Codacy Semgrep analysis.
- Result: ISSUES FOUND; Opengrep 1.22.0 ran, 47 findings, 9 `Failure: int_of_string` errors.

### 2026-06-28 Prospector `_compact` remediation

- Fixed local Codacy Prospector slice `CODACY-WC-010`.
- Changed `src/case_analysis_harvest_quality.py` to import existing `._utils._compact`; no new helper added.
- Updated local ignored ledger `docs/agent/codacy_remediation_ledger.md`.
- `rtk codacy-analysis analyze --tool Prospector --files src/case_analysis_harvest_quality.py src/case_analysis_harvest_bundle.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-harvest-before-2026-06-28.json --tool-timeout 600000`
- Why: reproduce focused Prospector findings before remediation.
- Gate type: focused Codacy Prospector baseline.
- Result: ISSUES FOUND; 56 findings, including 16 `_compact` undefined-name findings.
- `rtk codacy-analysis analyze --tool Prospector --files src/case_analysis_harvest_quality.py src/case_analysis_harvest_bundle.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-harvest-after-compact-clean-2026-06-28.json --tool-timeout 600000`
- Why: verify focused `_compact` remediation.
- Gate type: focused Codacy Prospector rerun.
- Result: ISSUES FOUND; focused slice improved 56 -> 40 findings.
- `rtk python3 -m py_compile src/case_analysis_harvest_quality.py`
- Why: syntax-check edited module.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/case_analysis_harvest_quality.py`
- Why: lint edited module and stale suppression cleanup.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-compact-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after local slice.
- Gate type: full Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 749 -> 733 findings.

### 2026-06-28 Prospector harvest-bundle import restoration

- Fixed local Codacy Prospector slice `CODACY-WC-011`.
- Changed `src/case_analysis_harvest_bundle.py` to import existing sibling harvest helpers from common, coverage, expansion, and quality modules.
- Updated local ignored ledger `docs/agent/codacy_remediation_ledger.md`.
- `rtk codacy-analysis analyze --tool Prospector --files src/case_analysis_harvest_quality.py src/case_analysis_harvest_bundle.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-harvest-after-bundle-imports-final-2026-06-28.json --tool-timeout 600000`
- Why: verify focused undefined-name remediation in harvest split modules.
- Gate type: focused Codacy Prospector rerun.
- Result: ISSUES FOUND; focused slice improved 40 -> 15 findings.
- `rtk python3 -m py_compile src/case_analysis_harvest_bundle.py src/case_analysis_harvest_quality.py`
- Why: syntax-check edited harvest modules.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/case_analysis_harvest_bundle.py src/case_analysis_harvest_quality.py`
- Why: lint edited harvest modules and stale suppression cleanup.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-bundle-imports-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after bundle import restoration.
- Gate type: full Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 733 -> 708 findings.

### 2026-06-28 Prospector harvest-coverage import restoration

- Fixed local Codacy Prospector slice `CODACY-WC-012`.
- Changed `src/case_analysis_harvest_coverage.py` to import existing `._utils._compact` and shared harvest common helpers.
- Updated local ignored ledger `docs/agent/codacy_remediation_ledger.md`.
- `rtk codacy-analysis analyze --tool Prospector --files src/case_analysis_harvest_coverage.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-harvest-coverage-before-2026-06-28.json --tool-timeout 600000`
- Why: reproduce focused Prospector findings before remediation.
- Gate type: focused Codacy Prospector baseline.
- Result: ISSUES FOUND; 25 findings, including 17 undefined-name findings.
- `rtk codacy-analysis analyze --tool Prospector --files src/case_analysis_harvest_coverage.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-harvest-coverage-final-2026-06-28.json --tool-timeout 600000`
- Why: verify focused undefined-name remediation in harvest coverage split module.
- Gate type: focused Codacy Prospector rerun.
- Result: ISSUES FOUND; focused slice improved 25 -> 8 findings.
- `rtk python3 -m py_compile src/case_analysis_harvest_coverage.py`
- Why: syntax-check edited harvest coverage module.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/case_analysis_harvest_coverage.py`
- Why: lint edited harvest coverage module and stale suppression cleanup.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-coverage-imports-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after coverage import restoration.
- Gate type: full Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 708 -> 691 findings.

### 2026-06-28 Prospector QA behavior metrics import restoration

- Fixed local Codacy Prospector slice `CODACY-WC-013`.
- Changed `src/qa_eval_scoring_behavior_metrics.py` to import existing `_normalize_eval_text` and `_ratio` helpers from `qa_eval_scoring_core.py`.
- Removed unused `qa_eval_scoring_utils` import and stale Ruff suppression.
- Updated local ignored ledger `docs/agent/codacy_remediation_ledger.md`.
- `rtk codacy-analysis analyze --tool Prospector --files src/qa_eval_scoring_behavior_metrics.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-qa-behavior-before-2026-06-28.json --tool-timeout 600000`
- Why: reproduce focused Prospector findings before remediation.
- Gate type: focused Codacy Prospector baseline.
- Result: ISSUES FOUND; 6 findings.
- `rtk codacy-analysis analyze --tool Prospector --files src/qa_eval_scoring_behavior_metrics.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-qa-behavior-final-2026-06-28.json --tool-timeout 600000`
- Why: verify focused QA behavior metrics remediation.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile src/qa_eval_scoring_behavior_metrics.py`
- Why: syntax-check edited QA scoring module.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/qa_eval_scoring_behavior_metrics.py`
- Why: lint edited QA scoring module and stale suppression cleanup.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-qa-behavior-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after QA behavior metrics import restoration.
- Gate type: full Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 691 -> 685 findings.

### 2026-06-28 Prospector QA summary import restoration

- Fixed local Codacy Prospector slice `CODACY-WC-014`.
- Changed `src/qa_eval_scoring_summary.py` to import existing `_average_metric` from `qa_eval_scoring_core.py`.
- Removed unused `QuestionCase` import and stale Ruff suppression.
- Updated local ignored ledger `docs/agent/codacy_remediation_ledger.md`.
- `rtk codacy-analysis analyze --tool Prospector --files src/qa_eval_scoring_summary.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-qa-summary-before-2026-06-28.json --tool-timeout 600000`
- Why: reproduce focused Prospector findings before remediation.
- Gate type: focused Codacy Prospector baseline.
- Result: ISSUES FOUND; 23 findings.
- `rtk codacy-analysis analyze --tool Prospector --files src/qa_eval_scoring_summary.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-qa-summary-clean-2026-06-28.json --tool-timeout 600000`
- Why: verify focused QA summary remediation.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile src/qa_eval_scoring_summary.py`
- Why: syntax-check edited QA scoring module.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/qa_eval_scoring_summary.py`
- Why: lint edited QA scoring module and stale suppression cleanup.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-qa-summary-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after QA summary import restoration.
- Gate type: full Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 685 -> 662 findings.

### 2026-06-28 Prospector QA slice A import restoration

- Fixed local Codacy Prospector slice `CODACY-WC-015`.
- Changed `src/qa_eval_scoring_slice_a.py` to import existing `_as_dict`, `_as_list`, `_append_unique`, and `_ratio` helpers.
- Removed unused `Counter` import and stale Ruff suppression.
- Updated local ignored ledger `docs/agent/codacy_remediation_ledger.md`.
- `rtk codacy-analysis analyze --tool Prospector --files src/qa_eval_scoring_slice_a.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-qa-slice-a-before-2026-06-28.json --tool-timeout 600000`
- Why: reproduce focused Prospector findings before remediation.
- Gate type: focused Codacy Prospector baseline.
- Result: ISSUES FOUND; 44 findings.
- `rtk codacy-analysis analyze --tool Prospector --files src/qa_eval_scoring_slice_a.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-qa-slice-a-clean-2026-06-28.json --tool-timeout 600000`
- Why: verify focused QA slice A remediation.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile src/qa_eval_scoring_slice_a.py`
- Why: syntax-check edited QA scoring module.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/qa_eval_scoring_slice_a.py`
- Why: lint edited QA scoring module and stale suppression cleanup.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-qa-slice-a-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after QA slice A import restoration.
- Gate type: full Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 662 -> 618 findings.

### 2026-06-28 Prospector multi-source linking import restoration

- Fixed local Codacy Prospector slice `CODACY-WC-016`.
- Changed `src/multi_source_case_bundle_linking.py` to import existing helper functions from `multi_source_case_bundle_common.py`.
- Removed unused imports and stale Ruff suppression.
- Updated local ignored ledger `docs/agent/codacy_remediation_ledger.md`.
- `rtk codacy-analysis analyze --tool Prospector --files src/multi_source_case_bundle_linking.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-mscb-linking-before-2026-06-28.json --tool-timeout 600000`
- Why: reproduce focused Prospector findings before remediation.
- Gate type: focused Codacy Prospector baseline.
- Result: ISSUES FOUND; 23 findings.
- `rtk codacy-analysis analyze --tool Prospector --files src/multi_source_case_bundle_linking.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-mscb-linking-final-2026-06-28.json --tool-timeout 600000`
- Why: verify focused multi-source linking remediation.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile src/multi_source_case_bundle_linking.py`
- Why: syntax-check edited multi-source bundle module.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/multi_source_case_bundle_linking.py`
- Why: lint edited multi-source bundle module and stale suppression cleanup.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-mscb-linking-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after multi-source linking import restoration.
- Gate type: full Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 618 -> 595 findings.

### 2026-06-28 Prospector QA legal metrics import restoration

- Fixed local Codacy Prospector slice `CODACY-WC-017`.
- Changed `src/qa_eval_scoring_legal_metrics.py` to import existing helper functions from `qa_eval_scoring_core.py`.
- Removed unused `Counter` import and stale Ruff suppression.
- Updated local ignored ledger `docs/agent/codacy_remediation_ledger.md`.
- `rtk codacy-analysis analyze --tool Prospector --files src/qa_eval_scoring_legal_metrics.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-qa-legal-before-2026-06-28.json --tool-timeout 600000`
- Why: reproduce focused Prospector findings before remediation.
- Gate type: focused Codacy Prospector baseline.
- Result: ISSUES FOUND; 15 findings.
- `rtk codacy-analysis analyze --tool Prospector --files src/qa_eval_scoring_legal_metrics.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-qa-legal-clean-final-2026-06-28.json --tool-timeout 600000`
- Why: verify focused QA legal metrics remediation.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile src/qa_eval_scoring_legal_metrics.py`
- Why: syntax-check edited QA scoring module.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/qa_eval_scoring_legal_metrics.py`
- Why: lint edited QA scoring module and stale suppression cleanup.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-qa-legal-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after QA legal metrics import restoration.
- Gate type: full Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 595 -> 580 findings.

### 2026-06-28 Prospector QA case metrics import restoration

- Fixed local Codacy Prospector slice `CODACY-WC-018`.
- Changed `src/qa_eval_scoring_case_metrics.py` to import existing helper functions from `qa_eval_scoring_core.py`.
- Removed unused `Counter` import and stale Ruff suppression.
- Updated local ignored ledger `docs/agent/codacy_remediation_ledger.md`.
- `rtk codacy-analysis analyze --tool Prospector --files src/qa_eval_scoring_case_metrics.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-qa-case-before-2026-06-28.json --tool-timeout 600000`
- Why: reproduce focused Prospector findings before remediation.
- Gate type: focused Codacy Prospector baseline.
- Result: ISSUES FOUND; 10 findings.
- `rtk codacy-analysis analyze --tool Prospector --files src/qa_eval_scoring_case_metrics.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-qa-case-clean-2026-06-28.json --tool-timeout 600000`
- Why: verify focused QA case metrics remediation.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile src/qa_eval_scoring_case_metrics.py`
- Why: syntax-check edited QA scoring module.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/qa_eval_scoring_case_metrics.py`
- Why: lint edited QA scoring module and stale suppression cleanup.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-qa-case-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after QA case metrics import restoration.
- Gate type: full Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 580 -> 570 findings.

### 2026-06-28 Prospector multi-source sources import restoration

- Fixed local Codacy Prospector slice `CODACY-WC-019`.
- Changed `src/multi_source_case_bundle_sources.py` to import existing helper functions from multi-source sibling modules.
- Removed unused imports and stale Ruff suppression.
- Updated local ignored ledger `docs/agent/codacy_remediation_ledger.md`.
- `rtk codacy-analysis analyze --tool Prospector --files src/multi_source_case_bundle_sources.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-mscb-sources-before-2026-06-28.json --tool-timeout 600000`
- Why: reproduce focused Prospector findings before remediation.
- Gate type: focused Codacy Prospector baseline.
- Result: ISSUES FOUND; 11 findings.
- `rtk codacy-analysis analyze --tool Prospector --files src/multi_source_case_bundle_sources.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-mscb-sources-clean-final-2026-06-28.json --tool-timeout 600000`
- Why: verify focused multi-source sources remediation.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk python3 -m py_compile src/multi_source_case_bundle_sources.py`
- Why: syntax-check edited multi-source bundle module.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check src/multi_source_case_bundle_sources.py`
- Why: lint edited multi-source bundle module and stale suppression cleanup.
- Gate type: targeted lint check.
- Result: PASS after one-file Ruff import-sort fix.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-mscb-sources-2026-06-28.json --tool-timeout 600000`
- Why: refresh full Prospector count after multi-source sources import restoration.
- Gate type: full Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 570 -> 559 findings.

- `rtk .venv/bin/ruff check --select F401 --fix tests/_ingest_cli_cases.py tests/_ingest_entities_cases.py tests/_ingest_extended_edge_cases.py tests/_ingest_extended_progress_cases.py tests/_tools_diagnostics_runtime_cases.py tests/helpers/cli_fakes.py tests/case_workflows/test_cli_subcommands_case_parse_args.py tests/_tools_diagnostics_ops_cases.py tests/helpers/ingest_extended_fixtures.py`
- Why: remove stale imports for `CODACY-WC-031` real helper/case files.
- Gate type: targeted Ruff autofix.
- Result: PASS; 120 unused-import fixes.
- `rtk python3 -m py_compile tests/_ingest_cli_cases.py tests/_ingest_entities_cases.py tests/_ingest_extended_edge_cases.py tests/_ingest_extended_progress_cases.py tests/_mcp_tools_search_monolith.py tests/_tools_diagnostics_runtime_cases.py tests/helpers/cli_fakes.py tests/case_workflows/test_cli_subcommands_case_parse_args.py tests/_tools_diagnostics_ops_cases.py tests/helpers/ingest_extended_fixtures.py`
- Why: syntax-check edited `CODACY-WC-031` test/helper files.
- Gate type: targeted compile check.
- Result: PASS.
- `rtk .venv/bin/ruff check tests/_ingest_cli_cases.py tests/_ingest_entities_cases.py tests/_ingest_extended_edge_cases.py tests/_ingest_extended_progress_cases.py tests/_mcp_tools_search_monolith.py tests/_tools_diagnostics_runtime_cases.py tests/helpers/cli_fakes.py tests/case_workflows/test_cli_subcommands_case_parse_args.py tests/_tools_diagnostics_ops_cases.py tests/helpers/ingest_extended_fixtures.py`
- Why: lint edited `CODACY-WC-031` files.
- Gate type: targeted lint check.
- Result: PASS.
- `rtk codacy-analysis analyze --tool Prospector --files tests/_ingest_cli_cases.py tests/_ingest_entities_cases.py tests/_ingest_extended_edge_cases.py tests/_ingest_extended_progress_cases.py tests/_mcp_tools_search_monolith.py tests/_tools_diagnostics_runtime_cases.py tests/helpers/cli_fakes.py tests/case_workflows/test_cli_subcommands_case_parse_args.py tests/_tools_diagnostics_ops_cases.py tests/helpers/ingest_extended_fixtures.py --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-top-ingest-diagnostics-2026-06-29.json --tool-timeout 600000`
- Why: verify focused `CODACY-WC-031` Prospector cleanup.
- Gate type: focused Codacy Prospector rerun.
- Result: PASS; 0 issues.
- `rtk .venv/bin/pytest -q --tb=short tests/_ingest_cases.py tests/_ingest_extended_cases.py tests/_cli_commands_cases.py tests/case_workflows/test_cli_subcommands_case_parse_args.py tests/_tools_diagnostics_cases.py tests/_tools_diagnostics_summary_cases.py tests/_mcp_tools_search_monolith.py`
- Why: verify aggregate test loaders and behavior around edited test/helper files.
- Gate type: targeted pytest.
- Result: PASS; 334 passed.
- `rtk codacy-analysis analyze --tool Prospector --no-log --output-format json --output /private/tmp/outlook-email-rag-codacy-prospector-after-top-ingest-diagnostics-2026-06-29.json --tool-timeout 600000`
- Why: refresh full Prospector count after `CODACY-WC-031`.
- Gate type: full local Codacy Prospector rerun.
- Result: ISSUES FOUND; full Prospector improved 315 -> 265 findings; 0 analyzer errors.

## 2026-06-26 audit remediation (findings F1–F8)

### Scope

- Remediated all 8 findings from `AUDIT_REPORT_2026-06-26.md` on the dirty
  working tree (branch `local-state-docs-quality-sync`)
- Applied Ponytail (full) and Karpathy guidelines: surgical changes, verified
  after each step
- Wrote `docs/agent/REMEDIATION_LEDGER_2026-06-26.md` with per-finding status

### Verification

- `ruff check .`
  - Why: full lint after deleting scratch scripts and fixing imports.
  - Gate type: full lint.
  - Result: PASS (F2 resolved; 50 total errored before deletion → 0 after)
- `ruff format --check .`
  - Why: verify all tracked files formatted.
  - Gate type: full format check.
  - Result: PASS (F4 resolved; 681 files formatted)
- `ruff check src/ tests/`
  - Why: scoped application/test lint.
  - Gate type: scoped lint.
  - Result: PASS
- `mypy src`
  - Why: type check after logger additions and F5/F8 changes.
  - Gate type: full type check.
  - Result: PASS (277 files)
- `bandit -r src -q -ll -ii`
  - Why: security scan after remediation.
  - Gate type: security scan.
  - Result: PASS (existing nosec warnings only)
- `python -c "import src.cli, src.mcp_server, src.web_app, src.ingest; print('WORKTREE IMPORT OK')"`
  - Why: smoke-check import surfaces in the current working tree after F3 consolidation.
  - Gate type: import smoke.
  - Result: PASS
- F3 verification: zero `def _as_dict`, `def _as_list`, `def _compact` remain
  outside `src/_utils.py` (grep verified)
- F7 verification: 5 silent `except: pass` blocks now emit
  `logger.debug(msg, exc_info=True)` (attachment_extractor L267,L313,
  ingest_pipeline L401,L1060, mcp_server L235)

### F1 pre-commit note

- `src/_utils.py` and `src/qa_eval_scoring_utils.py` are untracked but
  imported by 52 modules. They exist on disk and all verification gates pass.
  They must be `git add`'ed before any commit.

### Checks NOT run

- Full pytest suite (3300+ tests) — not executed in this time-bound session.
- `pip-audit` / `scripts/dependency_audit.py` — not executed.
- Codacy local re-analysis — skipped; prior baseline recorded 115 findings.

## 2026-06-26 repository audit report

### Scope

- surveyed repo structure, entry points, MCP tools, ingest/runtime paths, DB/SQL helpers, dependency pins, and current dirty working tree
- wrote root audit artifact: `AUDIT_REPORT_2026-06-26.md`
- did not change production code

### Verification Plan

- `.venv/bin/ruff check .`
  - Why: identify deterministic lint failures across the current working tree.
  - Gate type: full lint.
  - Result: FAIL
    - `50` errors, all in untracked root scratch files.
- `.venv/bin/ruff check src tests`
  - Why: separate application/test lint from untracked root scratch-file noise.
  - Gate type: scoped lint.
  - Result: PASS
    - `All checks passed!`
- `.venv/bin/ruff format --check .`
  - Why: identify deterministic formatting drift.
  - Gate type: full format check.
  - Result: FAIL
    - `21` files would reformat, including touched tracked `src/` files.
- `.venv/bin/mypy src`
  - Why: verify static typing of application modules.
  - Gate type: type check.
  - Result: PASS
    - `Success: no issues found in 277 source files`
- `.venv/bin/python -c "import src.cli, src.mcp_server, src.web_app; print('WORKTREE IMPORT OK')"`
  - Why: smoke-check main import surfaces in the current working tree.
  - Gate type: import smoke.
  - Result: PASS

## 2026-04-20 publication-safety cleanup

### Scope

- added a path-only privacy scanner in `scripts/privacy_scan.py`
- added a repo contract test requiring the tracked publication surface to stay synthetic
- quarantined local private/runtime/generated artifacts outside the repository
- converted public examples and fixtures toward reserved-domain, role-based synthetic data
- renamed synthetic full-pack attendance fixtures away from private system names and regenerated dependent goldens

### Verification Plan

- `python scripts/privacy_scan.py --tracked-only --json`
  - Why: prove tracked files do not contain private artifacts or non-synthetic identifiers.
  - Gate type: publication-safety contract.
  - Result: PASS
    - output was an empty JSON list
- `python scripts/privacy_scan.py --include-history --json`
  - Why: report whether git history still contains risky paths that need a separate rewrite.
  - Gate type: history audit.
  - Result: PASS
    - output was an empty JSON list
- `python -m pytest -q --tb=short tests/test_repo_contracts.py`
  - Why: verify documentation and publication-safety contracts after cleanup.
  - Gate type: targeted regression.
  - Result: PASS
    - `41` passed
    - `2` skipped
- `python -m ruff check scripts/privacy_scan.py tests/test_repo_contracts.py`
  - Why: lint the new scanner and touched contract test.
  - Gate type: targeted lint.
  - Result: PASS
- `python -m ruff check .`
  - Why: lint the full repository after the synthetic-data rewrite touched many fixtures and expected strings.
  - Gate type: full lint.
  - Result: PASS
- `python -m ruff format --check scripts/privacy_scan.py tests/test_repo_contracts.py tests/_web_app_main_cases.py tests/test_relationship_analysis.py tests/test_triage_deep_context.py`
  - Why: verify formatting for the directly edited scanner and line-wrap fixes.
  - Gate type: targeted format check.
  - Result: PASS
- `python -m pytest -q --tb=short tests/test_repo_contracts.py tests/test_sanitization_shared.py tests/test_legal_support_exporter.py tests/test_qa_eval_cases.py`
  - Why: verify publication contracts, redaction behavior, legal-support export behavior, and QA fixture loading.
  - Gate type: targeted regression.
  - Result: PASS
    - `66` passed
    - `2` skipped
- `python scripts/refresh_qa_eval_captured_reports.py --check`
  - Why: verify regenerated synthetic QA reports and legal-support goldens match their source fixtures.
  - Gate type: captured-artifact contract.
  - Result: PASS
    - all scenarios reported `match`
- `python -m pytest -q --tb=short`
  - Why: verify the repository after synthetic fixture rewrites, generated-golden refreshes, and ingest transaction cleanup.
  - Gate type: full regression.
  - Result: PASS
    - `3296` passed
    - `3` skipped
    - `24` warnings
- `python -m src.cli --help`
  - Why: surface-probe the main CLI after public example and mailbox rewrites.
  - Gate type: CLI smoke.
  - Result: PASS
- `python -m src.cli case --help`
  - Why: surface-probe the case workflow CLI after public example and mailbox rewrites.
  - Gate type: CLI smoke.
  - Result: PASS

## 2026-04-20 public architecture and methods documentation

### Scope

- added `docs/ARCHITECTURE_AND_METHODS.md` as the public deep-dive for architecture, retrieval mathematics, evaluation methodology, and a synthetic end-to-end example
- linked the new guide from `README.md`, `docs/README.md`, and `docs/README_USAGE_AND_OPERATIONS.md`
- added repo-contract coverage for the new guide, including Mermaid and formula anchors
- replaced old public repository URL examples with neutral `example-org` metadata
- changed privacy-scan marker construction so prior sensitive marker strings do not appear literally in the scanner source

### Verification Plan

- `python scripts/privacy_scan.py --json`
  - Why: verify current tracked and untracked non-ignored files stay publication-safe.
  - Gate type: publication-safety contract.
  - Result: PASS
    - output was an empty JSON list
- `python scripts/privacy_scan.py --tracked-only --json`
  - Why: verify the tracked publication surface after adding the new public guide.
  - Gate type: publication-safety contract.
  - Result: PASS
    - output was an empty JSON list
- strict literal marker grep
  - Why: verify the current working tree no longer contains previous actor, institution, surname-substring, local-user-path, or sensitive workflow wording markers.
  - Gate type: publication-safety audit.
  - Result: PASS
    - no matches
- `python -m pytest -q --tb=short tests/test_repo_contracts.py`
  - Why: verify public documentation links and repo contracts.
  - Gate type: targeted regression.
  - Result: PASS
    - `41` passed
    - `2` skipped
- `python scripts/privacy_scan.py --include-history --json`
  - Why: verify risky path patterns in committed history.
  - Gate type: history-path audit.
  - Result: PASS
    - output was an empty JSON list
- `python -m ruff check .`
  - Why: full lint after docs, metadata, scanner, and contract-test changes.
  - Gate type: full lint.
  - Result: PASS
- `python -m ruff format --check .`
  - Why: verify repository formatting after scanner edits.
  - Gate type: full format check.
  - Result: PASS
    - `636` files already formatted
- `python -m pytest -q --tb=short`
  - Why: full regression after documentation contracts and scanner changes.
  - Gate type: full regression.
  - Result: PASS
    - `3296` passed
    - `3` skipped
    - `24` warnings
- `python -m src.cli --help`
  - Why: surface-probe the main CLI after metadata and documentation changes.
  - Gate type: CLI smoke.
  - Result: PASS
- `python -m src.cli case --help`
  - Why: surface-probe the case workflow CLI after documentation changes.
  - Gate type: CLI smoke.
  - Result: PASS

## 2026-04-20 public docs proofread and source review

### Scope

- proofread and source-hardened the public documentation set:
  `README.md`, `docs/README.md`, `docs/ARCHITECTURE_AND_METHODS.md`,
  `docs/README_USAGE_AND_OPERATIONS.md`, `docs/CLI_REFERENCE.md`,
  `docs/MCP_TOOLS.md`, `docs/RUNTIME_TUNING.md`, and
  `docs/API_COMPATIBILITY.md`
- added `docs/agent/public_docs_source_review.md` as the persistent source and
  editorial review record
- replaced person-like public examples with role-based synthetic examples
- tied retrieval mathematics and interface claims to primary or official
  sources for BM25, ColBERT, BGE-M3, ChromaDB, MCP, Outlook `.olm`, and spaCy
  NER

### Verification Plan

- `python scripts/privacy_scan.py --json`
  - Why: verify current tracked and untracked non-ignored files stay publication-safe after the public docs proofread.
  - Gate type: publication-safety contract.
  - Result: PASS
    - output was an empty JSON list
- `python scripts/privacy_scan.py --tracked-only --json`
  - Why: verify tracked publication surface after replacing person-like examples with role-based synthetic examples.
  - Gate type: publication-safety contract.
  - Result: PASS
    - output was an empty JSON list
- `python scripts/privacy_scan.py --include-history --json`
  - Why: verify risky path patterns in committed history remain absent.
  - Gate type: history-path audit.
  - Result: PASS
    - output was an empty JSON list
- public-doc marker grep
  - Why: verify the reviewed public docs do not contain previous private/institution/person-like example markers.
  - Gate type: publication-safety audit.
  - Result: PASS
    - no matches
- `python -m pytest -q --tb=short tests/test_repo_contracts.py`
  - Why: verify public documentation links, publication-safety contracts, and updated synthetic example contract.
  - Gate type: targeted regression.
  - Result: PASS
    - `41` passed
    - `2` skipped
- `python -m ruff check .`
  - Why: full lint after docs and contract-test updates.
  - Gate type: full lint.
  - Result: PASS
- `python -m ruff format --check .`
  - Why: verify repository formatting after the docs/test changes.
  - Gate type: full format check.
  - Result: PASS
    - `636` files already formatted
- `python -m pytest -q --tb=short`
  - Why: full regression after public documentation proofread, source review log, and contract update.
  - Gate type: full regression.
  - Result: PASS
    - `3296` passed
    - `3` skipped
    - `24` warnings
- `python -m src.cli --help`
  - Why: surface-probe the main CLI after updating public examples and docs contracts.
  - Gate type: CLI smoke.
  - Result: PASS
- `python -m src.cli case --help`
  - Why: surface-probe the case workflow CLI after updating public examples and docs contracts.
  - Gate type: CLI smoke.
  - Result: PASS
- `python -m src.ingest --help`
  - Why: surface-probe the ingest CLI after tightening `.olm` documentation.
  - Gate type: CLI smoke.
  - Result: PASS

## 2026-04-20 deep repo audit and GitHub polish

### Scope

- added `docs/archive/2026-05-16-remediation-closure/agent-finished-docs/repo_audit_2026-04-20.md`
  as the persistent audit record
- removed the provider-specific repo-agent GitHub workflow and prompt surface from `.github/`
- renamed the agent-specific MCP configuration guide to `docs/agent/mcp_client_config_snippet.md`
- updated public docs, advanced runbooks, and repo-contract tests to use a generic MCP-client surface
- neutralized provider-specific historical changelog wording and one temporary test fixture path
- set live GitHub topics for the public repo while keeping package and docs URLs privacy-neutral

### Verification Plan

- `python -m ruff check .`
  - Why: full lint after docs, workflow-surface, contract-test, and fixture-path changes.
  - Gate type: full lint.
  - Result: PASS
- `python -m ruff format --check .`
  - Why: verify repository formatting after the audit and GitHub-polish changes.
  - Gate type: full format check.
  - Result: PASS
    - `636` files already formatted
- `python scripts/privacy_scan.py --json`
  - Why: verify current tracked and untracked non-ignored files stay publication-safe.
  - Gate type: publication-safety contract.
  - Result: PASS
    - output was an empty JSON list
- `python scripts/privacy_scan.py --tracked-only --json`
  - Why: verify tracked publication surface after GitHub-workflow and docs cleanup.
  - Gate type: publication-safety contract.
  - Result: PASS
    - output was an empty JSON list
- `python scripts/privacy_scan.py --include-history --json`
  - Why: verify risky path patterns in committed history remain absent.
  - Gate type: history-path audit.
  - Result: PASS
    - output was an empty JSON list
- provider-specific public-surface marker grep
  - Why: verify public docs, GitHub config, packaging, changelog, and tests no longer expose the removed repo-agent workflow/client markers.
  - Gate type: publication-safety audit.
  - Result: PASS
    - no matches
- `python -m mypy src`
  - Why: full type check after the audit pass.
  - Gate type: full type check.
  - Result: PASS
    - `Success: no issues found in 247 source files`
    - only untyped-function checking notes were emitted
- `python -m bandit -r src -q -ll -ii`
  - Why: security scan after trust-boundary review.
  - Gate type: security scan.
  - Result: PASS
    - no failing Bandit issues under the configured policy
    - no Bandit `nosec` parser/tester warnings remain
- `python scripts/dependency_audit.py`
  - Why: dependency vulnerability audit for release readiness.
  - Gate type: dependency audit.
  - Result: PASS
    - `No known vulnerabilities found`
- `python -m pytest -q --tb=short tests/test_repo_contracts.py`
  - Why: verify docs, workflow-surface, and publication contracts.
  - Gate type: targeted regression.
  - Result: PASS
    - `42` passed
    - `2` skipped
- `python -m pytest -q --tb=short tests/test_matter_file_ingestion.py`
  - Why: verify the neutralized missing-path fixture still exercises degraded-source handling.
  - Gate type: targeted regression.
  - Result: PASS
    - `13` passed
- `python -m pytest -q --tb=short`
  - Why: full regression after audit, docs, workflow, and metadata changes.
  - Gate type: full regression.
  - Result: PASS
    - `3297` passed
    - `3` skipped
    - no warning summary
- `python -m src.cli --help`
  - Why: surface-probe the main CLI.
  - Gate type: CLI smoke.
  - Result: PASS
- `python -m src.cli case --help`
  - Why: surface-probe the case workflow CLI.
  - Gate type: CLI smoke.
  - Result: PASS
- `python -m src.ingest --help`
  - Why: surface-probe the ingest CLI.
  - Gate type: CLI smoke.
  - Result: PASS
- GitHub metadata read-back
  - Why: verify live GitHub polish after setting topics.
  - Gate type: live GitHub API read-back.
  - Result: PASS
    - default branch: `dev`
    - visibility: public
    - license: MIT
    - topics: `chromadb`, `ediscovery`, `email-search`, `local-first`, `mcp`, `outlook`, `privacy`, `python`, `rag`, `sqlite`

## 2026-04-20 residual audit closure

### Scope

- treated the remaining caveats as fix targets instead of release notes:
  dirty-worktree wording, full-suite warning noise, Bandit suppression noise,
  and residual provider-specific public markers
- removed provider-specific legacy operator names from tracked `.gitignore`,
  changelog wording, and repo-contract expectations
- added targeted pytest warning filters for stale flat-flag and SWIG/importlib
  deprecations
- pinned Visualized-BGE auto-download to the HuggingFace file commit used for
  `Visualized_m3.pth`
- narrowed dynamic SQL and Markup suppressions to exact audited expression lines

### Verification Plan

- `python -m pytest -q --tb=short tests/test_image_embedder.py tests/test_image_embedder_extended.py tests/test_evidence_exporter.py tests/test_email_db_analytics.py tests/test_db_queries_refactor_seams.py tests/test_db_evidence_refactor_seams.py tests/test_matter_workspace.py tests/test_qa_eval_live_deps.py`
  - Why: targeted regression for the touched image-download, HTML-export, DB-query, and live-eval surfaces.
  - Gate type: targeted regression.
  - Result: PASS
    - `96` passed
- `python -m pytest -q --tb=short tests/test_repo_contracts.py`
  - Why: verify public-surface and repository hygiene contracts after removing remaining provider-specific markers.
  - Gate type: targeted regression.
  - Result: PASS
    - `42` passed
    - `2` skipped
- public-surface marker grep over `.github README.md docs SECURITY.md pyproject.toml CHANGELOG.md .gitignore tests`
  - Why: verify provider-specific, institutional, and private-actor markers are absent from public docs, GitHub config, packaging, changelog, ignore rules, and tests.
  - Gate type: publication-safety audit.
  - Result: PASS
    - no matches
- `python -m bandit -r src -q -ll -ii`
  - Why: verify security scan after suppression hygiene and HuggingFace revision pin.
  - Gate type: security scan.
  - Result: PASS
    - no output
- `python -m ruff check .`
  - Why: full lint after code, docs, and contract changes.
  - Gate type: full lint.
  - Result: PASS
- `python -m ruff format --check .`
  - Why: full format check after final edits.
  - Gate type: full format check.
  - Result: PASS
    - `636` files already formatted
- `python scripts/privacy_scan.py --json`
  - Why: verify current working tree remains synthetic and private-artifact free.
  - Gate type: privacy scan.
  - Result: PASS
    - output was an empty JSON list
- `python scripts/privacy_scan.py --tracked-only --json`
  - Why: verify tracked publication surface remains synthetic and private-artifact free.
  - Gate type: privacy scan.
  - Result: PASS
    - output was an empty JSON list
- `python scripts/privacy_scan.py --include-history --json`
  - Why: verify history path scan remains clean under the repo's privacy scanner.
  - Gate type: privacy scan.
  - Result: PASS
    - output was an empty JSON list

## 2026-04-20 trust-boundary remediation

### Scope

- tightened MCP ingest validation so `olm_path` must be an allowlisted readable
  `.olm` file and runtime overrides must stay inside runtime roots
- removed the repository root from default output roots and rejected tracked
  repository files as export targets
- added shared no-overwrite validation for HTML/PDF, CSV, GraphML, report, and
  JSONL file writers
- changed default export destinations to `private/exports/...`
- extended `privacy_scan.py --include-history` from path-only checks to
  historical blob-content scanning without printing matched text
- updated the LOC contract to include untracked files in the dirty worktree

### Verification Plan

- `pytest -q tests/test_mcp_models_base.py tests/test_evidence_exporter.py tests/test_privacy_scan.py tests/test_repo_contracts.py::test_repo_maintained_files_stay_under_800_loc_threshold tests/test_cli_subcommands_evidence_report.py tests/test_report_generator.py::test_cli_generate_report_default tests/test_report_generator.py::test_cli_export_network_default tests/test_cli_integration.py::test_parse_args_generate_report_default tests/test_cli_integration.py::test_parse_args_export_network_default`
  - Why: targeted regression for input path validation, output overwrite guards,
    history-content scanning, LOC contract coverage, and CLI default paths.
  - Gate type: targeted regression.
  - Result: PASS
    - `53` passed
- `ruff check src/repo_paths.py src/mcp_models_base.py src/mcp_models_search.py src/formatting.py src/evidence_exporter.py src/report_generator.py src/network_analysis.py src/training_data_generator.py src/mcp_models_evidence.py src/mcp_models_analysis.py src/mcp_models_case_analysis_legal_support.py scripts/privacy_scan.py tests/test_mcp_models_base.py tests/test_evidence_exporter.py tests/test_privacy_scan.py tests/test_repo_contracts.py tests/test_cli_subcommands_evidence_report.py tests/test_report_generator.py tests/test_cli_integration.py tests/conftest.py tests/_mcp_tools_search_runtime_cases.py tests/_mcp_tools_validation_cases.py tests/test_tools_evidence_export_formats.py`
  - Why: lint the touched Python implementation and regression tests.
  - Gate type: targeted lint.
  - Result: PASS
- `ruff format --check src/repo_paths.py src/mcp_models_base.py src/mcp_models_search.py src/formatting.py src/evidence_exporter.py src/report_generator.py src/network_analysis.py src/training_data_generator.py src/mcp_models_evidence.py src/mcp_models_analysis.py src/mcp_models_case_analysis_legal_support.py scripts/privacy_scan.py tests/test_mcp_models_base.py tests/test_evidence_exporter.py tests/test_privacy_scan.py tests/test_repo_contracts.py tests/conftest.py tests/_mcp_tools_search_runtime_cases.py tests/_mcp_tools_validation_cases.py tests/test_tools_evidence_export_formats.py tests/test_cli_subcommands_evidence_report.py tests/test_report_generator.py tests/test_cli_integration.py`
  - Why: verify formatter cleanliness after the final privacy-scan and LOC-contract edits.
  - Gate type: targeted format check.
  - Result: PASS
    - `23` files already formatted
- `pytest -q`
  - Why: full regression suite after tightening shared path validation.
  - Gate type: full test suite.
  - Result: PASS
    - `3305` passed
    - `3` skipped
- `python scripts/privacy_scan.py --tracked-only --json`
  - Why: verify the current tracked publication surface remains synthetic and
    private-artifact free.
  - Gate type: privacy scan.
  - Result: PASS
    - output was an empty JSON list
- `python scripts/privacy_scan.py --tracked-only --include-history --json`
  - Why: verify the new history-content scanner runs against historical blobs.
  - Gate type: privacy scan.
  - Result: FAIL
    - the strengthened scanner now reports historical blob-content findings
      under `history-*` categories
    - no matched private text was printed; output contains categories and paths
      only
    - remediation requires a separate history-rewrite decision, not an
      in-place source patch

## 2026-04-20 follow-up remediation pass

### Scope

- rewrote local Git history with synthetic replacements and restored `origin`
- made default export roots private-only
- routed case CLI and `scripts/prepare_case_inputs.py` through shared local-read
  and new-output validators
- added bounded dependency audit wrapper `scripts/dependency_audit.py`
- routed CI and the acceptance matrix through the bounded dependency audit
  wrapper
- added a BM25 warning-as-error gate to the acceptance matrix
- resolved the legacy evidence preservation decision in
  `docs/agent/runtime_path_remediation_plan.md`
- fixed the LOC contract test's unclosed file handle

### Verification

- `ruff check .`
  - Why: full lint after trust-boundary and verification-script edits.
  - Gate type: full lint.
  - Result: PASS
- `ruff format --check .`
  - Why: full formatter check after final edits.
  - Gate type: full format check.
  - Result: PASS
    - `641` files already formatted
- `python -m mypy src`
  - Why: type-check changed source and adjacent model paths.
  - Gate type: full type check.
  - Result: PASS
    - `Success: no issues found in 247 source files`
- `pytest -q`
  - Why: full regression after path validation, history rewrite recovery, and
    moved test-path index restoration.
  - Gate type: full test suite.
  - Result: PASS
    - `3313` passed
    - `3` skipped
- `python scripts/privacy_scan.py --json`
  - Why: verify the restored dirty working tree remains current-content clean.
  - Gate type: privacy scan.
  - Result: PASS
    - output was an empty JSON list
- `python scripts/privacy_scan.py --tracked-only --include-history --json`
  - Why: verify rewritten Git history is category/path clean.
  - Gate type: history privacy scan.
  - Result: PASS
    - output was an empty JSON list
- `pytest -q tests/test_repo_contracts.py::test_repo_maintained_files_stay_under_800_loc_threshold -W error::ResourceWarning`
  - Why: verify the LOC contract no longer leaks file handles.
  - Gate type: targeted warning gate.
  - Result: PASS
- `python scripts/dependency_audit.py --timeout-seconds 1`
  - Why: verify the dependency audit wrapper has bounded failure behavior.
  - Gate type: timeout behavior probe.
  - Result: PASS
    - exited `124` with a timeout message instead of hanging

## 2026-04-20 core-four LOC refactor pass

### Scope

- split `src/tools/search_answer_context_runtime.py` into runtime lane,
  ranking, budget, search, candidate-row, and builder helpers
- split `src/qa_eval_scoring_helpers.py` into core, case, behavior, legal,
  Slice-A, and summary helpers
- split `src/multi_source_case_bundle_helpers.py` into common, linking,
  reliability, chronology, and source-normalization helpers
- split `src/case_analysis_harvest.py` into common, coverage, quality,
  expansion, and bundle helpers
- kept compatibility facades at the original import paths so existing private
  helper imports and monkeypatch paths continue to work
- removed the four refactored modules from the LOC-contract exemption set

### Verification

- `pytest -q tests/test_repo_contracts.py::test_repo_maintained_files_stay_under_800_loc_threshold`
  - Why: targeted acceptance check for the hard 800-line maintainability
    contract after removing the four exemptions.
  - Gate type: targeted contract test.
  - Result: PASS
- `ruff check .`
  - Why: full lint after splitting runtime and helper modules.
  - Gate type: full lint.
  - Result: PASS
- `ruff format --check .`
  - Why: full formatter check after final import and facade edits.
  - Gate type: full format check.
  - Result: PASS
    - `660` files already formatted
- `python -m mypy src`
  - Why: full type-check after adding compatibility facades and split helper
    modules.
  - Gate type: full type check.
  - Result: PASS
    - `Success: no issues found in 269 source files`
- `pytest -q tests/test_search_answer_context.py tests/test_search_answer_context_runtime_diversity.py tests/test_search_answer_context_case_scope.py tests/_mcp_tools_search_answer_context_core_cases.py tests/test_case_analysis_archive_harvest.py tests/test_case_analysis_archive_harvest_bundle.py tests/test_case_analysis_archive_harvest_runtime.py`
  - Why: targeted regression for answer-context runtime, monkeypatch-stable
    private runtime imports, and archive-harvest orchestration.
  - Gate type: targeted regression.
  - Result: PASS
    - `74` passed
- `pytest -q tests/test_qa_eval.py tests/test_qa_eval_scoring.py tests/test_qa_eval_slice_a_metrics.py tests/_qa_eval_scoring_tail_cases.py tests/test_multi_source_case_bundle.py tests/test_multi_source_case_bundle_linking.py tests/test_multi_source_case_bundle_sources.py tests/test_multi_source_case_bundle_chronology.py`
  - Why: targeted regression for QA scoring and multi-source case-bundle
    helper splits.
  - Gate type: targeted regression.
  - Result: PASS
    - `66` passed
- `pytest -q`
  - Why: full regression after final facade import and mypy-visibility edits.
  - Gate type: full test suite.
  - Result: PASS
    - `3313` passed
    - `3` skipped
- `python scripts/privacy_scan.py --json`
  - Why: verify the current working tree remains free of configured private
    markers after the refactor.
  - Gate type: privacy scan.
  - Result: PASS
    - output was an empty JSON list
- `python scripts/privacy_scan.py --tracked-only --include-history --json`
  - Why: verify historical tracked blobs remain clean after the refactor pass.
  - Gate type: history privacy scan.
  - Result: PASS
    - output was an empty JSON list

## 2026-04-20 GitHub cleanup and polish pass

### Scope

- replaced placeholder GitHub URLs with the canonical
  `https://github.com/sebastianspicker/outlook-email-rag` repository URL
- added lightweight issue and pull-request templates with synthetic-data
  privacy boundaries
- consolidated the public docs hub so advanced operator material routes through
  `docs/agent/README.md`
- aligned `SECURITY.md` with the bounded dependency-audit wrapper
- neutralized unpolished informal eval wording as `rapid review`
- added repo contracts for canonical URLs, GitHub templates, privacy-safe
  template content, and the advanced docs index

### Verification

- `pytest -q tests/test_repo_contracts.py`
  - Why: targeted contract check for public docs, GitHub templates, privacy
    boundaries, and repo metadata.
  - Gate type: targeted contract test.
  - Result: PASS
    - `44` passed
    - `2` skipped
- `ruff check .`
  - Why: full lint after test and docs-surface edits.
  - Gate type: full lint.
  - Result: PASS
- `ruff format --check .`
  - Why: full formatter check after repository contract edits.
  - Gate type: full format check.
  - Result: PASS
    - `660` files already formatted
- `python scripts/privacy_scan.py --json`
  - Why: verify the current working tree remains clean after GitHub-template
    and docs-surface changes.
  - Gate type: privacy scan.
  - Result: PASS
    - output was an empty JSON list
- `python scripts/privacy_scan.py --tracked-only --include-history --json`
  - Why: verify historical tracked blobs remain clean while the current
    publication surface changes.
  - Gate type: history privacy scan.
  - Result: PASS
    - output was an empty JSON list
- `pytest -q`
  - Why: full regression after updating repo contracts and touched eval
    artifacts.
  - Gate type: full test suite.
  - Result: PASS
    - `3315` passed
    - `3` skipped

## 2026-04-21 main CI answer-context budget fix

### Scope

- preserved compact behavioral candidate surfaces during answer-context budget
  trimming
- kept top-level `case_patterns` available for scoped behavioral answer-context
  responses instead of treating it as an optional removable sidecar
- added low-budget regression coverage for the CI failures where
  `language_rhetoric` and `case_patterns` disappeared from the JSON payload

### Verification

- `pytest -q --tb=short tests/test_search_answer_context_behavioral.py`
  - Why: targeted regression for the two failing CI behavioral answer-context
    tests and adjacent behavioral context cases.
  - Gate type: targeted regression.
  - Result: PASS
    - `8` passed
- `ruff check src/tools/search_answer_context_runtime_budgeting.py src/tools/search_answer_context_evidence_payloads.py tests/_search_answer_context_behavioral_language_cases.py tests/_search_answer_context_behavioral_reply_pattern_cases.py`
  - Why: targeted lint for touched source and test files.
  - Gate type: targeted lint.
  - Result: PASS
- `ruff format --check src/tools/search_answer_context_runtime_budgeting.py src/tools/search_answer_context_evidence_payloads.py tests/_search_answer_context_behavioral_language_cases.py tests/_search_answer_context_behavioral_reply_pattern_cases.py`
  - Why: targeted format check after applying `ruff format` to the touched
    budgeting module.
  - Gate type: targeted format check.
  - Result: PASS
    - `4` files already formatted
- `mypy src`
  - Why: full source type check after changing answer-context runtime helpers.
  - Gate type: full type check.
  - Result: PASS
    - `Success: no issues found in 270 source files`
- `ruff check .`
  - Why: full lint before committing the CI fix.
  - Gate type: full lint.
  - Result: PASS
- `ruff format --check .`
  - Why: full format check before committing the CI fix.
  - Gate type: full format check.
  - Result: PASS
    - `665` files already formatted
- `pytest -q --tb=short`
  - Why: full local regression before committing the CI fix.
  - Gate type: full test suite.
  - Result: PASS
    - `3359` passed
    - `3` skipped

## 2026-04-21 main CI captured-artifact stabilization

### Scope

- rounded QA average metrics to a stable precision so Python 3.11/3.12 do not
  disagree on serialized captured-report values
- refreshed captured QA reports and legal-support full-pack goldens after the
  answer-context budget-surface change
- redacted fixture-local attendance-system filenames from public full-pack
  golden projections so publication-surface privacy scans stay clean

### Verification

- `python scripts/refresh_qa_eval_captured_reports.py --check`
  - Why: exact captured-artifact contract that CI checks, expanded to all
    captured scenarios and full-pack goldens.
  - Gate type: captured artifact contract.
  - Result: PASS
    - all scenarios reported `match`
- `pytest -q --tb=short tests/test_qa_eval_captured_artifacts_refresh.py tests/test_qa_eval_core_artifacts.py tests/test_repo_contracts.py`
  - Why: targeted regression for the CI failures plus the publication-surface
    privacy contract.
  - Gate type: targeted regression.
  - Result: PASS
    - `52` passed
    - `2` skipped
- `python scripts/privacy_scan.py --tracked-only --json`
  - Why: verify refreshed public artifacts and projection code do not introduce
    publication-risk markers.
  - Gate type: privacy scan.
  - Result: PASS
    - output was an empty JSON list
- `ruff check src/legal_support_acceptance_projection.py src/qa_eval_scoring_core.py src/qa_eval_thresholds.py`
  - Why: targeted lint for touched source files.
  - Gate type: targeted lint.
  - Result: PASS
- `ruff format --check src/legal_support_acceptance_projection.py src/qa_eval_scoring_core.py src/qa_eval_thresholds.py`
  - Why: targeted format check for touched source files.
  - Gate type: targeted format check.
  - Result: PASS
    - `3` files already formatted
- `mypy src`
  - Why: full source type check after QA metric and projection helper changes.
  - Gate type: full type check.
  - Result: PASS
    - `Success: no issues found in 270 source files`
- `pytest -q --tb=short`
  - Why: full local regression before committing the captured-artifact fix.
  - Gate type: full test suite.
  - Result: PASS
    - `3359` passed
    - `3` skipped

## 2026-05-08 security remediation validation

### Scope

- validated runtime store paths through the shared runtime-root validator for
  environment settings, settings overrides, and MCP archive path updates
- removed permissive `huge_tree` parsing from shared OLM XML parser setup

### Verification

- `ruff check .`
  - Why: full lint after security remediation.
  - Gate type: full lint.
  - Result: PASS
- `ruff format --check .`
  - Why: full format check after security remediation.
  - Gate type: full format check.
  - Result: PASS
    - `665` files already formatted
- `python -m mypy src`
  - Why: full source type check after settings cache and validator changes.
  - Gate type: full type check.
  - Result: PASS
    - `Success: no issues found in 270 source files`
- `pytest -q`
  - Why: full regression after security remediation.
  - Gate type: full test suite.
  - Result: PASS
    - `3364` passed
    - `3` skipped
- `python -m bandit -r src -q -ll -ii`
  - Why: full source Bandit security scan after remediation.
  - Gate type: security scan.
  - Result: PASS
    - command exited `0`; output contained existing `nosec` parsing warnings only
- direct repro probes for `/etc/passwd` runtime path overrides and deeply nested
  OLM XML
  - Why: confirm the reported findings no longer reproduce at the original
    trust boundaries.
  - Gate type: exploit regression probe.
  - Result: PASS

## 2026-06-03 Codacy repository findings readout

### Scope

- read Codacy Cloud state for `gh/sebastianspicker/outlook-email-rag`
- confirmed the Codacy PR surface was empty and pivoted to repository findings
  on `main`
- added `docs/agent/codacy_findings_status_2026-06-03.md` with findings grouped
  by severity and rule family
- added `docs/agent/codacy_status_ledger.md` to track remote, local, and
  reanalysis status by rule family
- added `docs/agent/codacy_remediation_ledger.md` to map Codacy rule families
  to ordered remediation slices

### Verification

- `gh pr list --repo sebastianspicker/outlook-email-rag --state open --json number,title,headRefName,baseRefName,url,updatedAt`
  - Why: confirm whether a PR-scoped Codacy readout was available.
  - Gate type: remote metadata check.
  - Result: PASS
    - returned `[]`
- Codacy MCP repository, pull-request, issue, SRM, and file-list queries
  - Why: read the remote Codacy baseline and group findings by severity, rule,
    and hotspot file.
  - Gate type: remote findings readout.
  - Result: PASS
    - Codacy PR list returned `total: 0`
    - repository baseline on `main` reported grade `D` / `46`, `9,856`
      issues, `175` complex files, and `29%` duplication
    - SRM reported `7,116` open items, all `OnTrack`
- `git diff --check -- docs/agent/Documentation.md`
  - Why: verify Markdown patch whitespace for the Codacy status update.
  - Gate type: docs diff hygiene.
  - Result: PASS
- `python scripts/privacy_scan.py --tracked-only --json`
  - Why: verify the tracked publication surface after adding the Codacy status
    readout and ledger.
  - Gate type: publication-safety contract.
  - Result: PASS
    - output was an empty JSON list
- `rg -n "codacy.*remediation|Codacy.*remediation|remediation ledger" docs/agent docs/archive docs -g '*.md'`
  - Why: check whether an existing Codacy remediation ledger needed updating
    before creating a new one.
  - Gate type: docs inventory.
  - Result: PASS
    - no existing Codacy remediation ledger was found

No local code changes or test verification were performed for this readout.

## 2026-06-04 docs and GitHub hygiene pass

### Scope

- tightened GitHub issue and pull-request templates with explicit surface,
  privacy, runtime-boundary, and skipped-check prompts
- restored `.github/dependabot.yml` on the `dev` branch target and grouped
  Python dependency update PRs by runtime versus development dependencies
- expanded `.gitignore` for local Codacy output, mailbox export formats,
  runtime sidecars, JSONL/HAR/CLIXML artifacts, temp files, and local agent
  status/ledger docs
- aligned repo-contract docs with the active
  `docs/archive/2026-05-16-remediation-closure/` archive location

### Verification

- `git check-ignore -v .codacy/codacy.config.json docs/agent/codacy_status_ledger.md docs/agent/codacy_remediation_ledger.md docs/agent/codacy_findings_status_2026-06-03.md private/runtime/current/email_metadata.db data/example.olm data/example.pst data/example.mbox tmp/example.jsonl tmp/example.har tmp/example.clixml`
  - Why: prove the new and existing ignore boundaries catch local Codacy
    state, internal ledgers, private runtime state, mailbox exports, and temp
    evidence artifacts.
  - Gate type: ignore-boundary check.
  - Result: PASS
    - every path was matched by `.gitignore`
- `python -m pytest -q --tb=short tests/test_repo_contracts_security.py tests/test_repo_contracts_docs.py`
  - Why: verify repository security/publication contracts and public docs
    routing after the GitHub and archive-location updates.
  - Gate type: targeted regression.
  - Result: PASS
    - `37` passed
    - `1` skipped
- `python -m ruff check tests/test_repo_contracts_security.py tests/test_repo_contracts_docs.py`
  - Why: lint the touched repo-contract tests.
  - Gate type: targeted lint.
  - Result: PASS
- `python scripts/privacy_scan.py --tracked-only --json`
  - Why: verify the tracked publication surface remains synthetic and
    private-artifact free after docs and GitHub metadata changes.
  - Gate type: publication-safety contract.
  - Result: PASS
    - output was an empty JSON list
- `python -c "import yaml; from pathlib import Path; [yaml.safe_load(Path(p).read_text()) for p in ['.github/dependabot.yml','.github/ISSUE_TEMPLATE/config.yml','.github/ISSUE_TEMPLATE/bug_report.yml','.github/ISSUE_TEMPLATE/feature_request.yml','.github/workflows/ci.yml']]; print('yaml ok')"`
  - Why: parse GitHub YAML files touched or referenced by the hygiene pass.
  - Gate type: metadata syntax check.
  - Result: PASS
    - printed `yaml ok`
- `git diff --check`
  - Why: verify whitespace hygiene for the full current diff.
  - Gate type: diff hygiene.
  - Result: PASS

## 2026-06-04 local Codacy Analysis CLI readout

### Scope

- ran local Codacy Analysis CLI against the current dirty checkout
- wrote the actionable readout to
  `docs/agent/codacy_local_cli_readout_2026-06-04.md`
- kept local findings separate from Codacy Cloud closure status

### Verification

- `codacy-analysis analyze --inspect --output-format json --no-log`
  - Why: confirm the locally configured Codacy tools are available before
    analysis.
  - Gate type: local Codacy capability check.
  - Result: PASS
    - Ruff `0.14.14`, Bandit `1.9.3`, and PyLintPython3 `3.3.5` were ready
    - no tools were unavailable
- `codacy-analysis analyze --output-format json --no-log --tool-timeout 600000 --output /private/tmp/outlook-email-rag-codacy-local.json`
  - Why: run the current local Codacy analysis and capture structured output.
  - Gate type: local static-analysis readout.
  - Result: ISSUES FOUND
    - total issues: `17,839`
    - Ruff: `0`
    - Bandit: `88`
    - PyLintPython3: `17,751`
    - one PyLint parse warning occurred because the sandbox blocked writing a
      stats file under the user cache directory
- `codacy-analysis analyze --diff --output-format json --no-log --tool-timeout 600000 --output /private/tmp/outlook-email-rag-codacy-local-diff.json`
  - Why: try to narrow the local readout to changed files.
  - Gate type: local static-analysis scoping probe.
  - Result: NOT USEFUL
    - Codacy resolved the git diff scope to zero files and skipped analysis

## 2026-06-04 Codacy local ledger refresh

### Scope

- refreshed `docs/agent/codacy_status_ledger.md` from the fresh local Codacy
  Analysis CLI JSON
- refreshed `docs/agent/codacy_remediation_ledger.md` with the current
  remediation order
- kept the ignored local-ledger boundary explicit; these files do not represent
  Codacy Cloud closure

### Verification

- `codacy-analysis analyze --inspect --output-format json --no-log --output /private/tmp/outlook-email-rag-codacy-inspect-2026-06-04-next.json`
  - Why: confirm local Codacy tool availability before refreshing ledgers.
  - Gate type: local Codacy capability check.
  - Result: PASS
    - Ruff `0.14.14`, Bandit `1.9.3`, and PyLintPython3 `3.3.5` were ready
    - no tools were unavailable
- `codacy-analysis analyze --output-format json --no-log --tool-timeout 600000 --output /private/tmp/outlook-email-rag-codacy-local-2026-06-04-next.json`
  - Why: produce the structured local analysis baseline used by the ledgers.
  - Gate type: local static-analysis readout.
  - Result: ISSUES FOUND
    - total issues: `1,955`
    - Error: `4`; High: `12`; Warning: `126`; Info: `1,813`
    - Ruff: `25`; Bandit: `14`; PyLintPython3: `1,916`
    - four tool errors/warnings were captured, including Bandit parse failures
      for the two syntax-broken exporter tests
- `git check-ignore -v docs/agent/codacy_status_ledger.md docs/agent/codacy_remediation_ledger.md`
  - Why: prove the refreshed local ledgers remain outside the tracked public
    surface.
  - Gate type: ignore-boundary check.
  - Result: PASS
    - both files matched `.gitignore:47:docs/agent/*_ledger.md`
- `git diff --check -- docs/agent/codacy_status_ledger.md docs/agent/codacy_remediation_ledger.md`
  - Why: verify whitespace hygiene for the refreshed ledger files.
  - Gate type: docs diff hygiene.
  - Result: PASS
- Local JSON consistency check
  - Why: verify the ledger counts match the structured Codacy output before
    handoff.
  - Gate type: docs evidence consistency check.
  - Result: PASS
    - JSON totals matched the ledgers: `1,955` findings; severities
      `Info=1,813`, `Warning=126`, `Error=4`, `High=12`

## 2026-06-04 docs, GitHub, and ignore-boundary polish

### Scope

- strengthened the pull-request template with dependency/security checks,
  source-security verification prompts, and explicit incomplete-evidence
  wording
- strengthened public issue templates with runtime-state, acceptance-criteria,
  artifact-redaction, and synthetic-data prompts
- added a public repository-maintenance section to `docs/README.md`
- expanded `.gitignore` for generated coverage, junit, SARIF, profiling,
  Playwright/blob reports, Hypothesis cache, and root-only local planning
  ledgers
- removed generated `.DS_Store` files from the working tree

### Verification

- `python -c "import yaml; from pathlib import Path; [yaml.safe_load(Path(p).read_text()) for p in ['.github/dependabot.yml','.github/ISSUE_TEMPLATE/config.yml','.github/ISSUE_TEMPLATE/bug_report.yml','.github/ISSUE_TEMPLATE/feature_request.yml','.github/workflows/ci.yml']]; print('yaml ok')"`
  - Why: parse GitHub workflow, Dependabot, and issue-template YAML after
    metadata edits.
  - Gate type: metadata syntax check.
  - Result: PASS
    - printed `yaml ok`
- `git check-ignore -v .codacy/codacy.config.json .coverage .coverage.local coverage.xml htmlcov/index.html report.cover junit.junit.xml .hypothesis/examples blob-report/report.zip playwright-report/index.html output.sarif profile.prof .DS_Store docs/.DS_Store private/runtime/current/email_metadata.db data/example.olm data/example.pst data/example.mbox tmp/example.jsonl tmp/example.har tmp/example.clixml docs/agent/codacy_status_ledger.md docs/agent/codacy_remediation_ledger.md plan.md status.md local-ledger.md local-status.md local-audit.md`
  - Why: prove local Codacy, coverage, report, runtime, mailbox-export,
    temp-artifact, internal-ledger, and generated macOS residue boundaries.
  - Gate type: ignore-boundary check.
  - Result: PASS
    - every path matched an intended `.gitignore` rule
- `git diff --check -- .github .gitignore docs/README.md docs/agent/Documentation.md`
  - Why: verify whitespace hygiene for the touched docs and metadata files.
  - Gate type: diff hygiene.
  - Result: PASS
- `python scripts/privacy_scan.py --tracked-only --json`
  - Why: verify the tracked publication surface after public docs and template
    edits.
  - Gate type: publication-safety contract.
  - Result: PASS
    - output was an empty JSON list
- `python -m pytest -q --tb=short tests/test_repo_contracts_security.py tests/test_repo_contracts_docs.py`
  - Why: verify repository security/publication contracts and public docs
    routing.
  - Gate type: targeted regression.
  - Result: PASS
    - `37` passed
    - `1` skipped
- `python -m ruff check tests/test_repo_contracts_security.py tests/test_repo_contracts_docs.py`
  - Why: lint the repo-contract tests used for this documentation and
    publication-boundary slice.
  - Gate type: targeted lint.
  - Result: PASS
    - printed `All checks passed!`

## 2026-06-04 deprecated docs and local ledger archive cleanup

### Scope

- kept the deprecated audit-era docs archived under the tracked public closure
  lane `docs/archive/2026-05-16-remediation-closure/`
- moved local Codacy status, readout, and remediation ledger snapshots out of
  the active `docs/agent/` root into the ignored local archive lane:
  `docs/agent/archive/2026-06-04-codacy-local-status-ledgers/`
- updated `.gitignore` so `docs/agent/archive/` remains local-only by default
- updated `docs/agent/README.md` to distinguish public closure archives from
  ignored local status/ledger archives

### Verification

- `find docs -maxdepth 4 -type f \( -iname '*status*' -o -iname '*ledger*' -o -iname '*audit*' -o -iname '*deprecated*' -o -iname '*plan*' -o -iname '*remediation*' \) | sort`
  - Why: inventory active and archived planning/status/ledger/audit candidates
    before moving files.
  - Gate type: docs inventory.
  - Result: PASS
    - deprecated audit-era files were already present under
      `docs/archive/2026-05-16-remediation-closure/`
    - active local Codacy status/readout/ledger files were present under
      `docs/agent/`
- `git check-ignore -v docs/agent/archive/2026-06-04-codacy-local-status-ledgers/codacy_status_ledger.md docs/agent/archive/2026-06-04-codacy-local-status-ledgers/codacy_remediation_ledger.md docs/agent/archive/2026-06-04-codacy-local-status-ledgers/codacy_local_cli_readout_2026-06-04.md`
  - Why: prove local Codacy status/ledger/readout snapshots remain outside the
    tracked publication surface after archival.
  - Gate type: ignore-boundary check.
  - Result: PASS
    - all paths matched `docs/agent/archive/`
- `find docs/agent -maxdepth 1 -type f \( -iname '*status*' -o -iname '*ledger*' -o -iname 'codacy_*.md' \) -print`
  - Why: prove active local status/ledger/Codacy snapshots were removed from
    the root `docs/agent/` surface.
  - Gate type: docs boundary check.
  - Result: PASS
    - no files were returned
- archive marker grep for local absolute paths and configured private marker
  terms
  - Why: verify the public closure archive does not retain known local path or
    private-marker labels after moving archived material.
  - Gate type: archive publication-safety spot check.
  - Result: PASS
    - no matches were returned
- `python scripts/privacy_scan.py --tracked-only --json`
  - Why: verify the tracked publication surface after archive routing and
    ignore-boundary updates.
  - Gate type: publication-safety contract.
  - Result: PASS
    - output was an empty JSON list
- `python scripts/privacy_scan.py --json`
  - Why: verify tracked plus untracked non-ignored files after adding the
    public archive files.
  - Gate type: broad publication-safety probe.
  - Result: FAIL, unrelated untracked test helper
    - the archive no longer produced findings
    - the only remaining finding was
      `tests/test_repo_contracts_security.py`, an unrelated untracked test file
      outside this archive/docs slice
- `git diff --check -- .gitignore docs/README.md docs/agent/README.md docs/agent/Documentation.md docs/archive`
  - Why: verify whitespace hygiene for the archive and docs metadata changes.
  - Gate type: diff hygiene.
  - Result: PASS
- `python -m pytest -q --tb=short tests/test_repo_contracts_security.py tests/test_repo_contracts_docs.py`
  - Why: verify repository security/publication contracts and docs routing
    after moving archives.
  - Gate type: targeted regression.
  - Result: PASS
    - `37` passed
    - `1` skipped
- `python -m ruff check tests/test_repo_contracts_security.py tests/test_repo_contracts_docs.py`
  - Why: lint the repo-contract tests used for this docs/archive slice.
  - Gate type: targeted lint.
  - Result: PASS
    - printed `All checks passed!`

## 2026-06-04 public documentation local-state sync

### Scope

- updated public docs to reflect the current dirty local checkout without
  claiming release readiness
- documented current interface facts: 68 MCP tools, preferred CLI subcommands,
  deprecated-but-supported flat flags, shared CLI/MCP campaign execution, and
  conditional topic surfaces
- documented current retrieval and archive-harvest diagnostics so expanded
  thread or attachment context is not mistaken for direct retrieval coverage
- documented local tooling policy boundaries for Bandit, PyLint/Codacy, SQL
  validation, and publication privacy checks

### Verification

- `python -c "from src.mcp_server import ToolDeps, mcp; from src.tools import register_all; manager=getattr(mcp, '_tool_manager', None); tools=getattr(manager, '_tools', None); register_all(mcp, ToolDeps()) if not isinstance(tools, dict) else None; manager=getattr(mcp, '_tool_manager', None); tools=getattr(manager, '_tools', None); print(len(tools))"`
  - Why: verify the public MCP tool count before documenting local state.
  - Gate type: interface probe.
  - Result: PASS
    - printed `68`
- `python -m src.cli --help`
  - Why: verify the root CLI subcommand surface and legacy flat-flag note.
  - Gate type: CLI smoke.
  - Result: PASS
    - help listed `search`, `browse`, `export`, `case`, `evidence`,
      `analytics`, `training`, `admin`, and `topics`
- `python -m src.cli case --help`
  - Why: verify shared campaign execution wording in CLI help.
  - Gate type: CLI smoke.
  - Result: PASS
    - help listed `execute-wave`, `execute-all-waves`, `gather-evidence`, and
      the shared campaign authority note
- `python -m src.cli topics --help`
  - Why: verify the local topics subcommand before documenting it as
    conditional.
  - Gate type: CLI smoke.
  - Result: PASS
    - help listed `topics build`
- `python scripts/privacy_scan.py --tracked-only --json`
  - Why: verify the tracked publication surface after public-doc edits.
  - Gate type: publication-safety contract.
  - Result: PASS
    - output was an empty JSON list
- `git diff --check -- README.md SECURITY.md docs`
  - Why: verify whitespace hygiene for the public docs and evidence-log edits.
  - Gate type: diff hygiene.
  - Result: PASS
- `python -m pytest -q --tb=short tests/test_repo_contracts_docs.py tests/test_repo_contracts_security.py`
  - Why: verify public docs, archive routing, GitHub metadata, and publication
    contracts after the local-state sync.
  - Gate type: targeted regression.
  - Result: PASS
    - `37` passed
    - `1` skipped
- `python -m ruff check tests/test_repo_contracts_docs.py tests/test_repo_contracts_security.py`
  - Why: lint the repo-contract tests used to validate the docs slice.
  - Gate type: targeted lint.
  - Result: PASS
    - printed `All checks passed!`

## 2026-06-04 Codacy local next-step readout

### Scope

- ran Codacy Analysis CLI against the current dirty checkout to identify the
  next local remediation steps
- wrote the ignored local evidence snapshot to
  `docs/agent/archive/2026-06-04-codacy-current-run/README.md`
- kept this local baseline separate from Codacy Cloud closure status

### Verification

- `codacy-analysis analyze --inspect --output-format json --no-log --output /private/tmp/outlook-email-rag-codacy-inspect-current.json`
  - Why: confirm local analyzer availability before the current baseline run.
  - Gate type: local Codacy capability check.
  - Result: PASS
    - Ruff `0.14.14`, Bandit `1.9.3`, and PyLintPython3 `3.3.5` were ready
    - no tools were unavailable
- `codacy-analysis analyze --output-format json --no-log --tool-timeout 600000 --output /private/tmp/outlook-email-rag-codacy-current.json`
  - Why: produce the current local issue baseline and rank next remediation
    steps.
  - Gate type: local static-analysis readout.
  - Result: ISSUES FOUND
    - total local findings: `115`
    - Ruff: `1`
    - Bandit: `0`
    - PyLintPython3: `114`
    - severities: `High=13`, `Info=102`
    - one Bandit `ParseWarning` was reported from long or malformed `# nosec`
      comment text; Bandit reported no issues
- local JSON grouping script
  - Why: group the current Codacy JSON by severity, tool, pattern, and hotspot
    file.
  - Gate type: evidence consistency check.
  - Result: PASS
    - the only High cluster is `PyLintPython3_R0401` in
      `tests/test_writing_analyzer.py`
    - the only Ruff issue is blank-line whitespace in
      `tests/_ingest_extended_progress_cases.py:59`
    - main hotspots are `src/retriever.py`,
      `tests/test_writing_analyzer.py`, `src/mcp_server.py`,
      `tests/conftest.py`, `scripts/wave_workflow_smoke.py`,
      `src/network_analysis.py`, and
      `src/tools/search_answer_context_runtime_builder.py`

## 2026-06-04 Codacy local ledger update

### Scope

- recreated active local Codacy status and remediation ledgers from the current
  Codacy Analysis CLI JSON
- kept the ledgers under ignored `docs/agent/` patterns so they remain local
  operational evidence, not public release evidence
- ordered the remediation ledger around the only High cluster, then deterministic
  whitespace and Bandit parser-warning cleanup, then policy-sensitive PyLint
  style findings

### Verification

- `git check-ignore -v docs/agent/codacy_status_ledger.md docs/agent/codacy_remediation_ledger.md`
  - Why: prove active local Codacy ledgers remain outside the tracked
    publication surface.
  - Gate type: ignore-boundary check.
  - Result: PASS
    - both files matched `.gitignore`
- `git diff --check -- docs/agent/codacy_status_ledger.md docs/agent/codacy_remediation_ledger.md docs/agent/Documentation.md`
  - Why: verify whitespace hygiene for the ledger and documentation-log edits.
  - Gate type: docs diff hygiene.
  - Result: PASS
- local JSON consistency check
  - Why: verify the ledger headline counts match
    `/private/tmp/outlook-email-rag-codacy-current.json`.
  - Gate type: evidence consistency check.
  - Result: PASS
    - JSON totals matched the ledgers: `115` findings; Ruff `1`, Bandit `0`,
      PyLintPython3 `114`; severities `High=13`, `Info=102`
- `python scripts/privacy_scan.py --tracked-only --json`
  - Why: verify the tracked publication surface after updating the
    documentation log.
  - Gate type: publication-safety contract.
  - Result: PASS
    - output was an empty JSON list

## 2026-06-04 Codacy local status and remediation ledger refresh

### Scope

- recreated active local Codacy status and remediation ledgers after the prior
  ledger archive cleanup
- based the ledgers on a fresh full local Codacy Analysis CLI run
- kept local issue status separate from Codacy Cloud closure
- ranked remaining work by local severity: Error and High findings first,
  followed by warning and style/policy cleanup

### Verification

- `codacy-analysis analyze --output-format json --no-log --tool-timeout 600000 --output /private/tmp/outlook-email-rag-codacy-ledger-current-2026-06-04.json`
  - Why: get a fresh current local issue baseline for the dirty checkout before
    writing ledgers.
  - Gate type: local static-analysis readout.
  - Result: ISSUES FOUND
    - total local findings: `193`
    - Ruff: `0`
    - Bandit: `7`
    - PyLintPython3: `186`
    - severities: `Error=4`, `High=11`, `Warning=52`, `Info=126`
    - two tool warnings were reported: one Bandit nosec-comment parse warning
      and one local PyLint stats-cache write warning
- local JSON grouping script
  - Why: group the Codacy JSON by severity, tool, pattern, and hotspot file.
  - Gate type: evidence consistency check.
  - Result: PASS
    - Error findings are all `PyLintPython3_E1102` in
      `tests/test_image_embedder_extended.py`
    - High findings are all `PyLintPython3_R0401` in
      `tests/test_writing_analyzer.py`
    - remaining Bandit findings are test-only `Bandit_B404` subprocess-import
      Info findings
- `git check-ignore -v docs/agent/codacy_status_ledger.md docs/agent/codacy_remediation_ledger.md`
  - Why: prove the local ledgers remain outside the tracked publication
    surface.
  - Gate type: ignore-boundary check.
  - Result: PASS
    - both paths matched `.gitignore`

## 2026-06-04 archive-boundary correction

### Scope

- root-anchored stale planning/status/ledger ignore rules so tracked
  `docs/archive/` remediation files are no longer hidden by `.gitignore`
- archived the current active local Codacy status and remediation ledgers under
  `docs/agent/archive/2026-06-04-codacy-current-local-ledgers/`
- left `docs/agent/archive/` ignored as the local-only lane for dirty-checkout
  ledgers and evidence snapshots
- rechecked the active `docs/agent/` root and moved the latest remaining local
  Codacy ledger duplicates into the ignored archive lane

### Verification

- `git check-ignore -n -v docs/archive/2026-05-16-remediation-closure/root-remediation/remediation-ledger.md docs/archive/2026-05-16-remediation-closure/root-remediation/remediation-status.md docs/archive/2026-05-16-remediation-closure/root-remediation/deprecation-and-simplification-audit.md docs/archive/2026-05-16-remediation-closure/agent-deprecated/deprecated/Plan.md docs/agent/archive/2026-06-04-codacy-current-local-ledgers/codacy_status_ledger.md docs/agent/archive/2026-06-04-codacy-current-local-ledgers/codacy_remediation_ledger.md local-ledger.md local-status.md local-audit.md plan.md status.md`
  - Why: prove root-level scratch ledgers still ignore while tracked archive
    candidates no longer match the stale root rules.
  - Gate type: ignore-boundary check.
  - Result: PASS
    - tracked archive candidates produced no ignore matches
    - local Codacy archive and root scratch files still matched intended rules
- `find docs/agent -maxdepth 1 -type f \( -iname '*status*' -o -iname '*ledger*' -o -iname 'codacy_*.md' -o -iname '*audit*' \) -print | sort`
  - Why: verify local status/ledger/Codacy snapshots were removed from the
    active `docs/agent/` root.
  - Gate type: docs boundary check.
  - Result: PASS
    - no files were returned
- `mv docs/agent/codacy_status_ledger.md docs/agent/archive/2026-06-04-codacy-current-local-ledgers/codacy_status_ledger.md`
  and
  `mv docs/agent/codacy_remediation_ledger.md docs/agent/archive/2026-06-04-codacy-current-local-ledgers/codacy_remediation_ledger.md`
  - Why: preserve the newest ignored local ledgers while clearing the active
    agent-docs root.
  - Gate type: archive move.
  - Result: PASS
- `python -c "import yaml; from pathlib import Path; [yaml.safe_load(Path(p).read_text()) for p in ['.github/dependabot.yml','.github/ISSUE_TEMPLATE/config.yml','.github/ISSUE_TEMPLATE/bug_report.yml','.github/ISSUE_TEMPLATE/feature_request.yml','.github/workflows/ci.yml']]; print('yaml ok')"`
  - Why: parse GitHub workflow, Dependabot, and issue-template YAML after
    metadata edits.
  - Gate type: metadata syntax check.
  - Result: PASS
    - printed `yaml ok`
- `git diff --check -- .github .gitignore docs/README.md docs/agent/README.md docs/agent/Plan.md docs/agent/Documentation.md docs/archive`
  - Why: verify whitespace hygiene for the docs, archive, GitHub, and ignore
    boundary changes.
  - Gate type: diff hygiene.
  - Result: PASS
- `python scripts/privacy_scan.py --tracked-only --json`
  - Why: verify the tracked publication surface after archive routing and
    `.gitignore` corrections.
  - Gate type: publication-safety contract.
  - Result: PASS
    - output was an empty JSON list
- `python -m pytest -q --tb=short tests/test_repo_contracts_security.py tests/test_repo_contracts_docs.py`
  - Why: verify repository security/publication contracts and docs routing.
  - Gate type: targeted regression.
  - Result: PASS
    - `37` passed
    - `1` skipped
- `python -m ruff check tests/test_repo_contracts_security.py tests/test_repo_contracts_docs.py`
  - Why: lint the repo-contract tests used for this docs/archive slice.
  - Gate type: targeted lint.
  - Result: PASS
    - printed `All checks passed!`
