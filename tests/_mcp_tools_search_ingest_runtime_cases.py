"""MCP ingest runtime cases."""

import json
from unittest.mock import patch

import pytest

from .helpers.mcp_tool_fakes import _successful_ingest_runtime_fixture


@pytest.mark.asyncio
async def test_email_ingest_returns_stats_json(monkeypatch, tmp_path):
    from mailarium.mcp_models import EmailIngestInput
    from mailarium.tools.search import email_ingest

    fake_stats = {
        "emails_parsed": 10,
        "chunks_created": 15,
        "chunks_added": 15,
        "chunks_skipped": 0,
        "batches_written": 1,
        "total_in_db": 15,
        "dry_run": False,
        "elapsed_seconds": 1.2,
    }

    monkeypatch.setattr("mailarium.ingest.ingest", lambda **kwargs: fake_stats)

    olm_path = tmp_path / "test.olm"
    olm_path.write_text("olm", encoding="utf-8")
    params = EmailIngestInput(olm_path=str(olm_path))
    output = await email_ingest(params)
    data = json.loads(output)

    assert data["emails_parsed"] == 10
    assert data["chunks_added"] == 15


@pytest.mark.asyncio
async def test_email_ingest_does_not_mutate_runtime_archive_paths(monkeypatch, tmp_path):
    from mailarium.mcp_models import EmailIngestInput
    from mailarium.tools.search import email_ingest

    olm_path, active_vector_index, active_db = _successful_ingest_runtime_fixture(monkeypatch, tmp_path)
    custom_vector_index = str(tmp_path / "custom-vector-index")
    custom_db = str(tmp_path / "custom-email.db")

    with (
        patch("mailarium.mcp_server.set_runtime_archive_paths") as mock_set_paths,
        patch("mailarium.mcp_server._resolved_runtime_paths", return_value=(active_vector_index, active_db)),
        patch("mailarium.tools.search.invalidate_mcp_singletons") as mock_invalidate,
    ):
        params = EmailIngestInput(
            olm_path=str(olm_path),
            vector_index_path=custom_vector_index,
            sqlite_path=custom_db,
        )
        output = await email_ingest(params)

    data = json.loads(output)
    assert data["emails_parsed"] == 1
    assert data["ingest_archive_status"] == "inactive_target_success"
    assert data["runtime_archive_unchanged"] is True
    assert data["active_archive_switch_required"] is True
    assert data["active_archive"]["sqlite_path"] == active_db
    mock_set_paths.assert_not_called()
    mock_invalidate.assert_not_called()


@pytest.mark.asyncio
async def test_email_ingest_invalidates_cache_when_target_matches_active_runtime(monkeypatch, tmp_path):
    from mailarium.mcp_models import EmailIngestInput
    from mailarium.tools.search import email_ingest

    olm_path, active_vector_index, active_db = _successful_ingest_runtime_fixture(monkeypatch, tmp_path)

    with (
        patch("mailarium.mcp_server._resolved_runtime_paths", return_value=(active_vector_index, active_db)),
        patch("mailarium.tools.search.invalidate_mcp_singletons") as mock_invalidate,
    ):
        params = EmailIngestInput(
            olm_path=str(olm_path),
            vector_index_path=active_vector_index,
            sqlite_path=active_db,
        )
        output = await email_ingest(params)

    data = json.loads(output)
    assert data["emails_parsed"] == 1
    assert data["ingest_archive_status"] == "active_archive_updated"
    assert "runtime_archive_unchanged" not in data
    mock_invalidate.assert_called_once()


@pytest.mark.asyncio
async def test_email_ingest_handles_file_not_found(monkeypatch, tmp_path):
    from mailarium.mcp_models import EmailIngestInput
    from mailarium.tools.search import email_ingest

    def _raise(**kwargs):
        raise FileNotFoundError("not found")

    monkeypatch.setattr("mailarium.ingest.ingest", _raise)

    olm_path = tmp_path / "missing-at-ingest.olm"
    olm_path.write_text("fixture", encoding="utf-8")

    params = EmailIngestInput(olm_path=str(olm_path))
    output = await email_ingest(params)
    data = json.loads(output)

    assert "error" in data
