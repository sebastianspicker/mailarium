"""CLI dispatch and argument-validation ingestion edge cases."""

import argparse

import pytest

from mailarium.ingest import main, parse_args


class TestMainDispatch:
    def test_main_reset_index_without_yes(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["data/file.olm", "--reset-index"])
        assert exc.value.code == 2
        out = capsys.readouterr().out
        assert "Refusing" in out

    def test_main_reset_index_with_yes(self, tmp_path, monkeypatch, capsys):
        import mailarium.ingest as ingest_mod

        monkeypatch.setattr(ingest_mod, "_reset_index", lambda args: None)
        with pytest.raises(SystemExit) as exc:
            main(["data/file.olm", "--reset-index", "--yes"])
        assert exc.value.code == 0
        out = capsys.readouterr().out
        assert "reset" in out.lower()

    def test_main_reingest_bodies(self, monkeypatch, capsys):
        import mailarium.ingest as ingest_mod

        monkeypatch.setattr(
            ingest_mod,
            "reingest_bodies",
            lambda olm_path, sqlite_path=None, force=False: {"message": "Bodies updated"},
        )
        with pytest.raises(SystemExit) as exc:
            main(["data/file.olm", "--reingest-bodies"])
        assert exc.value.code == 0
        assert "Bodies updated" in capsys.readouterr().out

    def test_main_reingest_metadata(self, monkeypatch, capsys):
        import mailarium.ingest as ingest_mod

        monkeypatch.setattr(
            ingest_mod,
            "reingest_metadata",
            lambda olm_path, sqlite_path=None: {"message": "Metadata updated"},
        )
        with pytest.raises(SystemExit) as exc:
            main(["data/file.olm", "--reingest-metadata"])
        assert exc.value.code == 0
        assert "Metadata updated" in capsys.readouterr().out

    def test_main_reingest_analytics(self, monkeypatch, capsys):
        import mailarium.ingest as ingest_mod

        monkeypatch.setattr(
            ingest_mod,
            "reingest_analytics",
            lambda sqlite_path=None: {"message": "Analytics computed"},
        )
        with pytest.raises(SystemExit) as exc:
            main(["--reingest-analytics"])
        assert exc.value.code == 0
        assert "Analytics computed" in capsys.readouterr().out

    def test_main_reembed(self, monkeypatch, capsys):
        import mailarium.ingest as ingest_mod

        monkeypatch.setattr(
            ingest_mod,
            "reembed",
            lambda vector_index_path=None, sqlite_path=None, batch_size=100: {"message": "Reembedded"},
        )
        with pytest.raises(SystemExit) as exc:
            main(["--reembed"])
        assert exc.value.code == 0
        assert "Reembedded" in capsys.readouterr().out

    def test_main_requires_olm_for_reingest_bodies(self):
        with pytest.raises(SystemExit) as exc:
            main(["--reingest-bodies"])

        assert exc.value.code == 2

    def test_main_runtime_error(self, monkeypatch, capsys):
        import mailarium.ingest as ingest_mod

        monkeypatch.setattr(
            ingest_mod,
            "ingest",
            lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("test runtime error")),
        )
        with pytest.raises(SystemExit) as exc:
            main(["data/file.olm", "--dry-run"])
        assert exc.value.code == 2
        out = capsys.readouterr().out
        assert "test runtime error" in out


class TestParseArgsEdgeCases:
    def test_all_flags(self, tmp_path):
        args = parse_args(
            [
                "data/file.olm",
                "--vector-index-path",
                str(tmp_path / "vector-index"),
                "--batch-size",
                "100",
                "--max-emails",
                "50",
                "--dry-run",
                "--extract-attachments",
                "--embed-images",
                "--extract-entities",
                "--sqlite-path",
                str(tmp_path / "test.db"),
                "--incremental",
                "--reset-index",
                "--reingest-bodies",
                "--reingest-metadata",
                "--reembed",
                "--reingest-analytics",
                "--force",
                "--timing",
                "--resume",
                "--yes",
                "--log-level",
                "DEBUG",
            ]
        )
        assert args.olm_path == "data/file.olm"
        assert args.vector_index_path == str(tmp_path / "vector-index")
        assert args.batch_size == 100
        assert args.max_emails == 50
        assert args.dry_run is True
        assert args.extract_attachments is True
        assert args.embed_images is True
        assert args.extract_entities is True
        assert args.sqlite_path == str(tmp_path / "test.db")
        assert args.incremental is True
        assert args.reset_index is True
        assert args.reingest_bodies is True
        assert args.reingest_metadata is True
        assert args.reembed is True
        assert args.reingest_analytics is True
        assert args.force is True
        assert args.timing is True
        assert args.resume is True
        assert args.yes is True
        assert args.log_level == "DEBUG"

    def test_positive_int_error(self):
        with pytest.raises(SystemExit):
            parse_args(["data/file.olm", "--batch-size", "-1"])

    def test_reingest_analytics_does_not_require_olm_path(self):
        args = parse_args(["--reingest-analytics"])
        assert args.olm_path is None
        assert args.reingest_analytics is True

    def test_reembed_does_not_require_olm_path(self):
        args = parse_args(["--reembed"])
        assert args.olm_path is None
        assert args.reembed is True

    def test_reextract_entities_does_not_require_olm_path(self):
        args = parse_args(["--reextract-entities"])
        assert args.olm_path is None
        assert args.reextract_entities is True

    def test_default_ingest_still_requires_olm_path(self):
        with pytest.raises(SystemExit):
            parse_args([])

    def test_reingest_bodies_still_requires_olm_path(self):
        with pytest.raises(SystemExit):
            parse_args(["--reingest-bodies"])


class TestPositiveInt:
    def test_valid(self):
        from mailarium.ingest import _positive_int

        assert _positive_int("5") == 5

    def test_invalid_raises_argparse_type_error(self):
        from mailarium.ingest import _positive_int

        with pytest.raises(argparse.ArgumentTypeError):
            _positive_int("0")

    def test_negative_raises_argparse_type_error(self):
        from mailarium.ingest import _positive_int

        with pytest.raises(argparse.ArgumentTypeError):
            _positive_int("-1")
