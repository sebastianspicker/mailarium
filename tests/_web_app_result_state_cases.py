"""Streamlit result state, navigation, and summary rendering cases."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from .helpers.web_app_fixtures import _columns_side_effect, _result, _setup_render_results_st


class TestRenderResultsThread:
    @patch("mailarium.web_app.st")
    def test_render_results_thread_button(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        mock_st.button.return_value = False
        mock_st.session_state = {}
        render_results(
            [_result(conversation_id="conv123")],
            preview_chars=200,
            retriever=MagicMock(),
        )
        mock_st.button.assert_called()

    @patch("mailarium.web_app.st")
    def test_render_results_no_conversation_id_no_button(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        render_results(
            [_result(conversation_id="")],
            preview_chars=200,
            retriever=MagicMock(),
        )
        mock_st.button.assert_not_called()

    @patch("mailarium.web_app.st")
    def test_render_results_no_retriever_no_button(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        render_results(
            [_result(conversation_id="conv123")],
            preview_chars=200,
            retriever=None,
        )
        mock_st.button.assert_not_called()

    @patch("mailarium.web_app.st")
    def test_render_results_inferred_thread_shows_scope_note(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        result = _result(conversation_id="")
        result.metadata["inferred_thread_id"] = "thread-inferred-1"

        render_results(
            [result],
            preview_chars=200,
            retriever=MagicMock(),
        )

        caption_calls = [str(call) for call in mock_st.caption.call_args_list]
        assert any("canonical conversation IDs" in call for call in caption_calls)

    @patch("mailarium.web_app.st")
    def test_render_results_thread_button_clicked(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        mock_st.button.return_value = True
        mock_st.session_state = {}

        render_results(
            [_result(conversation_id="conv_click")],
            preview_chars=200,
            retriever=MagicMock(),
        )
        assert mock_st.session_state.get("web_thread_id") == "conv_click"
        mock_st.rerun.assert_called()


class TestRenderResultsSummary:
    @patch("mailarium.web_app.st")
    def test_renders_compact_summary(self, mock_st):
        from mailarium.web_app import render_results_summary

        mock_st.columns.side_effect = _columns_side_effect
        render_results_summary(
            [_result(score_distance=0.2), _result(score_distance=0.4)],
            ["Sender: alice"],
            "Relevance",
        )
        summary_html = str(mock_st.markdown.call_args_list[0])
        assert "result-summary" in summary_html
        assert "2 results" in summary_html

    @patch("mailarium.web_app.st")
    def test_renders_filter_chips(self, mock_st):
        from mailarium.web_app import render_results_summary

        mock_st.columns.side_effect = _columns_side_effect
        render_results_summary([_result()], ["Sender: alice", "Folder: Inbox"], "Relevance")
        mock_st.markdown.assert_called()

    @patch("mailarium.web_app.st")
    def test_empty_results(self, mock_st):
        from mailarium.web_app import render_results_summary

        render_results_summary([], [], "Relevance")
        assert "0 results" in str(mock_st.markdown.call_args_list[0])

    @patch("mailarium.web_app.st")
    def test_no_filter_chips_when_empty(self, mock_st):
        from mailarium.web_app import render_results_summary

        mock_st.columns.side_effect = _columns_side_effect
        render_results_summary([_result()], [], "Relevance")
        chip_calls = [c for c in mock_st.markdown.call_args_list if "filter-chip" in str(c)]
        assert len(chip_calls) == 0
