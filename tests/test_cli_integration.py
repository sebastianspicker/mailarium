"""Integration tests for CLI analytics commands and dispatch logic."""

from __future__ import annotations

import sys
from argparse import Namespace
from io import StringIO
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

from mailarium.cli import (
    _run_entities,
    _run_export_network,
    _run_generate_report,
    _run_heatmap,
    _run_response_times,
    _run_suggest,
    _run_top_contacts,
    _run_volume,
    main,
)
from mailarium.cli_commands import _cmd_analytics

# ── Fixtures ─────────────────────────────────────────────────────────


class _FakeDB:
    """Minimal EmailDatabase stand-in for CLI analytics tests."""

    def top_contacts(self, email: str, limit: int = 20) -> list[dict]:
        return [
            {"partner": "bob@example.com", "total": 42},
            {"partner": "carol@example.com", "total": 10},
        ]

    def top_entities(self, entity_type: str | None = None, limit: int = 30) -> list[dict]:
        return [
            {"entity_text": "Acme Corp", "entity_type": "organization", "total_mentions": 15},
        ]

    def top_keywords(self, limit: int = 200) -> list[dict]:
        return [{"keyword": "invoice", "count": 5}]


class _FakeTemporalAnalyzer:
    """Minimal stand-in for TemporalAnalyzer."""

    def __init__(self, db):
        pass

    def volume_over_time(self, period: str = "day") -> list[dict]:
        return [{"period": "2024-01-01", "count": 10}]

    def activity_heatmap(self) -> list[dict]:
        return [{"hour": 9, "day_of_week": 1, "count": 5}]

    def response_times(self, limit: int = 20) -> list[dict]:
        return [{"replier": "employee@example.test", "avg_response_hours": 2.5, "response_count": 10}]


def _capture_stdout(func, *args, **kwargs) -> str:
    """Capture stdout from a function call."""
    old_stdout = sys.stdout
    sys.stdout = buffer = StringIO()
    try:
        func(*args, **kwargs)
    finally:
        sys.stdout = old_stdout
    return buffer.getvalue()


# ── _run_top_contacts ────────────────────────────────────────────────


def test_run_top_contacts_prints_partners():
    db = _FakeDB()
    output = _capture_stdout(_run_top_contacts, db, "employee@example.test")
    assert "bob@example.com" in output
    assert "carol@example.com" in output
    assert "42" in output


def test_run_top_contacts_no_contacts():
    db = MagicMock()
    db.top_contacts.return_value = []
    output = _capture_stdout(_run_top_contacts, db, "nobody@example.com")
    assert "No contacts found" in output


# ── _run_volume ──────────────────────────────────────────────────────


def test_run_volume_prints_bars():
    db = _FakeDB()
    with patch("mailarium.cli.TemporalAnalyzer", _FakeTemporalAnalyzer, create=True), patch.dict("sys.modules", {}):
        # We need to patch the import inside _run_volume
        import mailarium.cli as cli_mod

        original = cli_mod.__dict__.get("TemporalAnalyzer")
        try:
            # Patch the lazy import
            with patch(
                "mailarium.temporal_analysis.TemporalAnalyzer",
                _FakeTemporalAnalyzer,
            ):
                output = _capture_stdout(_run_volume, db, "day")
                assert "2024-01-01" in output
                assert "10" in output
        finally:
            if original:
                cli_mod.__dict__["TemporalAnalyzer"] = original


# ── _run_entities ────────────────────────────────────────────────────


def test_run_entities_prints_entities():
    db = _FakeDB()
    output = _capture_stdout(_run_entities, db, None)
    assert "Acme Corp" in output
    assert "organization" in output
    assert "15" in output


def test_run_entities_no_results():
    db = MagicMock()
    db.top_entities.return_value = []
    output = _capture_stdout(_run_entities, db, "phone")
    assert "No entities found" in output


# ── _run_heatmap ─────────────────────────────────────────────────────


def _run_heatmap_with_data(data: list[dict]) -> tuple[str, MagicMock]:
    analyzer = MagicMock()
    analyzer.activity_heatmap.return_value = data
    with patch("mailarium.temporal_analysis.TemporalAnalyzer", return_value=analyzer):
        output = _capture_stdout(_run_heatmap, _FakeDB())
    return output, analyzer


