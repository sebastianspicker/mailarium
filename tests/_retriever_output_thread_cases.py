"""Retriever conversation-thread lookup behavior."""

from unittest.mock import MagicMock

import pytest

from tests.helpers.retriever_cases import _bare_retriever, _thread_collection


class TestSearchByThread:
    def test_empty_conversation_id_returns_empty(self):
        r = _bare_retriever()
        assert r.search_by_thread("") == []
        assert r.search_by_thread("   ") == []

    def test_raises_on_non_positive_top_k(self):
        r = _bare_retriever()
        with pytest.raises(ValueError, match="positive"):
            r.search_by_thread("conv1", top_k=0)

    def test_empty_get_returns_empty(self):
        r = _bare_retriever()
        r.collection = MagicMock()
        r.collection.get.return_value = {"ids": []}

        assert r.search_by_thread("conv1") == []

    def test_returns_results_sorted_by_date(self):
        r = _bare_retriever()
        r.collection = _thread_collection(
            ids=["c1", "c2"],
            documents=["body1", "body2"],
            metadatas=[
                {"uid": "u1", "date": "2024-01-02", "conversation_id": "conv1"},
                {"uid": "u2", "date": "2024-01-01", "conversation_id": "conv1"},
            ],
        )

        thread = r.search_by_thread("conv1")
        assert thread[0].metadata["date"] == "2024-01-01"
        assert thread[1].metadata["date"] == "2024-01-02"

        r.collection.get.assert_called_once()
        call_kwargs = r.collection.get.call_args
        assert call_kwargs[1]["where"] == {"conversation_id": {"$eq": "conv1"}}

    def test_deduplicates_results(self):
        r = _bare_retriever()
        r.collection = MagicMock()
        r.collection.get.return_value = {
            "ids": ["c1", "c1b", "c2"],
            "documents": ["body1", "body1b", "body2"],
            "metadatas": [
                {"uid": "u1", "date": "2024-01-01"},
                {"uid": "u1", "date": "2024-01-01"},
                {"uid": "u2", "date": "2024-01-02"},
            ],
        }

        thread = r.search_by_thread("conv1")
        uids = [result.metadata["uid"] for result in thread]
        assert uids == ["u1", "u2"]

    def test_prefers_one_body_row_over_attachment_chunks_for_same_email(self):
        r = _bare_retriever()
        r.collection = MagicMock()
        r.collection.get.return_value = {
            "ids": ["u1__att_0_0", "u1__0", "u1__att_1_0"],
            "documents": ["attachment one", "email body", "attachment two"],
            "metadatas": [
                {"uid": "u1", "date": "2024-01-01", "attachment_filename": "one.pdf"},
                {"uid": "u1", "date": "2024-01-01"},
                {"uid": "u1", "date": "2024-01-01", "attachment_filename": "two.pdf"},
            ],
        }

        thread = r.search_by_thread("conv1")

        assert [item.chunk_id for item in thread] == ["u1__0"]

    def test_sorts_thread_results_by_parsed_timestamp_not_raw_string(self):
        r = _bare_retriever()
        r.collection = _thread_collection(
            ids=["c1", "c2"],
            documents=["body1", "body2"],
            metadatas=[
                {"uid": "u1", "date": "Wed, 25 Jun 2025 10:52:47 +0200", "conversation_id": "conv1"},
                {"uid": "u2", "date": "2025-06-25T08:00:00+00:00", "conversation_id": "conv1"},
            ],
        )

        thread = r.search_by_thread("conv1")

        assert [item.metadata["uid"] for item in thread] == ["u2", "u1"]
