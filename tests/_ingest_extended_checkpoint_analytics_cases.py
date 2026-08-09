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
