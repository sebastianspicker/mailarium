"""Focused contracts for the mockup-matching search workspace."""

from __future__ import annotations

from unittest.mock import MagicMock

from mailarium.web_app_workspace import render_search_workspace_impl

from .helpers.web_app_fixtures import _result


def _workspace_streamlit() -> MagicMock:
    st_module = MagicMock()
    st_module.session_state = {"web_query": "handoff"}
    st_module.columns.side_effect = lambda widths, **_kwargs: [MagicMock() for _ in widths]
    st_module.button.return_value = False
    st_module.expander.return_value.__enter__ = MagicMock(return_value=MagicMock())
    st_module.expander.return_value.__exit__ = MagicMock(return_value=False)
    return st_module


def _render(st_module: MagicMock, results: list) -> None:
    render_search_workspace_impl(
        st_module=st_module,
        retriever=MagicMock(),
        results=results,
        page_results=results,
        page=0,
        page_size=20,
        total_pages=1,
        filters={"hybrid": True, "rerank": True},
        sort_value="relevance",
        build_export_payload_fn=lambda **values: values,
        build_csv_export_fn=lambda _results: "header\n",
    )


def _document_markup(st_module: MagicMock) -> str:
    """Return the rendered selected-document article from a workspace render."""
    return st_module.markdown.call_args_list[3].args[0]


def test_workspace_defaults_to_first_result_and_renders_all_three_panes():
    st_module = _workspace_streamlit()
    results = [_result(chunk_id="first"), _result(chunk_id="second")]

    _render(st_module, results)

    assert st_module.session_state["web_selected_chunk_id"] == "first"
    rendered = "\n".join(str(call) for call in st_module.markdown.call_args_list)
    assert "mailarium-results-marker" in rendered
    assert "mailarium-document-marker" in rendered
    assert "mailarium-inspector-marker" in rendered
    assert "<span>Source</span>" in rendered


def test_workspace_renders_fully_escaped_document_markup():
    st_module = _workspace_streamlit()
    result = _result(
        subject="<script>alert(1)</script>",
        sender_name="Alice <Operations>",
        sender_email="alice&ops@example.com",
        to="Team <team@example.com> & Legal",
        date="2024-01-15T09:30:45",
        folder="Inbox & <Priority>",
        text="<img src=x onerror=alert(1)>. This sentence is long enough to become quoted proof.",
    )

    _render(st_module, [result])

    assert _document_markup(st_module) == (
        "<article class='archive-document'>"
        "<header><h2>&lt;script&gt;alert(1)&lt;/script&gt;</h2>"
        "<div class='document-actions' aria-hidden='true'>&#8942;</div></header>"
        "<div class='document-metadata'>"
        "<span><b>From</b>Alice &lt;Operations&gt; &lt;alice&amp;ops@example.com&gt;</span>"
        "<span><b>Date</b>2024-01-15 · 09:30:45</span>"
        "<span><b>To</b>Team &lt;team@example.com&gt; &amp; Legal</span>"
        "<span><b>Source</b>Inbox &amp; &lt;Priority&gt;</span>"
        "</div>"
        "<div class='thread-line'><span class='thread-dots' aria-hidden='true'>&#9679;&mdash;&#9675;&mdash;&#9675;</span>"
        "<span>Single indexed message</span></div>"
        "<div class='document-body'>&lt;img src=x onerror=alert(1)&gt;. "
        "<mark class='provenance-highlight'>This sentence is long enough to become quoted proof.</mark></div>"
        "<div class='document-attachments'><small>0 attachments</small>"
        "<div class='document-empty-attachments'>No attachments recorded</div></div>"
        "</article>"
    )
    assert st_module.markdown.call_args_list[3].kwargs == {"unsafe_allow_html": True}


def test_workspace_renders_only_first_four_escaped_attachments():
    st_module = _workspace_streamlit()
    result = _result(
        attachment_names="brief<1>.pdf; owners&2.xlsx, notes.txt; plan.docx; hidden.png",
    )

    _render(st_module, [result])

    document = _document_markup(st_module)
    assert "<small>5 attachments</small>" in document
    assert "<strong>brief&lt;1&gt;.pdf</strong>" in document
    assert "<strong>owners&amp;2.xlsx</strong>" in document
    assert "<strong>notes.txt</strong>" in document
    assert "<strong>plan.docx</strong>" in document
    assert "hidden.png" not in document
    assert "No attachments recorded" not in document


def test_workspace_uses_metadata_fallbacks_for_sender_and_source():
    st_module = _workspace_streamlit()
    result = _result(sender_name="", sender_email="", folder="", attachment_names="")

    _render(st_module, [result])

    document = _document_markup(st_module)
    assert "<span><b>From</b>Unknown sender</span>" in document
    assert "<span><b>Source</b>Archive</span>" in document
    assert "<div class='document-empty-attachments'>No attachments recorded</div>" in document


def test_workspace_thread_button_updates_session_and_reruns_only_for_available_thread():
    st_module = _workspace_streamlit()
    st_module.button.side_effect = [False, True, False]

    _render(st_module, [_result(conversation_id="thread-42")])

    assert st_module.session_state["web_thread_id"] == "thread-42"
    st_module.rerun.assert_called_once_with()
    assert st_module.button.call_args_list[1].args == ("View full thread",)
    assert st_module.button.call_args_list[1].kwargs == {
        "key": "workspace-thread-c1",
        "use_container_width": True,
    }

    no_thread = _workspace_streamlit()
    _render(no_thread, [_result(conversation_id="")])

    assert all(call.args[0] != "View full thread" for call in no_thread.button.call_args_list)
    assert "web_thread_id" not in no_thread.session_state
    no_thread.rerun.assert_not_called()
