"""Retriever BM25-index result behavior."""

import types
from unittest.mock import MagicMock, patch

from tests.helpers.retriever_cases import _bare_retriever


class TestGetBM25Results:
    def test_returns_chunk_ids_on_success(self):
        r = _bare_retriever()
        mock_bm25 = MagicMock()
        mock_bm25.is_built = True
        mock_bm25.search.return_value = [("c1", 0.5), ("c2", 0.3)]
        r._bm25_index = mock_bm25

        result = r._get_bm25_results("test", 10)
        assert result == ["c1", "c2"]

    def test_returns_none_when_not_built(self):
        r = _bare_retriever()
        mock_bm25 = MagicMock()
        mock_bm25.is_built = False
        r._bm25_index = mock_bm25

        result = r._get_bm25_results("test", 10)
        assert result is None

    def test_builds_from_collection_on_first_call(self):
        r = _bare_retriever()
        r._bm25_index = None
        r.collection = MagicMock()

        mock_bm25_instance = MagicMock()
        mock_bm25_instance.is_built = True
        mock_bm25_instance.search.return_value = [("c1", 0.5)]

        mock_bm25_module = types.ModuleType("mailarium.bm25_index")
        mock_bm25_module.BM25Index = MagicMock(return_value=mock_bm25_instance)
        with patch.dict("sys.modules", {"mailarium.bm25_index": mock_bm25_module}):
            result = r._get_bm25_results("test", 10)
            assert result == ["c1"]
            mock_bm25_instance.build_from_collection.assert_called_once()

    def test_returns_none_on_import_error(self):
        r = _bare_retriever()
        r._bm25_index = None
        r.collection = MagicMock()

        with patch.dict("sys.modules", {"mailarium.bm25_index": None}):
            result = r._get_bm25_results("test", 10)
            assert result is None

    def test_returns_none_on_generic_exception(self):
        r = _bare_retriever()
        mock_bm25 = MagicMock()
        mock_bm25.is_built = True
        mock_bm25.search.side_effect = RuntimeError("boom")
        r._bm25_index = mock_bm25

        result = r._get_bm25_results("test", 10)
        assert result is None

    def test_rebuilds_when_revision_changes_with_same_count(self):
        r = _bare_retriever()
        r.collection = MagicMock()
        r.collection.count.return_value = 50
        r.collection.metadata = {"index_revision": "rev-2"}
        mock_bm25 = MagicMock()
        mock_bm25.is_built = True
        mock_bm25.search.return_value = [("c1", 0.5)]
        mock_bm25._chunk_ids = ["c1"] * 50
        r._bm25_index = mock_bm25
        r._bm25_build_revision = (50, "rev-1")

        result = r._get_bm25_results("test", 10)
        assert result == ["c1"]
        mock_bm25.build_from_collection.assert_called_once_with(r.collection)
