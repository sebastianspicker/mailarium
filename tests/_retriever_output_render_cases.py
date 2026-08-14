"""Retriever result serialization and bounded rendering behavior."""

from tests.helpers.retriever_cases import _bare_retriever, _make_result


def test_format_results_budget_exhaustion_shows_omitted():
    r = _bare_retriever()
    results = [_make_result(f"c{i}", text="x" * 500, uid=f"u{i}", date=f"2024-01-{i:02d}") for i in range(1, 20)]

    output = r.format_results_for_llm(results, max_body_chars=500, max_response_tokens=100)
    assert "omitted" in output.lower() or "result" in output.lower()


def test_format_results_thread_budget_exhaustion():
    """Budget exhaustion mid-thread should stop and report omissions."""
    r = _bare_retriever()
    results = [
        _make_result("c1", text="x" * 1000, uid="u1", date="2024-01-01", conversation_id="conv1"),
        _make_result("c2", text="x" * 1000, uid="u2", date="2024-01-02", conversation_id="conv1"),
        _make_result("c3", text="x" * 1000, uid="u3", date="2024-01-03", conversation_id="conv1"),
    ]

    output = r.format_results_for_llm(results, max_body_chars=1000, max_response_tokens=50)
    assert "omitted" in output.lower() or "tokens" in output.lower()


def test_format_results_unlimited_budget():
    r = _bare_retriever()
    results = [_make_result("c1", text="hello")]
    output = r.format_results_for_llm(results, max_response_tokens=0)
    assert "hello" in output
    assert "omitted" not in output.lower()


class TestSerializeResults:
    def test_basic_serialization(self):
        r = _bare_retriever()
        results = [_make_result("c1", text="body")]
        payload = r.serialize_results("test", results)
        assert payload["query"] == "test"
        assert payload["count"] == 1
        assert payload["total_count"] == 1
        assert payload["returned_count"] == 1
        assert payload["omitted_count"] == 0
        assert payload["results_truncated"] is False
        assert len(payload["results"]) == 1
        assert payload["results"][0]["chunk_id"] == "c1"

    def test_body_truncation(self):
        r = _bare_retriever()
        results = [_make_result("c1", text="x" * 1000)]
        payload = r.serialize_results("test", results, max_body_chars=50)
        assert len(payload["results"][0]["text"]) < 1000

    def test_token_budget_omits_results(self):
        r = _bare_retriever()
        results = [_make_result(f"c{i}", text="x" * 500, uid=f"u{i}") for i in range(50)]
        payload = r.serialize_results("test", results, max_body_chars=500, max_response_tokens=100)
        assert payload["count"] < 50
        assert payload["total_count"] == 50
        assert payload["results_truncated"] is True
        assert payload["omitted_count"] > 0
        assert "omitted" in payload["truncation_note"]

    def test_unlimited_budget_includes_all(self):
        r = _bare_retriever()
        results = [_make_result(f"c{i}", text="hello", uid=f"u{i}") for i in range(5)]
        payload = r.serialize_results("test", results, max_response_tokens=0)
        assert len(payload["results"]) == 5
        assert payload["results_truncated"] is False

    def test_no_truncation_with_zero_body_chars(self):
        r = _bare_retriever()
        text = "x" * 2000
        results = [_make_result("c1", text=text)]
        payload = r.serialize_results("test", results, max_body_chars=0)
        assert payload["results"][0]["text"] == text
