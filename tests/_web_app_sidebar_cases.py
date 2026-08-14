"""Streamlit sidebar and style rendering cases."""

from __future__ import annotations

from unittest.mock import patch

from .helpers.web_app_fixtures import _sidebar_retriever


class TestInjectStyles:
    @patch("mailarium.web_app.st")
    def test_inject_styles_renders_css(self, mock_st):
        from mailarium.web_app import inject_styles

        inject_styles()
        mock_st.markdown.assert_called_once()
        call_args = mock_st.markdown.call_args
        assert "<style>" in call_args[0][0]
        assert "#07110f" in call_args[0][0]
        assert "#f47732" in call_args[0][0]
        assert "prefers-reduced-motion" in call_args[0][0]
        assert "mailarium-lockup" in call_args[0][0]
        assert "LUMINOUS ARCHIVE" not in call_args[0][0]
        assert call_args[1]["unsafe_allow_html"] is True


class TestRenderSidebar:
    @patch("mailarium.web_app.st")
    def test_render_sidebar_with_stats_and_folders(self, mock_st):
        from mailarium.web_app import render_sidebar

        retriever = _sidebar_retriever(
            mock_st,
            stats={
                "total_emails": 100,
                "total_chunks": 500,
                "unique_senders": 25,
                "date_range": {"earliest": "2020-01-01", "latest": "2024-06-15"},
                "folders": {"Inbox": 80, "Sent": 20},
            },
            senders=[
                {"name": "Alice", "email": "employee@example.test", "count": 50},
                {"name": "Bob", "email": "bob@example.com", "count": 30},
            ],
        )

        render_sidebar(retriever)

        mock_st.sidebar.markdown.assert_any_call("#### Archive Overview")
        # Uses columns for metrics
        mock_st.sidebar.columns.assert_called()

    @patch("mailarium.web_app.st")
    def test_render_sidebar_no_folders(self, mock_st):
        from mailarium.web_app import render_sidebar

        retriever = _sidebar_retriever(
            mock_st,
            stats={"total_emails": 0, "total_chunks": 0, "unique_senders": 0, "date_range": {}, "folders": {}},
            senders=[],
        )

        render_sidebar(retriever)

        mock_st.sidebar.caption.assert_called_once_with("No dated messages indexed.")

    @patch("mailarium.web_app.st")
    def test_render_sidebar_sender_with_no_name(self, mock_st):
        from mailarium.web_app import render_sidebar

        retriever = _sidebar_retriever(
            mock_st,
            stats={
                "total_emails": 1,
                "total_chunks": 1,
                "unique_senders": 1,
                "date_range": {"earliest": "2024-01-01", "latest": "2024-01-01"},
                "folders": {},
            },
            senders=[{"name": "", "email": "anon@example.com", "count": 5}],
        )

        render_sidebar(retriever)

        # Sender with empty name now uses email as fallback
        markdown_calls = [str(c) for c in mock_st.markdown.call_args_list]
        assert any("anon@example.com" in c for c in markdown_calls)
