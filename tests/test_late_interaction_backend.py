"""Verifies the local late-interaction backend bounds resource use and follows its offline protocol."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from mailarium.late_interaction_backend import LateInteractionError, LocalLateInteractionBackend
from mailarium.retriever_models import SearchResult


def _result(identifier: str) -> SearchResult:
    return SearchResult(chunk_id=identifier, text=identifier, metadata={}, distance=0.5)


def _artifact(tmp_path: Path) -> tuple[Path, Path]:
    runner = tmp_path / "runner"
    runner.write_text("runner", encoding="utf-8")
    model = tmp_path / "model"
    model.mkdir()
    payload = model / "artifact.bin"
    payload.write_bytes(b"artifact")
    (model / "late-interaction-manifest.json").write_text(
        json.dumps(
            {
                "version": 1,
                "model_id": "local",
                "artifact": payload.name,
                "sha256": hashlib.sha256(b"artifact").hexdigest(),
            }
        ),
        encoding="utf-8",
    )
    return runner, model


def _executable_runner(tmp_path: Path, source: str) -> Path:
    runner = tmp_path / "executable-runner"
    runner.write_text(f"#!{sys.executable}\n{source}\n", encoding="utf-8")
    runner.chmod(0o700)
    return runner


def test_local_runner_reorders_by_returned_score(tmp_path):
    runner, model = _artifact(tmp_path)
    output = json.dumps({"version": 1, "scores": {"a": 0.1, "b": 0.9}})
    with patch("mailarium.late_interaction_backend._run_bounded_runner", return_value=(0, output)) as run:
        results = LocalLateInteractionBackend(str(runner), str(model)).rerank("q", [_result("a"), _result("b")], top_k=1)
    assert [item.chunk_id for item in results] == ["b"]
    assert results[0].metadata["reranker"] == "late_interaction_local"
    assert results[0].metadata["score_kind"] == "late_interaction"
    assert results[0].distance == pytest.approx(0.1)
    assert run.call_args.args[0] == runner.resolve()


def test_local_runner_rejects_response_ids_not_requested(tmp_path):
    runner, model = _artifact(tmp_path)
    output = json.dumps({"version": 1, "scores": {"other": 1.0}})
    with patch("mailarium.late_interaction_backend._run_bounded_runner", return_value=(0, output)):
        with pytest.raises(LateInteractionError, match="IDs do not match"):
            LocalLateInteractionBackend(str(runner), str(model)).rerank("q", [_result("a")], top_k=1)


@pytest.mark.parametrize(
    ("output", "message"),
    [
        ("not-json", "returned invalid JSON"),
        (json.dumps([]), "unsupported protocol version"),
        (json.dumps({"version": 2, "scores": {"a": 0.0}}), "unsupported protocol version"),
        (json.dumps({"version": 1, "scores": [0.0]}), "must contain a scores object"),
        (json.dumps({"version": 1, "scores": {}}), "IDs do not match"),
        (json.dumps({"version": 1, "scores": {"a": 0.0, "extra": 0.1}}), "IDs do not match"),
        (json.dumps({"version": 1, "scores": {"a": "not-a-score"}}), "invalid score for 'a'"),
        (json.dumps({"version": 1, "scores": {"a": -1.01}}), "out-of-range score for 'a'"),
        (json.dumps({"version": 1, "scores": {"a": 1.01}}), "out-of-range score for 'a'"),
    ],
)
def test_local_runner_rejects_invalid_score_protocol_responses(tmp_path, output, message):
    runner, model = _artifact(tmp_path)
    with patch("mailarium.late_interaction_backend._run_bounded_runner", return_value=(0, output)):
        with pytest.raises(LateInteractionError, match=message):
            LocalLateInteractionBackend(str(runner), str(model)).rerank("q", [_result("a")], top_k=1)


@pytest.mark.parametrize("score", [-1.0, 1.0])
def test_local_runner_accepts_score_range_boundaries(tmp_path, score):
    runner, model = _artifact(tmp_path)
    output = json.dumps({"version": 1, "scores": {"a": score}})
    with patch("mailarium.late_interaction_backend._run_bounded_runner", return_value=(0, output)):
        results = LocalLateInteractionBackend(str(runner), str(model)).rerank("q", [_result("a")], top_k=1)

    assert results[0].distance == 1.0 - score


def test_local_runner_preserves_input_order_for_equal_scores(tmp_path):
    runner, model = _artifact(tmp_path)
    output = json.dumps({"version": 1, "scores": {"a": 0.5, "b": 0.5}})
    with patch("mailarium.late_interaction_backend._run_bounded_runner", return_value=(0, output)):
        results = LocalLateInteractionBackend(str(runner), str(model)).rerank("q", [_result("a"), _result("b")], top_k=2)

    assert [result.chunk_id for result in results] == ["a", "b"]


def test_local_runner_coerces_legacy_boolean_scores(tmp_path):
    runner, model = _artifact(tmp_path)
    output = json.dumps({"version": 1, "scores": {"a": True, "b": False}})
    with patch("mailarium.late_interaction_backend._run_bounded_runner", return_value=(0, output)):
        results = LocalLateInteractionBackend(str(runner), str(model)).rerank("q", [_result("a"), _result("b")], top_k=2)

    assert [result.chunk_id for result in results] == ["a", "b"]
    assert [result.distance for result in results] == [0.0, 1.0]


def test_local_runner_rejects_oversized_response_before_json_parsing(tmp_path, monkeypatch):
    runner, model = _artifact(tmp_path)
    output = "not-json" + "x" * 10_000
    monkeypatch.setattr("mailarium.late_interaction_backend._MAX_PAYLOAD_CHARS", 10_000)
    with patch("mailarium.late_interaction_backend._run_bounded_runner", return_value=(0, output)):
        with pytest.raises(LateInteractionError) as exc_info:
            LocalLateInteractionBackend(str(runner), str(model)).rerank("q", [_result("a")], top_k=1)

    assert str(exc_info.value) == "late-interaction response exceeds the configured safety limit"


def test_executable_local_runner_completes_protocol_round_trip(tmp_path):
    _runner, model = _artifact(tmp_path)
    runner = _executable_runner(
        tmp_path,
        "import json, sys\n"
        "payload = json.load(sys.stdin)\n"
        "scores = {item['chunk_id']: 0.75 for item in payload['documents']}\n"
        "print(json.dumps({'version': 1, 'scores': scores}))",
    )

    results = LocalLateInteractionBackend(str(runner), str(model)).rerank("query", [_result("a")], top_k=1)

    assert [result.chunk_id for result in results] == ["a"]


def test_local_runner_stops_oversized_stdout(tmp_path, monkeypatch):
    _runner, model = _artifact(tmp_path)
    runner = _executable_runner(tmp_path, "import sys\nsys.stdout.write('x' * 2048)")
    monkeypatch.setattr("mailarium.late_interaction_backend._MAX_RESPONSE_BYTES", 1024)

    with pytest.raises(LateInteractionError, match="stdout exceeds"):
        LocalLateInteractionBackend(str(runner), str(model)).rerank("private query", [_result("a")], top_k=1)


def test_local_runner_stops_oversized_stderr_without_disclosure(tmp_path, monkeypatch):
    _runner, model = _artifact(tmp_path)
    marker = "private-mailbox-content"
    runner = _executable_runner(tmp_path, f"import sys\nsys.stderr.write({marker!r} * 100)")
    monkeypatch.setattr("mailarium.late_interaction_backend._MAX_STDERR_BYTES", 128)

    with pytest.raises(LateInteractionError, match="stderr exceeds") as exc_info:
        LocalLateInteractionBackend(str(runner), str(model)).rerank("private query", [_result("a")], top_k=1)

    assert marker not in str(exc_info.value)


def test_local_runner_timeout_stops_child(tmp_path):
    _runner, model = _artifact(tmp_path)
    runner = _executable_runner(tmp_path, "import time\ntime.sleep(1)")

    with pytest.raises(subprocess.TimeoutExpired):
        LocalLateInteractionBackend(str(runner), str(model), timeout_seconds=0.1).rerank("private query", [_result("a")], top_k=1)


def test_local_runner_redacts_sensitive_stderr_on_failure(tmp_path):
    _runner, model = _artifact(tmp_path)
    marker = "private-mailbox-content"
    runner = _executable_runner(tmp_path, f"import sys\nsys.stderr.write({marker!r})\nraise SystemExit(7)")

    with pytest.raises(LateInteractionError, match="exited with 7") as exc_info:
        LocalLateInteractionBackend(str(runner), str(model)).rerank("private query", [_result("a")], top_k=1)

    assert marker not in str(exc_info.value)
