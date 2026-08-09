"""Compatibility facade for diagnostics-tool test doubles and fixtures."""

from .diagnostics_base_fakes import MockDeps, MockEmailDB, MockRetriever, SqliteConnectionOwner, ToolDependencyAnnotations
from .diagnostics_cache_fixtures import populated_mcp_caches
from .diagnostics_database_fixtures import diagnostics_database
from .diagnostics_mcp_fakes import FakeMCP, _register
from .diagnostics_report_fixtures import (
    answer_task_readiness,
    standard_core_summary,
    write_diagnostics_report,
    write_json_artifact,
)

__all__ = (
    "FakeMCP",
    "MockDeps",
    "MockEmailDB",
    "MockRetriever",
    "SqliteConnectionOwner",
    "ToolDependencyAnnotations",
    "_register",
    "answer_task_readiness",
    "diagnostics_database",
    "populated_mcp_caches",
    "standard_core_summary",
    "write_diagnostics_report",
    "write_json_artifact",
)
