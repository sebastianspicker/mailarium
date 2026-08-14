"""Main-page submitted-search cases."""

from __future__ import annotations

from unittest.mock import MagicMock

from .helpers.web_app_fixtures import _result, _setup_main_search_st


class _MainSearchCasesMixin:
    def test_main_search_no_query(self):
        from mailarium.web_app import main

        with self._patch_main_deps() as m:
            retriever = MagicMock()
            retriever.collection.count.return_value = 10
            m.get_retriever.return_value = retriever
            _setup_main_search_st(m.st, search_clicked=True)

            main()
            m.st.warning.assert_called_with("Please enter a query.")

    def test_main_search_with_query_and_results(self):
        from mailarium.web_app import main

        with self._patch_main_deps() as m:
            retriever = MagicMock()
            retriever.collection.count.return_value = 10
            retriever.search_filtered.return_value = [_result(), _result(chunk_id="c2")]
            m.get_retriever.return_value = retriever
            _setup_main_search_st(
                m.st,
                search_clicked=True,
                text_inputs=["contract renewal", "", "", "", "", "", "", ""],
            )

            main()
            retriever.search_filtered.assert_called_once()

    def test_main_search_invalid_date_range(self):
        from mailarium.web_app import main

        with self._patch_main_deps() as m:
            retriever = MagicMock()
            retriever.collection.count.return_value = 10
            m.get_retriever.return_value = retriever

            date_from = MagicMock()
            date_from.__str__ = MagicMock(return_value="2025-06-01")
            date_from.__bool__ = MagicMock(return_value=True)
            date_to = MagicMock()
            date_to.__str__ = MagicMock(return_value="2024-01-01")
            date_to.__bool__ = MagicMock(return_value=True)

            _setup_main_search_st(
                m.st,
                search_clicked=True,
                text_inputs=["query", "", "", "", "", "", "", ""],
                date_inputs=[date_from, date_to],
            )

            main()
            m.st.error.assert_called_with("Date From cannot be later than Date To.")

    def test_main_search_with_all_filters(self):
        from mailarium.web_app import main

        with self._patch_main_deps() as m:
            retriever = MagicMock()
            retriever.collection.count.return_value = 10
            retriever.search_filtered.return_value = [_result()]
            m.get_retriever.return_value = retriever

            _setup_main_search_st(
                m.st,
                search_clicked=True,
                text_inputs=[
                    "important query",
                    "alice@example.test",
                    "bob@example.test",
                    "Contract",
                    "Legal",
                    "carol@example.test",
                    "dave@example.test",
                    "procurement",
                ],
                number_inputs=[10, 3],
                selectbox_inputs=["Newest first", "reply"],
                slider_inputs=[0.5, 1200],
                checkbox_inputs=[True, True, True, True],
            )

            main()
            call_kwargs = retriever.search_filtered.call_args[1]
            assert call_kwargs["sender"] == "alice@example.test"
            assert call_kwargs["to"] == "bob@example.test"
            assert call_kwargs["has_attachments"] is True
            assert call_kwargs["priority"] == 3
            assert call_kwargs["email_type"] == "reply"
            assert call_kwargs["min_score"] == 0.5
            assert call_kwargs["hybrid"] is True
            assert call_kwargs["rerank"] is True
            assert call_kwargs["expand_query"] is True
            assert call_kwargs["scope"] == "procurement"

    def test_main_search_runtime_error_is_rendered_without_replacing_prior_results(self):
        from mailarium.web_app import main

        with self._patch_main_deps() as m:
            prior_results = [_result(chunk_id="prior")]
            retriever = MagicMock()
            retriever.collection.count.return_value = 10
            retriever.search_filtered.side_effect = RuntimeError("model cache unavailable")
            m.get_retriever.return_value = retriever
            _setup_main_search_st(
                m.st,
                search_clicked=True,
                text_inputs=["new query", "", "", "", "", "", "", "general"],
            )
            m.st.session_state["web_results"] = prior_results

            main()

            assert m.st.session_state["web_results"] == prior_results
            assert m.st.session_state["web_search_error"] == "RuntimeError"
            m.st.error.assert_called_with(
                "Search could not be completed. Check Admin diagnostics and the configured model/runtime paths."
            )
