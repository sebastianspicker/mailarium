"""MCP registration doubles shared by diagnostics-tool tests."""

from __future__ import annotations

from .diagnostics_base_fakes import MockDeps


class FakeMCP:
    """Test double carrying deterministic FakeMCP state for focused unit tests."""

    def __init__(self):
        """Implement the init behavior exposed by the FakeMCP test double."""
        self._tools = {}

    def tool(self, name=None, annotations=None):
        """Implement the tool behavior exposed by the FakeMCP test double."""

        def decorator(fn):
            self._tools[name] = fn
            return fn

        return decorator


def _register():
    """Provide deterministic register behavior for focused test setup."""
    from mailarium.tools import diagnostics

    fake_mcp = FakeMCP()
    diagnostics.register(fake_mcp, MockDeps)
    return fake_mcp
