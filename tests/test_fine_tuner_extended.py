"""Synchronous SentenceTransformers trainer orchestration tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

import pytest

from mailarium.fine_tuner import FineTuner


class _FakeTrainingState:
    records: dict[str, object]

    @classmethod
    def record(cls, event: str) -> None:
        cls.records["events"].append(event)


class _FakeDataset:
    @classmethod
    def from_dict(cls, columns):
        _FakeTrainingState.record("dataset")
        _FakeTrainingState.records["columns"] = columns
        return {"dataset": columns}


class _DenseArguments:
    def __init__(self, **kwargs):
        _FakeTrainingState.record("dense-arguments")
        _FakeTrainingState.records["arguments"] = kwargs


class _SparseArguments:
    def __init__(self, **kwargs):
        _FakeTrainingState.record("sparse-arguments")
        _FakeTrainingState.records["arguments"] = kwargs


class _DenseModel:
    def __init__(self, base_model, **kwargs):
        _FakeTrainingState.record("dense-model")
        assert base_model == "BAAI/bge-m3"
        assert kwargs == {"device": _FakeTrainingState.records["device"], "trust_remote_code": False}

    def __setattr__(self, name, value):
        if name == "max_seq_length":
            _FakeTrainingState.record("max-sequence-length")
        super().__setattr__(name, value)

    def save_pretrained(self, destination, **kwargs):
        _FakeTrainingState.record("dense-save")
        assert self.trained_with is _FakeTrainingState.records["loss"]
        _FakeTrainingState.records["save"] = (destination, kwargs)


class _SparseModel:
    def __init__(self, base_model, **kwargs):
        _FakeTrainingState.record("sparse-model")
        assert base_model == "opensearch-project/opensearch-neural-sparse-encoding-multilingual-v1"
        assert kwargs == {"device": _FakeTrainingState.records["device"], "trust_remote_code": False}

    def __setattr__(self, name, value):
        if name == "max_seq_length":
            _FakeTrainingState.record("sparse-max-sequence-length")
        super().__setattr__(name, value)

    def save_pretrained(self, destination, **kwargs):
        _FakeTrainingState.record("sparse-save")
        assert self.trained_with is _FakeTrainingState.records["loss"]
        _FakeTrainingState.records["save"] = (destination, kwargs)


class _DenseLoss:
    def __init__(self, *, model):
        _FakeTrainingState.record("dense-loss")
        assert isinstance(model, _DenseModel)
        _FakeTrainingState.records["loss"] = self


class _SparseLoss:
    def __init__(self, *, model):
        _FakeTrainingState.record("sparse-loss")
        assert isinstance(model, _SparseModel)
        _FakeTrainingState.records["loss"] = self


class _DenseTrainer:
    def __init__(self, **kwargs):
        _FakeTrainingState.record("dense-trainer")
        assert isinstance(kwargs["model"], _DenseModel)
        assert isinstance(kwargs["args"], _DenseArguments)
        assert isinstance(kwargs["loss"], _DenseLoss)
        self.model = kwargs["model"]
        self.loss = kwargs["loss"]

    def train(self):
        _FakeTrainingState.record("dense-train")
        self.model.trained_with = self.loss
        return SimpleNamespace(metrics={"loss": 0.25, "epoch": 2, "ignored": "text"})


class _SparseTrainer:
    def __init__(self, **kwargs):
        _FakeTrainingState.record("sparse-trainer")
        assert isinstance(kwargs["model"], _SparseModel)
        assert isinstance(kwargs["args"], _SparseArguments)
        assert isinstance(kwargs["loss"], _SparseLoss)
        self.model = kwargs["model"]
        self.loss = kwargs["loss"]

    def train(self):
        _FakeTrainingState.record("sparse-train")
        self.model.trained_with = self.loss
        return SimpleNamespace(metrics={"loss": 0.25, "epoch": 2, "ignored": "text"})


def _install_fake_training_dependencies(monkeypatch, records: dict[str, object]) -> None:
    _FakeTrainingState.records = records
    datasets = ModuleType("datasets")
    datasets.Dataset = _FakeDataset
    sentence_transformers = ModuleType("sentence_transformers")
    sentence_transformers.SentenceTransformer = _DenseModel
    sentence_transformers.SentenceTransformerTrainer = _DenseTrainer
    sentence_transformers.SentenceTransformerTrainingArguments = _DenseArguments
    sentence_transformers.SparseEncoder = _SparseModel
    sentence_transformers.SparseEncoderTrainer = _SparseTrainer
    sentence_transformers.SparseEncoderTrainingArguments = _SparseArguments
    sentence_transformers.losses = SimpleNamespace(TripletLoss=_DenseLoss)
    sparse_encoder = ModuleType("sentence_transformers.sparse_encoder")
    sparse_encoder.losses = SimpleNamespace(SparseTripletLoss=_SparseLoss)
    monkeypatch.setitem(sys.modules, "datasets", datasets)
    monkeypatch.setitem(sys.modules, "sentence_transformers", sentence_transformers)
    monkeypatch.setitem(sys.modules, "sentence_transformers.sparse_encoder", sparse_encoder)


def _triplets(path: Path) -> None:
    path.write_text(json.dumps({"query": "q", "pos": "p", "neg": "n"}) + "\n", encoding="utf-8")


def test_dense_training_writes_config_manifest_and_completed_status(tmp_path):
    data, output = tmp_path / "triplets.jsonl", tmp_path / "model"
    _triplets(data)
    trainer = FineTuner(device="cpu")
    with patch.object(trainer, "_train_dense", return_value={"loss": 0.25}) as train:
        result = trainer.fine_tune(str(data), str(output), epochs=2)
    assert result["status"] == "completed"
    assert result["mode"] == "dense"
    assert train.call_count == 1
    manifest = json.loads((output / "training_manifest.json").read_text(encoding="utf-8"))
    assert manifest["metrics"] == {"loss": 0.25}
    assert manifest["training_data_sha256"]


def test_sparse_mode_selects_sparse_trainer(tmp_path):
    data, output = tmp_path / "triplets.jsonl", tmp_path / "model"
    _triplets(data)
    trainer = FineTuner(device="cpu")
    with patch.object(trainer, "_train_sparse", return_value={"loss": 0.5}) as train:
        result = trainer.fine_tune(str(data), str(output), mode="sparse")
    assert result["mode"] == "sparse"
    train.assert_called_once()


@pytest.mark.parametrize(
    ("mode", "device", "expected_events"),
    [
        (
            "dense",
            "cuda",
            [
                "dense-model",
                "max-sequence-length",
                "dataset",
                "dense-loss",
                "dense-arguments",
                "dense-trainer",
                "dense-train",
                "dense-save",
            ],
        ),
        (
            "sparse",
            "cpu",
            [
                "sparse-model",
                "dataset",
                "sparse-loss",
                "sparse-arguments",
                "sparse-trainer",
                "sparse-train",
                "sparse-save",
            ],
        ),
        (
            "sparse",
            "cuda",
            [
                "sparse-model",
                "dataset",
                "sparse-loss",
                "sparse-arguments",
                "sparse-trainer",
                "sparse-train",
                "sparse-save",
            ],
        ),
    ],
)
def test_training_modes_share_orchestration_and_preserve_mode_specific_setup(
    monkeypatch,
    tmp_path,
    mode,
    device,
    expected_events,
):
    records: dict[str, object] = {"device": device, "events": []}
    _install_fake_training_dependencies(monkeypatch, records)

    output = tmp_path / mode
    config = {
        "epochs": 2,
        "batch_size": 3,
        "gradient_accumulation": 4,
        "learning_rate": 1e-5,
        "warmup_ratio": 0.1,
        "max_len": 23,
    }
    tuner = FineTuner(device=device)
    metrics = getattr(tuner, f"_train_{mode}")([{"query": "q", "pos": "p", "neg": "n"}], output, config)

    assert records["events"] == expected_events
    assert "sparse-max-sequence-length" not in records["events"]
    assert records["columns"] == {"anchor": ["q"], "positive": ["p"], "negative": ["n"]}
    assert records["arguments"] == {
        "output_dir": str(output / "checkpoints"),
        "num_train_epochs": 2.0,
        "per_device_train_batch_size": 3,
        "gradient_accumulation_steps": 4,
        "learning_rate": 1e-5,
        "warmup_ratio": 0.1,
        "fp16": device == "cuda",
        "report_to": [],
        "save_strategy": "no",
    }
    assert records["save"] == (str(output / "model"), {"safe_serialization": True})
    assert metrics == {"loss": 0.25, "epoch": 2.0}


@pytest.mark.parametrize("mode", ["invalid", "", None])
def test_invalid_training_mode_is_rejected(tmp_path, mode):
    with pytest.raises(ValueError):
        FineTuner(device="cpu").fine_tune(str(tmp_path / "missing"), str(tmp_path / "out"), mode=mode)
