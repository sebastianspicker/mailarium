"""Ingestion summary formatting edge cases."""

from mailarium.ingest import format_ingestion_summary


class TestFormatSummaryEdgeCases:
    def test_includes_sqlite_inserted(self):
        lines = format_ingestion_summary(
            {
                "emails_parsed": 10,
                "chunks_created": 20,
                "chunks_added": 18,
                "chunks_skipped": 2,
                "batches_written": 3,
                "total_in_db": 99,
                "sqlite_inserted": 10,
                "dry_run": False,
                "elapsed_seconds": 1.5,
            }
        )
        assert any("SQLite rows inserted: 10" in line for line in lines)

    def test_includes_skipped_incremental(self):
        lines = format_ingestion_summary(
            {
                "emails_parsed": 10,
                "chunks_created": 20,
                "chunks_added": 18,
                "chunks_skipped": 2,
                "batches_written": 3,
                "total_in_db": 99,
                "sqlite_inserted": 5,
                "skipped_incremental": 5,
                "dry_run": False,
                "elapsed_seconds": 1.5,
            }
        )
        assert any("Skipped (incremental): 5" in line for line in lines)

    def test_no_timing_info(self):
        lines = format_ingestion_summary({"emails_parsed": 10, "chunks_created": 20, "dry_run": True, "elapsed_seconds": 1.0})
        assert not any("Timing:" in line for line in lines)
