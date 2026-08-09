"""MCP-cache fixtures shared by diagnostics-tool tests."""

from __future__ import annotations

import threading
from contextlib import contextmanager


@contextmanager
def populated_mcp_caches():
    """Temporarily seed MCP caches so mutating admin actions must clear them."""
    from mailarium import mcp_server

    original_retriever = mcp_server._retriever
    original_email_db = mcp_server._email_db
    original_retriever_lock = mcp_server._retriever_lock
    original_email_db_lock = mcp_server._email_db_lock
    try:
        mcp_server._retriever = object()
        mcp_server._email_db = object()
        mcp_server._retriever_lock = threading.Lock()
        mcp_server._email_db_lock = threading.Lock()
        yield mcp_server
    finally:
        mcp_server._retriever = original_retriever
        mcp_server._email_db = original_email_db
        mcp_server._retriever_lock = original_retriever_lock
        mcp_server._email_db_lock = original_email_db_lock
