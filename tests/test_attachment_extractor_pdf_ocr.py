"""Focused tests for rendered-page PDF OCR extraction."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import mailarium.attachment_extractor as extractor


def test_pdf_render_uses_bounded_page_arguments(monkeypatch, tmp_path: Path) -> None:
    rendered_dir = tmp_path / "rendered"
    rendered_dir.mkdir()
    temp_pdf = tmp_path / "source.pdf"
    run_process = MagicMock(return_value=subprocess.CompletedProcess([], 0))

    monkeypatch.setenv("ATTACHMENT_PDF_OCR_MAX_PAGES", "99")
    monkeypatch.setattr(extractor, "pdf_ocr_available", lambda: True)
    monkeypatch.setattr(extractor.tempfile, "mkdtemp", lambda prefix: str(rendered_dir))
    monkeypatch.setattr(extractor, "_write_temporary_attachment", lambda content, suffix: str(temp_pdf))
    monkeypatch.setattr(extractor.shutil, "which", lambda executable: f"/tools/{executable}")
    monkeypatch.setattr(extractor, "_run_ocr_process", run_process)

    assert extractor.extract_pdf_text_ocr("scan.pdf", b"pdf") is None
    run_process.assert_called_once_with(
        [
            "/tools/pdftoppm",
            "-f",
            "1",
            "-l",
            "50",
            "-png",
            str(temp_pdf),
            str(rendered_dir / "page"),
        ],
        timeout_seconds=90,
    )


def test_rendered_pages_use_lexical_order_and_omit_empty_text(monkeypatch, tmp_path: Path) -> None:
    for page_name in ("page-2.png", "page-10.png", "page-1.png"):
        (tmp_path / page_name).write_bytes(page_name.encode())
    page_order: list[str] = []

    def extract_page(filename: str, content: bytes, *, timeout_seconds: int) -> str | None:
        page_order.append(filename)
        return {"page-1.png": "first", "page-10.png": "", "page-2.png": "second"}[filename]

    monkeypatch.setattr(extractor, "extract_image_text_ocr", extract_page)

    assert extractor._extract_rendered_pdf_page_text(str(tmp_path), timeout_seconds=90) == "first\n\nsecond"
    assert page_order == ["page-1.png", "page-10.png", "page-2.png"]


def test_rendered_page_text_is_joined_and_globally_truncated(monkeypatch, tmp_path: Path) -> None:
    (tmp_path / "page-1.png").write_bytes(b"one")
    (tmp_path / "page-2.png").write_bytes(b"two")
    monkeypatch.setattr(extractor, "extract_image_text_ocr", lambda *args, **kwargs: "x" * 30_000)

    result = extractor._extract_rendered_pdf_page_text(str(tmp_path), timeout_seconds=90)

    assert result is not None
    assert result.endswith("[... content truncated ...]")
    assert len(result) < 60_002


def test_pdf_render_nonzero_return_code_fails_without_image_ocr(monkeypatch, tmp_path: Path) -> None:
    rendered_dir = tmp_path / "rendered"
    rendered_dir.mkdir()
    image_ocr = MagicMock()

    monkeypatch.setattr(extractor, "pdf_ocr_available", lambda: True)
    monkeypatch.setattr(extractor.tempfile, "mkdtemp", lambda prefix: str(rendered_dir))
    monkeypatch.setattr(extractor, "_write_temporary_attachment", lambda content, suffix: str(tmp_path / "source.pdf"))
    monkeypatch.setattr(extractor.shutil, "which", lambda executable: f"/tools/{executable}")
    monkeypatch.setattr(extractor, "_run_ocr_process", lambda *args, **kwargs: subprocess.CompletedProcess([], 1))
    monkeypatch.setattr(extractor, "_extract_rendered_pdf_page_text", image_ocr)

    assert extractor.extract_pdf_text_ocr("scan.pdf", b"pdf") is None
    image_ocr.assert_not_called()


def test_pdf_ocr_cleans_up_temporary_pdf_and_render_directory(monkeypatch, tmp_path: Path) -> None:
    temp_pdf = str(tmp_path / "source.pdf")
    rendered_dir = str(tmp_path / "rendered")
    safe_unlink = MagicMock()
    remove_tree = MagicMock()

    monkeypatch.setattr(extractor, "pdf_ocr_available", lambda: True)
    monkeypatch.setattr(extractor.tempfile, "mkdtemp", lambda prefix: rendered_dir)
    monkeypatch.setattr(extractor, "_write_temporary_attachment", lambda content, suffix: temp_pdf)
    monkeypatch.setattr(extractor.shutil, "which", lambda executable: f"/tools/{executable}")
    monkeypatch.setattr(extractor, "_run_ocr_process", lambda *args, **kwargs: subprocess.CompletedProcess([], 1))
    monkeypatch.setattr(extractor, "_safe_unlink", safe_unlink)
    monkeypatch.setattr(extractor.shutil, "rmtree", remove_tree)

    assert extractor.extract_pdf_text_ocr("scan.pdf", b"pdf") is None
    safe_unlink.assert_called_once_with(temp_pdf, message="Failed to unlink temp PDF")
    remove_tree.assert_called_once_with(rendered_dir, ignore_errors=True)
