"""Retriever sparse-index result behavior."""

import types
from unittest.mock import MagicMock, patch

from tests.helpers.retriever_cases import _bare_retriever, _configured_sparse_retriever


class TestGetSparseResults:
    def test_returns_none_when_embedder_has_no_sparse(self):
        r = _bare_retriever()
        mock_embedder = MagicMock()
        mock_embedder.has_sparse = False
        r._embedder = mock_embedder
        assert r._get_sparse_results("test", 10) is None

    def test_returns_none_when_no_email_db(self):
        r = _bare_retriever()
        mock_embedder = MagicMock()
        mock_embedder.has_sparse = True
        r._embedder = mock_embedder
        r._email_db = None
        r._email_db_checked = True
        assert r._get_sparse_results("test", 10) is None

    def test_returns_none_when_sparse_index_not_built(self):
        r = _bare_retriever()
        mock_embedder = MagicMock()
        mock_embedder.has_sparse = True
        r._embedder = mock_embedder
        r._email_db = MagicMock()
        r._email_db_checked = True

        mock_sparse = MagicMock()
        mock_sparse.is_built = False
        mock_sparse.doc_count = 0

        mock_sparse_module = types.ModuleType("mailarium.sparse_index")
        mock_sparse_module.SparseIndex = MagicMock(return_value=mock_sparse)
        with patch.dict("sys.modules", {"mailarium.sparse_index": mock_sparse_module}):
            r._sparse_index = None
            result = r._get_sparse_results("test", 10)
            assert result is None

    def test_returns_none_when_empty_query_sparse(self):
        r = _bare_retriever()
        mock_embedder = MagicMock()
        mock_embedder.has_sparse = True
        mock_embedder.encode_sparse_query.return_value = [{}]
        r._embedder = mock_embedder
        r._email_db = MagicMock()
        r._email_db_checked = True

        mock_sparse = MagicMock()
        mock_sparse.is_built = True
        mock_sparse.doc_count = 100
        r._sparse_index = mock_sparse

        result = r._get_sparse_results("test", 10)
        assert result is None

    def test_returns_chunk_ids_on_success(self):
        r, mock_sparse, _ = _configured_sparse_retriever({1: 0.5, 2: 0.3})
        mock_sparse.search.return_value = [("c1", 0.9), ("c2", 0.8)]

        result = r._get_sparse_results("test", 10)
        assert result == ["c1", "c2"]

    def test_returns_none_on_exception(self):
        r = _bare_retriever()
        mock_embedder = MagicMock()
        mock_embedder.has_sparse = True
        mock_embedder.encode_sparse_query.side_effect = RuntimeError("boom")
        r._embedder = mock_embedder
        r._email_db = MagicMock()
        r._email_db_checked = True
        r.collection = MagicMock()
        r.collection.count.return_value = 10
        r.collection.metadata = {"index_revision": "rev-1"}
        r._sparse_index = MagicMock()
        r._sparse_index.is_built = True
        r._sparse_index.doc_count = 10

        result = r._get_sparse_results("test", 10)
        assert result is None

    def test_partial_sparse_coverage_still_returns_sparse_results(self):
        r, mock_sparse, _ = _configured_sparse_retriever({1: 0.9}, sparse_doc_count=80)
        mock_sparse.search.return_value = [("c5", 0.7)]
        r._set_last_search_debug({})

        assert r._get_sparse_results("test", 10) == ["c5"]
        assert r.last_search_debug["sparse_diagnostics"]["coverage"]["status"] == "partial"

    def test_sparse_rebuilds_when_revision_changes_with_same_count(self):
        r = _bare_retriever()
        r.settings = MagicMock(sparse_model="test-sparse", sparse_model_revision="test-revision")
        mock_embedder = MagicMock()
        mock_embedder.has_sparse = True
        mock_embedder.encode_sparse_query.return_value = [{1: 0.5}]
        r._embedder = mock_embedder
        r._email_db = MagicMock()
        r._email_db_checked = True
        r.collection = MagicMock()
        r.collection.count.return_value = 100
        r.collection.metadata = {"index_revision": "rev-2"}

        mock_sparse = MagicMock()
        mock_sparse.is_built = True
        mock_sparse.doc_count = 100
        mock_sparse.search.return_value = [("c1", 0.9)]
        r._sparse_index = mock_sparse
        r._sparse_build_count = (100, "rev-1")

        result = r._get_sparse_results("test", 10)
        assert result == ["c1"]
        mock_sparse.build_from_db.assert_called_once_with(
            r._email_db,
            model_id="test-sparse",
            model_revision="test-revision",
        )  # pylint: disable=no-member
