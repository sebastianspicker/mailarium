"""Compatibility facade for legacy extended MCP tool fakes imports."""

# ruff: noqa: F401

from .mcp_tool_answer_context_fakes import _assert_strong_attachment_candidate, _inferred_thread_dependencies
from .mcp_tool_email_db_fakes import MockEmailDB, close_sqlite_connection
from .mcp_tool_registration_fakes import FakeMCP, _register_module
from .mcp_tool_search_fakes import MockDeps, MockRetriever, _make_result
