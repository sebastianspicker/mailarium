"""MCP administration reingestion actions and error responses."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from .helpers.diagnostics_fakes import _register, populated_mcp_caches


class TestReingestBodies:
    @pytest.mark.asyncio
    async def test_reingest_bodies_happy_path(self, tmp_path):
        fake_mcp = _register()
        fn = fake_mcp._tools["email_admin"]
        from mailarium.mcp_models import EmailAdminInput

        with populated_mcp_caches() as mcp_server:
            with patch("mailarium.ingest.reingest_bodies") as mock_fn:
                mock_fn.return_value = {"updated": 10, "skipped": 5}
                params = EmailAdminInput(
                    action="reingest_bodies",
                    olm_path=str(tmp_path / "test.olm"),
                )
                result = await fn(params)
                data = json.loads(result)
                assert data["updated"] == 10
                assert mcp_server._retriever is None
                assert mcp_server._email_db is None

    @pytest.mark.asyncio
    async def test_reingest_bodies_missing_olm_path(self):
        fake_mcp = _register()
        fn = fake_mcp._tools["email_admin"]
        from mailarium.mcp_models import EmailAdminInput

        params = EmailAdminInput(action="reingest_bodies")
        result = await fn(params)
        data = json.loads(result)
        assert "error" in data
        assert "olm_path" in data["error"]

    @pytest.mark.asyncio
    async def test_reingest_bodies_file_not_found(self):
        fake_mcp = _register()
        fn = fake_mcp._tools["email_admin"]
        from mailarium.mcp_models import EmailAdminInput

        with patch("mailarium.ingest.reingest_bodies", side_effect=FileNotFoundError):
            params = EmailAdminInput(
                action="reingest_bodies",
                olm_path="/nonexistent.olm",
            )
            result = await fn(params)
            data = json.loads(result)
            assert "error" in data

    @pytest.mark.asyncio
    async def test_reingest_bodies_generic_error(self, tmp_path):
        fake_mcp = _register()
        fn = fake_mcp._tools["email_admin"]
        from mailarium.mcp_models import EmailAdminInput

        with patch("mailarium.ingest.reingest_bodies", side_effect=RuntimeError("disk full")):
            params = EmailAdminInput(
                action="reingest_bodies",
                olm_path=str(tmp_path / "test.olm"),
            )
            result = await fn(params)
            data = json.loads(result)
            assert "error" in data

    @pytest.mark.asyncio
    async def test_reingest_bodies_with_force(self, tmp_path):
        fake_mcp = _register()
        fn = fake_mcp._tools["email_admin"]
        from mailarium.mcp_models import EmailAdminInput

        with patch("mailarium.ingest.reingest_bodies") as mock_fn:
            mock_fn.return_value = {"updated": 20, "skipped": 0}
            params = EmailAdminInput(
                action="reingest_bodies",
                olm_path=str(tmp_path / "test.olm"),
                force=True,
            )
            result = await fn(params)
            data = json.loads(result)
            assert data["updated"] == 20
            mock_fn.assert_called_once_with(str(tmp_path / "test.olm"), force=True)


class TestReingestMetadata:
    @pytest.mark.asyncio
    async def test_reingest_metadata_happy_path(self, tmp_path):
        fake_mcp = _register()
        fn = fake_mcp._tools["email_admin"]
        from mailarium.mcp_models import EmailAdminInput

        with populated_mcp_caches() as mcp_server:
            with patch("mailarium.ingest.reingest_metadata") as mock_fn:
                mock_fn.return_value = {"updated": 15}
                params = EmailAdminInput(
                    action="reingest_metadata",
                    olm_path=str(tmp_path / "test.olm"),
                )
                result = await fn(params)
                data = json.loads(result)
                assert data["updated"] == 15
                assert mcp_server._retriever is None
                assert mcp_server._email_db is None

    @pytest.mark.asyncio
    async def test_reingest_metadata_missing_olm_path(self):
        fake_mcp = _register()
        fn = fake_mcp._tools["email_admin"]
        from mailarium.mcp_models import EmailAdminInput

        params = EmailAdminInput(action="reingest_metadata")
        result = await fn(params)
        data = json.loads(result)
        assert "error" in data
        assert "olm_path" in data["error"]

    @pytest.mark.asyncio
    async def test_reingest_metadata_file_not_found(self):
        fake_mcp = _register()
        fn = fake_mcp._tools["email_admin"]
        from mailarium.mcp_models import EmailAdminInput

        with patch("mailarium.ingest.reingest_metadata", side_effect=FileNotFoundError):
            params = EmailAdminInput(
                action="reingest_metadata",
                olm_path="/nonexistent.olm",
            )
            result = await fn(params)
            data = json.loads(result)
            assert "error" in data

    @pytest.mark.asyncio
    async def test_reingest_metadata_generic_error(self, tmp_path):
        fake_mcp = _register()
        fn = fake_mcp._tools["email_admin"]
        from mailarium.mcp_models import EmailAdminInput

        with patch("mailarium.ingest.reingest_metadata", side_effect=RuntimeError("bad XML")):
            params = EmailAdminInput(
                action="reingest_metadata",
                olm_path=str(tmp_path / "test.olm"),
            )
            result = await fn(params)
            data = json.loads(result)
            assert "error" in data


class TestReingestAnalytics:
    @pytest.mark.asyncio
    async def test_reingest_analytics_happy_path(self):
        fake_mcp = _register()
        fn = fake_mcp._tools["email_admin"]
        from mailarium.mcp_models import EmailAdminInput

        with populated_mcp_caches() as mcp_server:
            with patch("mailarium.ingest.reingest_analytics") as mock_fn:
                mock_fn.return_value = {"processed": 100}
                params = EmailAdminInput(action="reingest_analytics")
                result = await fn(params)
                data = json.loads(result)
                assert data["processed"] == 100
                assert mcp_server._retriever is None
                assert mcp_server._email_db is None

    @pytest.mark.asyncio
    async def test_reingest_analytics_error(self):
        fake_mcp = _register()
        fn = fake_mcp._tools["email_admin"]
        from mailarium.mcp_models import EmailAdminInput

        with patch("mailarium.ingest.reingest_analytics", side_effect=RuntimeError("model load failed")):
            params = EmailAdminInput(action="reingest_analytics")
            result = await fn(params)
            data = json.loads(result)
            assert "error" in data
