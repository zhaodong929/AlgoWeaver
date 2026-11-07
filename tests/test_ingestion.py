import zipfile
from pathlib import Path

import pytest

import algo_weaver.services.ingestion as ingestion
from algo_weaver.services.ingestion import SourceIngestor


def test_ingestor_preserves_markdown_provenance(tmp_path: Path) -> None:
    source = tmp_path / "algorithm.md"
    source.write_text("# Moving Average\nSmooth a time series.", encoding="utf-8")

    result = SourceIngestor().ingest_path(source, source_id="doc-001", source_type="document")

    assert result.status == "ingested"
    assert result.source_format == "markdown"
    assert result.content.startswith("# Moving Average")
    assert len(result.content_sha256) == 64
    assert result.metadata["line_count"] == 2


def test_ingestor_normalizes_csv_for_extraction(tmp_path: Path) -> None:
    source = tmp_path / "metrics.csv"
    source.write_text("metric,value\naccuracy,0.9\n", encoding="utf-8")

    result = SourceIngestor().ingest_path(source)

    assert "| metric | value |" in result.content
    assert "| accuracy | 0.9 |" in result.content
    assert result.metadata["row_count"] == 1


def test_ingestor_reports_unsupported_formats_without_reading_as_text(tmp_path: Path) -> None:
    source = tmp_path / "archive.bin"
    source.write_bytes(b"opaque")

    result = SourceIngestor().ingest_path(source)

    assert result.status == "unsupported"
    assert result.content == ""
    assert result.error and "unsupported extension" in result.error


def test_ingestor_rejects_missing_paths(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        SourceIngestor().ingest_path(tmp_path / "missing.md")


def test_office_formats_use_optional_docling_adapter(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "report.pdf"
    source.write_bytes(b"%PDF-placeholder")
    monkeypatch.setattr(ingestion, "_decode_with_docling", lambda _: "# Parsed report")

    result = SourceIngestor().ingest_path(source, source_type="document")

    assert result.status == "ingested"
    assert result.content == "# Parsed report"
    assert result.metadata["parser"] == "docling"


def test_office_formats_report_missing_optional_dependency(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "report.docx"
    source.write_bytes(b"docx-placeholder")

    def missing_docling(_):
        raise ModuleNotFoundError("docling")

    monkeypatch.setattr(ingestion, "_decode_with_docling", missing_docling)
    monkeypatch.setattr(
        ingestion,
        "_decode_with_stdlib_office",
        lambda *_: (_ for _ in ()).throw(ModuleNotFoundError("docling")),
    )
    result = SourceIngestor().ingest_path(source)

    assert result.status == "unsupported"
    assert result.error and "optional 'documents' extra" in result.error


def _zip_file(path: Path, name: str, content: str) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(name, content)


def test_docx_stdlib_fallback_extracts_paragraphs(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "report.docx"
    _zip_file(
        source,
        "word/document.xml",
        '<document xmlns:w="urn"><body><w:p><w:r><w:t>Inventory plan</w:t></w:r></w:p></body></document>',
    )
    monkeypatch.setattr(ingestion, "_decode_with_docling", lambda _: (_ for _ in ()).throw(ModuleNotFoundError()))

    result = SourceIngestor().ingest_path(source)

    assert result.status == "ingested"
    assert result.content == "Inventory plan"
    assert result.metadata["parser"] == "stdlib-office"


def test_xlsx_stdlib_fallback_extracts_shared_strings(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "metrics.xlsx"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr(
            "xl/sharedStrings.xml",
            '<sst xmlns="urn"><si><t>metric</t></si><si><t>accuracy</t></si></sst>',
        )
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            '<worksheet xmlns="urn"><sheetData><row><c t="s"><v>0</v></c></row><row><c t="s"><v>1</v></c></row></sheetData></worksheet>',
        )
    monkeypatch.setattr(ingestion, "_decode_with_docling", lambda _: (_ for _ in ()).throw(ModuleNotFoundError()))

    result = SourceIngestor().ingest_path(source)

    assert result.status == "ingested"
    assert "metric" in result.content
    assert "accuracy" in result.content


def test_pptx_stdlib_fallback_extracts_slide_text(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "slides.pptx"
    _zip_file(
        source,
        "ppt/slides/slide1.xml",
        '<p:sld xmlns:p="urnp" xmlns:a="urn"><a:t>Forecast result</a:t></p:sld>',
    )
    monkeypatch.setattr(ingestion, "_decode_with_docling", lambda _: (_ for _ in ()).throw(ModuleNotFoundError()))

    result = SourceIngestor().ingest_path(source)

    assert result.status == "ingested"
    assert result.content == "Forecast result"
    assert result.metadata["parser"] == "stdlib-office"


def test_pdf_stdlib_fallback_extracts_basic_literal_text(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "report.pdf"
    source.write_bytes(b"%PDF-1.4\nBT\n(Inventory forecast) Tj\nET\n%%EOF")
    monkeypatch.setattr(
        ingestion,
        "_decode_with_docling",
        lambda _: (_ for _ in ()).throw(ModuleNotFoundError()),
    )

    result = SourceIngestor().ingest_path(source)

    assert result.status == "ingested"
    assert result.content == "Inventory forecast"
    assert result.metadata["parser"] == "stdlib-pdf-text"