def test_run_heatmap_empty_data_prints_exact_line():
    output, analyzer = _run_heatmap_with_data([])

    assert output == "No heatmap data available.\n"
    analyzer.activity_heatmap.assert_called_once_with()


def test_run_heatmap_plain_fallback_has_full_24_by_7_snapshot(monkeypatch):
    monkeypatch.setitem(sys.modules, "rich.console", None)
    data = [
        {"hour": 0, "day_of_week": 0, "count": 8},
        {"hour": 0, "day_of_week": 0, "count": 2},
        {"hour": 0, "day_of_week": 1, "count": 8},
        {"hour": 0, "day_of_week": 2, "count": 6},
        {"hour": 0, "day_of_week": 3, "count": 4},
        {"hour": 0, "day_of_week": 4, "count": 2},
    ]

    output, analyzer = _run_heatmap_with_data(data)

    assert output.splitlines() == [
        "",
        "Activity heatmap (hour × day-of-week):",
        "",
        "      Mon   Tue   Wed   Thu   Fri   Sat   Sun",
        "  00  " + " ░  " + " █  " + " ▓  " + " ▒  " + " ░  " + "    " * 2,
        *[f"  {hour:02d}  " + "    " * 7 for hour in range(1, 24)],
        "",
        "  Legend: ' '=0  ░=low  ▒=mid  ▓=high  █=peak (max=8)",
    ]
    analyzer.activity_heatmap.assert_called_once_with()


def test_run_heatmap_rich_rendering_captures_panel_contract(monkeypatch):
    class FakePanel:
        def __init__(self, body, *, title, border_style):
            self.body = body
            self.title = title
            self.border_style = border_style

    captured: list[FakePanel] = []

    class FakeConsole:
        def print(self, panel):
            captured.append(panel)

    console_module = ModuleType("rich.console")
    console_module.Console = FakeConsole
    panel_module = ModuleType("rich.panel")
    panel_module.Panel = FakePanel
    monkeypatch.setitem(sys.modules, "rich.console", console_module)
    monkeypatch.setitem(sys.modules, "rich.panel", panel_module)

    output, analyzer = _run_heatmap_with_data(
        [
            {"hour": 9, "day_of_week": 0, "count": 0},
            {"hour": 9, "day_of_week": 1, "count": 1},
            {"hour": 9, "day_of_week": 2, "count": 2},
            {"hour": 9, "day_of_week": 3, "count": 3},
            {"hour": 9, "day_of_week": 4, "count": 4},
        ]
    )
    panel = captured[0]
    empty_cell = " [dim] [/dim]  "
    low_cell = " [blue]░[/blue]  "
    mid_cell = " [cyan]▒[/cyan]  "
    high_cell = " [yellow]▓[/yellow]  "
    peak_cell = " [green bold]█[/green bold]  "
    expected_rows = [f"  [dim]{hour:02d}[/]   " + empty_cell * 7 for hour in range(24)]
    expected_rows[9] = f"  [dim]09[/]   {empty_cell}{low_cell}{mid_cell}{high_cell}{peak_cell}{empty_cell * 2}"
    expected_body = "\n".join(
        [
            "       [bold]Mon[/]   [bold]Tue[/]   [bold]Wed[/]   [bold]Thu[/]   [bold]Fri[/]   [bold]Sat[/]   [bold]Sun[/]",
            *expected_rows,
            "",
            "  [dim]' '=none  [blue]░[/]=low  [cyan]▒[/]=mid  [yellow]▓[/]=high  [green bold]█[/]=peak (max=4)[/]",
        ]
    )

    assert output == ""
    assert panel.title == "[bold]Activity Heatmap (hour x day-of-week)[/]"
    assert panel.border_style == "blue"
    assert panel.body == expected_body
    analyzer.activity_heatmap.assert_called_once_with()


def test_run_heatmap_duplicate_cell_uses_last_count_and_global_max(monkeypatch):
    monkeypatch.setitem(sys.modules, "rich.console", None)
    output, analyzer = _run_heatmap_with_data(
        [
            {"hour": 9, "day_of_week": 1, "count": 10},
            {"hour": 9, "day_of_week": 1, "count": 3},
        ]
    )

    assert output.splitlines()[13] == "  09  " + "    " + " ░  " + "    " * 5
    assert "max=10" in output
    analyzer.activity_heatmap.assert_called_once_with()


