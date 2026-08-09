"""MCP registration doubles for tool tests."""

from .mcp_tool_search_fakes import MockDeps


class FakeMCP:
    """Minimal MCP stub that captures tool registrations."""

    def __init__(self):
        """Implement the init behavior exposed by the FakeMCP test double."""
        self._tools = {}

    def tool(self, name=None, annotations=None):
        """Implement the tool behavior exposed by the FakeMCP test double."""

        def decorator(fn):
            self._tools[name] = fn
            return fn

        return decorator


def _register_module(module):
    """Register a tool module with a FakeMCP and MockDeps, returning the FakeMCP."""
    fake_mcp = FakeMCP()
    module.register(fake_mcp, MockDeps)
    return fake_mcp
