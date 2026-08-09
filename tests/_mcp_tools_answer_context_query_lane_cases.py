"""Answer-context query-lane public and runtime cases."""

import pytest

from .helpers.answer_context_fakes import _run_answer_context_json
from .helpers.mcp_tool_fakes import _BasicRetriever, _make_result


class _LaneMergeRetriever(_BasicRetriever):
    def search_filtered(self, query, top_k=10, **kwargs):
        self._last_search_debug = {  # pylint: disable=attribute-defined-outside-init
            "executed_query": query,
            "used_query_expansion": False,
            "expand_query_requested": False,
            "use_hybrid": False,
            "use_rerank": False,
            "top_k": top_k,
            "fetch_size": top_k,
        }
        if "Protokoll" in query:
            return [
                _make_result(
                    uid="uid-wave-1",
                    chunk_id="chunk-wave-1",
                    text="PR-Sitzung mit Protokoll.",
                    distance=0.1,
                )
            ]
        return [
            _make_result(
                uid="uid-wave-2",
                chunk_id="chunk-wave-2",
                text="Mobiles Arbeiten wurde gestrichen.",
                distance=0.12,
            )
        ]


class _LaneMergeDB:
    conn = None

    def get_emails_full_batch(self, uids):
        return {
            "uid-wave-1": {
                "uid": "uid-wave-1",
                "body_text": "PR-Sitzung mit Protokoll.",
                "normalized_body_source": "body_text",
            },
            "uid-wave-2": {
                "uid": "uid-wave-2",
                "body_text": "Mobiles Arbeiten wurde gestrichen.",
                "normalized_body_source": "body_text",
            },
        }


@pytest.mark.asyncio
async def test_email_answer_context_merges_query_lanes(monkeypatch):
    from mailarium.mcp_models import EmailAnswerContextInput

    data = await _run_answer_context_json(
        monkeypatch,
        retriever=_LaneMergeRetriever(),
        db=_LaneMergeDB(),
        params=EmailAnswerContextInput(
            question="Welche Widersprüche gibt es?",
            max_results=2,
            query_lanes=["17.12.2024 Protokoll PR-Sitzung", "mobiles Arbeiten spontanes Streichen"],
        ),
    )

    assert data["count"] == 2
    assert data["search"]["retrieval_diagnostics"]["query_lane_count"] == 2
    assert len(data["search"]["retrieval_diagnostics"]["query_lanes"]) == 2


def test_search_across_query_lanes_preserves_unique_lane_hits_with_scan_state() -> None:
    from mailarium.tools.search_answer_context_runtime_search import _search_across_query_lanes

    class DummyRetriever(_BasicRetriever):
        def search_filtered(self, query, top_k=10, **kwargs):
            self._last_search_debug = {  # pylint: disable=attribute-defined-outside-init
                "executed_query": query,
                "used_query_expansion": False,
            }
            if query == "lane one":
                return [
                    _make_result(uid="uid-shared", chunk_id="chunk-shared", text="shared", distance=0.05),
                    _make_result(uid="uid-lane-one", chunk_id="chunk-lane-one", text="lane one", distance=0.06),
                ]
            return [
                _make_result(uid="uid-shared", chunk_id="chunk-shared-second", text="shared", distance=0.04),
                _make_result(uid="uid-lane-two", chunk_id="chunk-lane-two", text="lane two", distance=0.07),
            ]

    retriever = DummyRetriever()
    results, diagnostics, search_meta = _search_across_query_lanes(
        retriever=retriever,
        search_kwargs={"hybrid": True},
        query_lanes=["lane one", "lane two"],
        top_k=2,
        lane_top_k=4,
        reserve_per_lane=1,
        scan_id="wave:test",
    )

    uids = [result.metadata.get("uid") for result in results]
    assert "uid-shared" in uids
    assert "uid-lane-two" in uids
    assert len(results) == 2
    assert diagnostics[0]["scan_id"] == "wave:test"
    assert diagnostics[0]["search_top_k"] == 4
    assert diagnostics[1]["excluded_count"] >= 1
    assert search_meta["candidate_pool_count"] >= 2
    assert search_meta["lane_top_k"] == 4
    assert search_meta["selected_result_count"] == 2
    assert any(item["uid"] == "uid-lane-two" for item in search_meta["evidence_bank"])
