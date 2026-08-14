"""Streamlit static result-card rendering cases."""

from __future__ import annotations

from unittest.mock import patch

from mailarium.retriever import SearchResult

from .helpers.web_app_fixtures import _result, _setup_render_results_st


class TestRenderResultsBasic:
    @patch("mailarium.web_app.st")
    def test_render_results_basic(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        render_results([_result()], preview_chars=200)
        # Uses markdown header instead of subheader
        markdown_calls = [str(c) for c in mock_st.markdown.call_args_list]
        assert any("Matching Emails" in c for c in markdown_calls)

    @patch("mailarium.web_app.st")
    def test_render_results_no_subject(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        result = SearchResult(chunk_id="c1", text="body", metadata={}, distance=0.1)
        render_results([result], preview_chars=200)
        expander_title = mock_st.expander.call_args_list[0][0][0]
        assert "(no subject)" in expander_title

    @patch("mailarium.web_app.st")
    def test_render_results_multiple(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        render_results([_result(chunk_id=f"c{i}") for i in range(3)], preview_chars=200)
        assert mock_st.expander.call_count == 3

    @patch("mailarium.web_app.st")
    def test_render_results_score_clamped(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        # A negative distance yields a high score (>1.0) which should be rendered safely
        render_results([_result(score_distance=-0.5)], preview_chars=200)
        # Score is rendered as a styled badge via st.markdown, not st.progress
        markdown_calls = [str(c) for c in mock_st.markdown.call_args_list]
        assert any("score-badge" in c for c in markdown_calls)


class TestRenderResultsBodyDisplay:
    @patch("mailarium.web_app.st")
    def test_render_results_long_body_shows_full_expander(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        render_results([_result(text="x" * 500)], preview_chars=200)
        assert mock_st.expander.call_count >= 2

    @patch("mailarium.web_app.st")
    def test_render_results_short_body_no_full_expander(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        render_results([_result(text="short")], preview_chars=200)
        assert mock_st.expander.call_count == 1


class TestRenderResultsRecipients:
    @patch("mailarium.web_app.st")
    def test_render_results_with_to_recipients_truncated(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        render_results(
            [_result(to="a@example.test, b@example.test, c@example.test, d@example.test, e@example.test")],
            preview_chars=200,
        )
        # Verify columns were called
        mock_st.columns.assert_called()

    @patch("mailarium.web_app.st")
    def test_render_results_no_to_recipients(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        render_results([_result(to="")], preview_chars=200)
        # Verify it doesn't crash

    @patch("mailarium.web_app.st")
    def test_render_results_exactly_3_recipients(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        render_results([_result(to="a@example.test, b@example.test, c@example.test")], preview_chars=200)


class TestRenderResultsBadges:
    @patch("mailarium.web_app.st")
    def test_render_results_type_badge_and_att_badge(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        render_results(
            [_result(email_type="reply", attachment_count="3")],
            preview_chars=200,
        )
        # Badges are now rendered as HTML inside the expander, not in the title
        markdown_calls = [str(c) for c in mock_st.markdown.call_args_list]
        assert any("reply" in c.lower() for c in markdown_calls)
        assert any("3 att" in c for c in markdown_calls)

    @patch("mailarium.web_app.st")
    def test_render_results_original_email_type_no_badge(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        render_results([_result(email_type="original")], preview_chars=200)
        expander_title = mock_st.expander.call_args_list[0][0][0]
        assert "[ORIGINAL]" not in expander_title

    @patch("mailarium.web_app.st")
    def test_render_results_zero_att_no_badge(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        render_results([_result(attachment_count="0")], preview_chars=200)
        expander_title = mock_st.expander.call_args_list[0][0][0]
        assert "att." not in expander_title

    @patch("mailarium.web_app.st")
    def test_render_results_attachment_names_shown(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        render_results([_result(attachment_names="doc.pdf")], preview_chars=200)
        # Attachment names are now rendered via st.markdown
        markdown_calls = [str(c) for c in mock_st.markdown.call_args_list]
        assert any("doc.pdf" in c for c in markdown_calls)

    @patch("mailarium.web_app.st")
    def test_render_results_empty_attachment_names(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        render_results([_result(attachment_names="")], preview_chars=200)
        caption_calls = [str(c) for c in mock_st.caption.call_args_list]
        assert not any("Attachments:" in c for c in caption_calls)

    @patch("mailarium.web_app.st")
    def test_render_results_priority_shown(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        render_results([_result(priority="3")], preview_chars=200)
        # Priority is now rendered via st.markdown
        markdown_calls = [str(c) for c in mock_st.markdown.call_args_list]
        assert any("Priority" in c for c in markdown_calls)

    @patch("mailarium.web_app.st")
    def test_render_results_priority_zero_not_shown(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        render_results([_result(priority="0")], preview_chars=200)
        caption_calls = [str(c) for c in mock_st.caption.call_args_list]
        assert not any("Priority:" in c for c in caption_calls)

    @patch("mailarium.web_app.st")
    def test_render_results_empty_priority_not_shown(self, mock_st):
        from mailarium.web_app import render_results

        _setup_render_results_st(mock_st)
        render_results([_result(priority="")], preview_chars=200)
        caption_calls = [str(c) for c in mock_st.caption.call_args_list]
        assert not any("Priority:" in c for c in caption_calls)
