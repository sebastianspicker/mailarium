"""Main-page saved search, thread, and pagination cases."""

from __future__ import annotations

from unittest.mock import MagicMock

from .helpers.web_app_fixtures import _result, _setup_main_search_st, _setup_main_session_results


class _MainSessionCasesMixin:
    def test_main_search_no_results_in_session(self):
        from mailarium.web_app import main

        with self._patch_main_deps() as m:
            retriever = MagicMock()
            retriever.collection.count.return_value = 10
            m.get_retriever.return_value = retriever
            _setup_main_search_st(m.st, search_clicked=False)

            main()
            m.st.info.assert_called()

    def test_main_with_existing_results_in_session(self):
        from mailarium.web_app import main

        with self._patch_main_deps() as m:
            m.st.sidebar.radio.return_value = "Search"
            m.st.sidebar.text_input.return_value = ""
            retriever = MagicMock()
            retriever.collection.count.return_value = 10
            m.get_retriever.return_value = retriever

            existing_results = [_result(), _result(chunk_id="c2")]
            _setup_main_session_results(
                m.st,
                results=existing_results,
                query="old query",
                filters={"sender": "alice"},
            )

            main()
            m.workspace.assert_called_once()
            m.summary.assert_called_once()

    def test_main_with_thread_view(self):
        from mailarium.web_app import main

        with self._patch_main_deps() as m:
            retriever = MagicMock()
            retriever.collection.count.return_value = 10
            thread_results = [_result(subject="Thread Email 1")]
            retriever.search_by_thread.return_value = thread_results
            m.get_retriever.return_value = retriever

            _setup_main_session_results(m.st, results=[_result()], thread_id="conv123")

            main()
            retriever.search_by_thread.assert_called_with("conv123")
            markdown_calls = [str(c) for c in m.st.markdown.call_args_list]
            assert any("Conversation Thread" in c for c in markdown_calls)

    def test_main_thread_view_no_results(self):
        from mailarium.web_app import main

        with self._patch_main_deps() as m:
            retriever = MagicMock()
            retriever.collection.count.return_value = 10
            retriever.search_by_thread.return_value = []
            m.get_retriever.return_value = retriever

            _setup_main_session_results(m.st, results=[_result()], thread_id="conv_empty")

            main()
            m.st.info.assert_any_call("No emails found for this thread.")

    def test_main_pagination_multiple_pages(self):
        from mailarium.web_app import main

        with self._patch_main_deps() as m:
            retriever = MagicMock()
            retriever.collection.count.return_value = 10
            m.get_retriever.return_value = retriever

            many_results = [_result(chunk_id=f"c{i}") for i in range(25)]
            _setup_main_session_results(m.st, results=many_results)

            main()
            workspace_call = m.workspace.call_args
            page_results = workspace_call.kwargs["page_results"]
            assert len(page_results) == 20
