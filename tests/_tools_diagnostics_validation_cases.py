"""Diagnostics-model validation cases."""

from __future__ import annotations

import pytest


class TestInvalidAction:
    @pytest.mark.asyncio
    async def test_invalid_action(self):
        from pydantic import ValidationError

        from mailarium.mcp_models import EmailAdminInput

        with pytest.raises(ValidationError, match="action"):
            EmailAdminInput(action="destroy_everything")