def test_run_heatmap_all_zero_counts_use_blank_cells_without_division(monkeypatch):
    monkeypatch.setitem(sys.modules, "rich.console", None)
    output, analyzer = _run_heatmap_with_data([{"hour": 9, "day_of_week": 1, "count": 0}])

    assert output.splitlines()[13] == "  09  " + "    " * 7
    assert output.endswith("█=peak (max=0)\n")
    analyzer.activity_heatmap.assert_called_once_with()


def test_run_heatmap_only_falls_back_for_import_errors():
    data = [{"hour": 9, "day_of_week": 1, "count": 5}]

    with (
        patch(
            "mailarium.cli_commands_analytics._render_rich_heatmap",
            side_effect=ImportError("Rich unavailable"),
        ) as render_rich,
        patch("mailarium.cli_commands_analytics._render_plain_heatmap") as render_plain,
    ):
        output, analyzer = _run_heatmap_with_data(data)

    assert output == ""
    render_rich.assert_called_once_with({(9, 1): 5}, 5)
    render_plain.assert_called_once_with({(9, 1): 5}, 5)
    analyzer.activity_heatmap.assert_called_once_with()

    with (
        patch(
            "mailarium.cli_commands_analytics._render_rich_heatmap",
            side_effect=RuntimeError("render failed"),
        ),
        patch("mailarium.cli_commands_analytics._render_plain_heatmap") as render_plain,
        pytest.raises(RuntimeError, match="render failed"),
    ):
        _run_heatmap_with_data(data)

    render_plain.assert_not_called()


def test_run_heatmap_constructs_analyzer_before_rendering(monkeypatch):
    db = _FakeDB()
    data = [{"hour": 9, "day_of_week": 1, "count": 5}]
    events: list[object] = []

    class OrderedAnalyzer:
        def __init__(self, received_db):
            events.append(("construct", received_db))

        def activity_heatmap(self):
            events.append("analyze")
            return data

    def record_render(grid, max_count):
        events.append(("render", grid, max_count))

    monkeypatch.setattr("mailarium.temporal_analysis.TemporalAnalyzer", OrderedAnalyzer)
    monkeypatch.setattr("mailarium.cli_commands_analytics._render_rich_heatmap", record_render)

    assert _capture_stdout(_run_heatmap, db) == ""
    assert events == [
        ("construct", db),
        "analyze",
        ("render", {(9, 1): 5}, 5),
    ]


# ── _run_response_times ──────────────────────────────────────────────


def test_run_response_times_prints_times():
    db = _FakeDB()
    with patch("mailarium.temporal_analysis.TemporalAnalyzer", _FakeTemporalAnalyzer):
        output = _capture_stdout(_run_response_times, db)
        assert "employee@example.test" in output
        assert "2.5" in output


# ── _run_suggest ─────────────────────────────────────────────────────


def test_run_suggest_prints_suggestions():
    fake_db = _FakeDB()
    fake_suggester = MagicMock()
    fake_suggester.suggest_flat.return_value = ["recent invoices", "security review"]

    with patch("mailarium.cli_commands._get_email_db", return_value=fake_db):
        with patch("mailarium.query_suggestions.QuerySuggester", return_value=fake_suggester):
            output = _capture_stdout(_run_suggest)
            assert "recent invoices" in output
            assert "security review" in output


def test_run_suggest_no_suggestions():
    fake_db = _FakeDB()
    fake_suggester = MagicMock()
    fake_suggester.suggest_flat.return_value = []

    with patch("mailarium.cli_commands._get_email_db", return_value=fake_db):
        with patch("mailarium.query_suggestions.QuerySuggester", return_value=fake_suggester):
            output = _capture_stdout(_run_suggest)
            assert "No suggestions available" in output


# ── _run_generate_report ─────────────────────────────────────────────


def test_run_generate_report_calls_generator():
    fake_db = _FakeDB()
    mock_generator = MagicMock()

    with patch("mailarium.cli_commands._get_email_db", return_value=fake_db):
        with patch("mailarium.report_generator.ReportGenerator", return_value=mock_generator):
            output = _capture_stdout(_run_generate_report, "report.html")
            assert "report.html" in output
            mock_generator.generate.assert_called_once_with(output_path="report.html")


