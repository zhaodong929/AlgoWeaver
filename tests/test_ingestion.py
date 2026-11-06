from pathlib import Path

import pytest

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
