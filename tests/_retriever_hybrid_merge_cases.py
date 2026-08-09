"""Retriever sparse-and-semantic result fusion behavior."""

import types
from unittest.mock import MagicMock, patch

from tests.helpers.retriever_cases import _bare_retriever, _make_result


class TestMergeHybrid:
    def test_merge_hybrid_no_keyword_results_returns_semantic(self):
        r = _bare_retriever()
        r._get_sparse_results = MagicMock(return_value=None)
        r._get_bm25_results = MagicMock(return_value=None)
        semantic = [_make_result("c1")]
        result = r._merge_hybrid("test", semantic, 10)
        assert result is semantic

    def test_merge_hybrid_empty_keyword_results_returns_semantic(self):
        r = _bare_retriever()
        r._get_sparse_results = MagicMock(return_value=None)
        r._get_bm25_results = MagicMock(return_value=[])
        semantic = [_make_result("c1")]
        result = r._merge_hybrid("test", semantic, 10)
        assert result is semantic

    def test_merge_hybrid_fuses_sparse_and_semantic(self):
        r = _bare_retriever()
        r._get_sparse_results = MagicMock(return_value=["c1", "c3"])
        r.collection = MagicMock()
        r.collection.get.return_value = {
            "ids": ["c3"],
            "documents": ["keyword doc"],
            "metadatas": [{"uid": "u3"}],
        }

        semantic = [_make_result("c1", uid="u1"), _make_result("c2", uid="u2")]
        mock_bm25 = types.ModuleType("mailarium.bm25_index")

        def rrf(semantic_ids, keyword_ids, k=60, **_weights):
            merged = []
            seen = set()
            for chunk_id in keyword_ids + semantic_ids:
                if chunk_id not in seen:
                    merged.append(chunk_id)
                    seen.add(chunk_id)
            return merged

        mock_bm25.reciprocal_rank_fusion = rrf
        with patch.dict("sys.modules", {"mailarium.bm25_index": mock_bm25}):
            result = r._merge_hybrid("test", semantic, 10)
            chunk_ids = [result.chunk_id for result in result]
            assert "c1" in chunk_ids
            assert "c3" in chunk_ids
            keyword_only = next(result for result in result if result.chunk_id == "c3")
            assert keyword_only.metadata["score_kind"] == "keyword_fused"
            assert keyword_only.metadata["score_calibration"] == "synthetic"

    def test_merge_hybrid_import_error_returns_semantic(self):
        r = _bare_retriever()
        r._get_sparse_results = MagicMock(return_value=["c99"])

        with patch.dict("sys.modules", {"mailarium.bm25_index": None}):
            semantic = [_make_result("c1")]
            result = r._merge_hybrid("test", semantic, 10)
            assert result is semantic

    def test_merge_hybrid_failure_does_not_claim_fusion(self):
        r = _bare_retriever()
        r._last_search_debug = {}
        r._get_sparse_results = MagicMock(return_value=["c1"])
        semantic = [_make_result("c1")]

        with patch("mailarium.retriever_hybrid._merged_hybrid_results", side_effect=RuntimeError("fusion failed")):
            result = r._merge_hybrid("test", semantic, 10)

        assert result is semantic
        assert "fusion" not in r._last_search_debug

    def test_merge_hybrid_generic_exception_returns_semantic(self):
        r = _bare_retriever()
        r._get_sparse_results = MagicMock(side_effect=RuntimeError("boom"))
        semantic = [_make_result("c1")]
        result = r._merge_hybrid("test", semantic, 10)
        assert result is semantic

    def test_merge_hybrid_collection_get_failure_handled(self):
        """If collection.get fails for missing IDs, merge still works."""
        r = _bare_retriever()
        r._get_sparse_results = MagicMock(return_value=["c1", "c_missing"])
        r.collection = MagicMock()
        r.collection.get.side_effect = RuntimeError("db error")

        semantic = [_make_result("c1", uid="u1")]
        mock_bm25 = types.ModuleType("mailarium.bm25_index")
        mock_bm25.reciprocal_rank_fusion = lambda semantic_ids, keyword_ids, **_kwargs: (
            keyword_ids + [chunk_id for chunk_id in semantic_ids if chunk_id not in keyword_ids]
        )
        with patch.dict("sys.modules", {"mailarium.bm25_index": mock_bm25}):
            result = r._merge_hybrid("test", semantic, 10)
            assert any(item.chunk_id == "c1" for item in result)
