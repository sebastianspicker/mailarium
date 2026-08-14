"""MCP administration reembedding actions and error responses."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from .helpers.diagnostics_fakes import _register, populated_mcp_caches


class TestReembed:
    @pytest.mark.asyncio
    async def test_reembed_happy_path(self):
        fake_mcp = _register()
        fn = fake_mcp._tools["email_admin"]
        from mailarium.mcp_models import EmailAdminInput

        with populated_mcp_caches() as mcp_server:
            with patch("mailarium.ingest.reembed") as mock_fn:
                mock_fn.return_value = {"chunks_embedded": 500}
                params = EmailAdminInput(action="reembed", batch_size=50)
                result = await fn(params)
                data = json.loads(result)
                assert data["chunks_embedded"] == 500
                mock_fn.assert_called_once_with(batch_size=50)
                assert mcp_server._retriever is None
                assert mcp_server._email_db is None

    @pytest.mark.asyncio
    async def test_reembed_error(self):
        fake_mcp = _register()
        fn = fake_mcp._tools["email_admin"]
        from mailarium.mcp_models import EmailAdminInput

        with patch("mailarium.ingest.reembed", side_effect=RuntimeError("OOM")):
            params = EmailAdminInput(action="reembed")
            result = await fn(params)
            data = json.loads(result)
            assert "error" in data
