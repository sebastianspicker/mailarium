"""MCP server diagnostics and async-offload cases."""

import json

import pytest

from mailarium.config import get_settings


@pytest.mark.asyncio
async def test_email_diagnostics_returns_json(monkeypatch):
    from mailarium.mcp_server import _offload
    from mailarium.tools import diagnostics

    class DummyEmbedder:
        device = "cpu"
        _model = type("Model", (), {"__name__": "StubModel"})()
        has_sparse = False

    class DummyRetriever:
        embedder = DummyEmbedder()
        _sparse_index = None

    class MockDeps:
        get_retriever = staticmethod(lambda: DummyRetriever())
        get_email_db = staticmethod(lambda: None)
        offload = staticmethod(_offload)

    monkeypatch.setattr(diagnostics, "_deps", MockDeps)
    monkeypatch.setenv("DEVICE", "auto")
    monkeypatch.setenv("EMBEDDING_BATCH_SIZE", "0")
    get_settings.cache_clear()

    try:
        output = await diagnostics.email_diagnostics(MockDeps)
        data = json.loads(output)

        assert "embedding_model" in data
        assert "resolved_device" in data
        assert "resolved_batch_size" in data
        assert "batch_size_setting" in data
        assert "embedder_device" in data
        assert "embedder_batch_size" in data
        assert "embedder_backend" in data
        assert "sparse_enabled" in data
        assert "late_interaction_enabled" in data
        assert "sparse_vector_count" in data
        assert "sparse_index_built" in data
    finally:
        get_settings.cache_clear()


@pytest.mark.asyncio
async def test_offload_runs_sync_in_thread():
    """_offload should run a sync function without blocking the event loop."""
    from mailarium.mcp_server import _offload

    result = await _offload(lambda: 42)
    assert result == 42


@pytest.mark.asyncio
async def test_offload_with_args():
    """_offload passes positional and keyword arguments through."""
    from mailarium.mcp_server import _offload

    result = await _offload(lambda x, y=0: x + y, 10, y=5)
    assert result == 15
