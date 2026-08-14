"""WAL checkpoint and analytics pipeline tests."""

from unittest.mock import MagicMock

from mailarium.ingest import _EmbedPipeline

from .helpers.ingest_extended_fixtures import _make_email


class TestCheckpointWal:
    def test_checkpoint_wal_success(self):
        mock_db = MagicMock()
        pipeline = _EmbedPipeline(embedder=None, email_db=mock_db, entity_extractor_fn=None, batch_size=100)
        pipeline._checkpoint_wal()
        mock_db.conn.execute.assert_called_with("PRAGMA wal_checkpoint(PASSIVE)")

    def test_checkpoint_wal_failure_is_non_critical(self):
        mock_db = MagicMock()
        mock_db.conn.execute.side_effect = Exception("WAL error")
        pipeline = _EmbedPipeline(embedder=None, email_db=mock_db, entity_extractor_fn=None, batch_size=100)
        pipeline._checkpoint_wal()

    def test_checkpoint_wal_no_db(self):
        pipeline = _EmbedPipeline(embedder=None, email_db=None, entity_extractor_fn=None, batch_size=100)
        pipeline._checkpoint_wal()


class TestComputeAnalytics:
    def test_skips_when_no_email_db(self):
        pipeline = _EmbedPipeline(embedder=None, email_db=None, entity_extractor_fn=None, batch_size=100)
        pipeline._compute_analytics([_make_email(1)])

    def test_short_body_is_recorded_with_low_confidence_metadata(self):
        mock_db = MagicMock()
        pipeline = _EmbedPipeline(embedder=None, email_db=mock_db, entity_extractor_fn=None, batch_size=100)
        email = _make_email(1, body_text="zur Prüfung")
        pipeline._compute_analytics([email])
        mock_db.update_analytics_batch.assert_called_once()
        rows = mock_db.update_analytics_batch.call_args.args[0]
        assert len(rows) == 1
        assert rows[0][0] == "de"
        assert rows[0][1] == "low"
        assert rows[0][2] == "short_text_stopword_vote"
        assert rows[0][3] == "body_text"

    def test_prefers_forensic_text_for_analytics(self):
        mock_db = MagicMock()
        pipeline = _EmbedPipeline(embedder=None, email_db=mock_db, entity_extractor_fn=None, batch_size=100)
        email = _make_email(1, body_text="ok")
        email.forensic_body_text = "zur Prüfung"
        email.forensic_body_source = "raw_body_text"
        pipeline._compute_analytics([email])
        rows = mock_db.update_analytics_batch.call_args.args[0]
        assert rows[0][0] == "de"
        assert rows[0][1] == "low"
        assert rows[0][3] == "raw_body_text"

    def test_analytics_writers_receive_commit_false(self):
        mock_db = MagicMock()
        pipeline = _EmbedPipeline(embedder=None, email_db=mock_db, entity_extractor_fn=None, batch_size=100)
        email = _make_email(1)
        email.segments = [{"segment_type": "authored_body", "text": email.body_text, "source_surface": "body_text", "ordinal": 0}]

        pipeline._compute_analytics([email], commit=False)

        assert mock_db.update_analytics_batch.call_args.kwargs == {"commit": False}
        assert mock_db.upsert_language_surface_analytics.call_args.kwargs == {"commit": False}

    def test_default_analytics_writers_receive_commit_true_in_order(self):
        class RecordingWriter:
            def __init__(self, name, call_log):
                self.name = name
                self.call_log = call_log

            def __call__(self, rows, *, commit=True):
                self.call_log.append((self.name, rows, commit))

        class RecordingDb:
            def __init__(self):
                self.call_log = []
                self.update_analytics_batch = RecordingWriter("analytics", self.call_log)
                self.upsert_language_surface_analytics = RecordingWriter("surface", self.call_log)

        recording_db = RecordingDb()
        pipeline = _EmbedPipeline(embedder=None, email_db=recording_db, entity_extractor_fn=None, batch_size=100)
        email = _make_email(1)
        email.segments = [{"segment_type": "authored_body", "text": email.body_text, "source_surface": "body_text", "ordinal": 0}]

        pipeline._compute_analytics([email])

        assert [name for name, _rows, _commit in recording_db.call_log] == ["analytics", "surface"]
        assert [commit for _name, _rows, commit in recording_db.call_log] == [True, True]
        assert all(rows for _name, rows, _commit in recording_db.call_log)

    def test_legacy_analytics_writers_retry_once_with_equivalent_rows(self):
        class LegacyWriter:
            def __init__(self, name, call_log):
                self.name = name
                self.call_log = call_log
                self.calls = []

            def __call__(self, rows, **kwargs):
                self.calls.append((rows, kwargs))
                self.call_log.append(self.name)
                if kwargs:
                    raise TypeError("legacy writer got an unexpected keyword argument 'commit'")

        class LegacyDb:
            def __init__(self):
                self.call_log = []
                self.update_analytics_batch = LegacyWriter("analytics", self.call_log)
                self.upsert_language_surface_analytics = LegacyWriter("surface", self.call_log)

        legacy_db = LegacyDb()
        pipeline = _EmbedPipeline(embedder=None, email_db=legacy_db, entity_extractor_fn=None, batch_size=100)
        email = _make_email(1)
        email.segments = [{"segment_type": "authored_body", "text": email.body_text, "source_surface": "body_text", "ordinal": 0}]

        pipeline._compute_analytics([email], commit=False)

        assert legacy_db.call_log == ["analytics", "analytics", "surface", "surface"]
        for writer in (legacy_db.update_analytics_batch, legacy_db.upsert_language_surface_analytics):
            assert [kwargs for _rows, kwargs in writer.calls] == [{"commit": False}, {}]
            assert writer.calls[0][0] is writer.calls[1][0]
            assert writer.calls[0][0] == writer.calls[1][0]

    def test_unrelated_analytics_writer_type_error_propagates_without_retry(self):
        mock_db = MagicMock()
        mock_db.update_analytics_batch.side_effect = TypeError("analytics row must contain eight fields")
        pipeline = _EmbedPipeline(embedder=None, email_db=mock_db, entity_extractor_fn=None, batch_size=100)

        try:
            pipeline._compute_analytics([_make_email(1)], commit=False)
        except TypeError as exc:
            assert str(exc) == "analytics row must contain eight fields"
        else:
            raise AssertionError("Expected the unrelated TypeError to propagate")

        mock_db.update_analytics_batch.assert_called_once()
        assert mock_db.update_analytics_batch.call_args.kwargs == {"commit": False}