def test_run_generate_report_surfaces_degraded_warnings():
    fake_db = _FakeDB()
    mock_generator = MagicMock()
    mock_generator.last_warnings = ["monthly_volume unavailable: RuntimeError"]

    with patch("mailarium.cli_commands._get_email_db", return_value=fake_db):
        with patch("mailarium.report_generator.ReportGenerator", return_value=mock_generator):
            output = _capture_stdout(_run_generate_report, "report.html")
            assert "Report generated with warnings: report.html" in output
            assert "monthly_volume unavailable: RuntimeError" in output


def test_run_generate_report_exits_on_render_error(capsys):
    fake_db = _FakeDB()
    from mailarium.report_generator import ReportGenerationError

    mock_generator = MagicMock()
    mock_generator.generate.side_effect = ReportGenerationError(
        "Jinja2 is required for report generation. Run: pip install jinja2"
    )

    with patch("mailarium.cli_commands._get_email_db", return_value=fake_db):
        with patch("mailarium.report_generator.ReportGenerator", return_value=mock_generator):
            with pytest.raises(SystemExit) as exc:
                _run_generate_report("report.html")

    assert exc.value.code == 1
    assert "Error: Jinja2 is required for report generation. Run: pip install jinja2" in capsys.readouterr().out


# ── _run_export_network ──────────────────────────────────────────────


def test_run_export_network_success():
    fake_db = _FakeDB()
    mock_network = MagicMock()
    mock_network.export_graphml.return_value = {
        "output_path": "network.graphml",
        "total_nodes": 10,
        "total_edges": 25,
    }

    with patch("mailarium.cli_commands._get_email_db", return_value=fake_db):
        with patch("mailarium.network_analysis.CommunicationNetwork", return_value=mock_network):
            output = _capture_stdout(_run_export_network, "network.graphml")
            assert "network.graphml" in output
            assert "Nodes: 10" in output
            assert "Edges: 25" in output


def test_run_export_network_error():
    fake_db = _FakeDB()
    mock_network = MagicMock()
    mock_network.export_graphml.return_value = {"error": "No data"}

    with patch("mailarium.cli_commands._get_email_db", return_value=fake_db):
        with patch("mailarium.network_analysis.CommunicationNetwork", return_value=mock_network):
            with pytest.raises(SystemExit) as exc_info:
                _run_export_network("network.graphml")
            assert exc_info.value.code == 1


def test_main_threads_sqlite_override_into_retriever(tmp_path) -> None:
    with (
        patch("mailarium.retriever.EmailRetriever") as mock_retriever,
        patch("mailarium.cli._cmd_search", side_effect=lambda _args, get_retriever: get_retriever()) as mock_search,
        patch("mailarium.cli.set_cli_sqlite_path_override") as mock_set_sqlite,
    ):
        main(
            [
                "search",
                "budget",
                "--vector-index-path",
                str(tmp_path / "vector-index"),
                "--sqlite-path",
                str(tmp_path / "email.db"),
            ]
        )

    mock_retriever.assert_called_once_with(
        vector_index_path=str(tmp_path / "vector-index"),
        sqlite_path=str(tmp_path / "email.db"),
        sparse_enabled=None,
        image_search_enabled=None,
    )
    mock_set_sqlite.assert_called_once_with(str(tmp_path / "email.db"))
    mock_search.assert_called_once()


def test_main_browse_does_not_construct_retriever() -> None:
    with patch("mailarium.retriever.EmailRetriever") as mock_retriever, patch("mailarium.cli._cmd_browse") as mock_browse:
        main(["browse"])

    mock_retriever.assert_not_called()
    mock_browse.assert_called_once()


def test_cmd_analytics_contacts_avoids_retriever_startup() -> None:
    args = Namespace(analytics_action="contacts", email_address="employee@example.test")

    with (
        patch("mailarium.cli_commands._get_email_db", return_value=object()),
        patch("mailarium.cli_commands._run_top_contacts") as mock_run,
        pytest.raises(SystemExit) as exc,
    ):
        _cmd_analytics(args, lambda: (_ for _ in ()).throw(AssertionError("retriever should stay lazy")))

    assert exc.value.code == 0
    mock_run.assert_called_once()
