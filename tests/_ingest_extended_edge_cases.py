"""Compatibility exports for extended ingestion edge-case tests."""

from ._ingest_extended_cli_edge_cases import TestMainDispatch, TestParseArgsEdgeCases, TestPositiveInt
from ._ingest_extended_facade_option_cases import TestIngestEdgeCases
from ._ingest_extended_reingest_edge_cases import (
    TestReembedEdgeCases,
    TestReingestAnalyticsEdgeCases,
    TestReingestBodiesEdgeCases,
    TestReingestMetadataEdgeCases,
)
from ._ingest_extended_summary_cases import TestFormatSummaryEdgeCases

__all__ = [
    "TestFormatSummaryEdgeCases",
    "TestIngestEdgeCases",
    "TestMainDispatch",
    "TestParseArgsEdgeCases",
    "TestPositiveInt",
    "TestReembedEdgeCases",
    "TestReingestAnalyticsEdgeCases",
    "TestReingestBodiesEdgeCases",
    "TestReingestMetadataEdgeCases",
]
