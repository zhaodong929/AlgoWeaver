"""Small, dependency-free source ingestion service for the first vertical slice."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import zipfile
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Final, cast
from xml.etree import ElementTree as ET

from algo_weaver.schemas.ingestion import IngestedSource, IngestionBatch, SourceFormat

_EXTENSION_MAP: Final[dict[str, tuple[SourceFormat, str]]] = {
    ".txt": ("text", "text/plain"),
    ".md": ("markdown", "text/markdown"),
    ".markdown": ("markdown", "text/markdown"),
    ".py": ("python", "text/x-python"),
    ".csv": ("csv", "text/csv"),
    ".json": ("json", "application/json"),
    ".yaml": ("yaml", "application/yaml"),
    ".yml": ("yaml", "application/yaml"),
    ".pdf": ("pdf", "application/pdf"),
    ".docx": (
        "docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ),
    ".pptx": (
        "pptx",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ),
    ".xlsx": (
        "xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ),
}

_DOCLING_FORMATS: Final[frozenset[SourceFormat]] = frozenset({"pdf", "docx", "pptx", "xlsx"})


class SourceIngestor:
    """Read supported local sources while preserving a deterministic provenance record."""

    def ingest_path(
        self,
        path: str | Path,
        *,
        source_id: str | None = None,
        source_type: str = "unknown",
    ) -> IngestedSource:
        source_path = Path(path)
        if not source_path.exists():
            raise FileNotFoundError(f"source path does not exist: {source_path}")
        if not source_path.is_file():
            raise ValueError(f"source path is not a file: {source_path}")

        source_format, media_type = _EXTENSION_MAP.get(
            source_path.suffix.lower(), ("unknown", "application/octet-stream")
        )
        identifier = source_id or source_path.name
        raw = source_path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()

        if source_format == "unknown":
            return IngestedSource(
                source_id=identifier,
                path=str(source_path),
                source_type=source_type,
                source_format=source_format,
                media_type=media_type,
                content_sha256=digest,
                status="unsupported",
                error=(
                    f"unsupported extension '{source_path.suffix or '<none>'}'; "
                    "install a format-specific adapter in a later milestone"
                ),
            )

        if source_format in _DOCLING_FORMATS:
            try:
                content = _decode_with_docling(source_path)
            except ModuleNotFoundError:
                if source_format == "pdf":
                    try:
                        content = _decode_pdf_text(raw)
                    except ValueError:
                        content = ""
                    if content:
                        return _office_result(
                            identifier,
                            source_path,
                            source_format,
                            media_type,
                            digest,
                            content,
                            parser="stdlib-pdf-text",
                        )
                if source_format in {"docx", "pptx", "xlsx"}:
                    try:
                        content = _decode_with_stdlib_office(source_path, source_format)
                    except ModuleNotFoundError:
                        pass
                    except Exception as exc:
                        return _failed_office_result(
                            identifier, source_path, source_format, media_type, digest, exc
                        )
                    else:
                        return _office_result(
                            identifier,
                            source_path,
                            source_format,
                            media_type,
                            digest,
                            content,
                            parser="stdlib-office",
                        )
                return IngestedSource(
                    source_id=identifier,
                    path=str(source_path),
                    source_type=source_type,
                    source_format=source_format,
                    media_type=media_type,
                    content_sha256=digest,
                    status="unsupported",
                    error=(
                        f"{source_format} parsing requires the optional 'documents' extra "
                        "(Docling)"
                    ),
                )
            except Exception as exc:
                return IngestedSource(
                    source_id=identifier,
                    path=str(source_path),
                    source_type=source_type,
                    source_format=source_format,
                    media_type=media_type,
                    content_sha256=digest,
                    status="failed",
                    error=f"Docling failed to parse {source_path.name}: {exc}",
                )
            document_metadata: dict[str, str | int | bool] = {
                "file_name": source_path.name,
                "size_bytes": len(raw),
                "line_count": content.count("\n") + (1 if content else 0),
                "parser": "docling",
            }
            return IngestedSource(
                source_id=identifier,
                path=str(source_path),
                source_type=source_type,
                source_format=source_format,
                media_type=media_type,
                content=content,
                content_sha256=digest,
                metadata=document_metadata,
            )

        raw_text = raw.decode("utf-8-sig")
        content = _decode_content(raw, source_format)
        metadata: dict[str, str | int | bool] = {
            "file_name": source_path.name,
            "size_bytes": len(raw),
            "line_count": content.count("\n") + (1 if content else 0),
        }
        if source_format == "csv":
            metadata["row_count"] = _csv_row_count(raw_text)

        return IngestedSource(
            source_id=identifier,
            path=str(source_path),
            source_type=source_type,
            source_format=source_format,
            media_type=media_type,
            content=content,
            content_sha256=digest,
            metadata=metadata,
        )

    def ingest_paths(
        self,
        paths: Iterable[str | Path],
        *,
        source_ids: Mapping[str, str] | None = None,
        source_type: str = "unknown",
    ) -> IngestionBatch:
        """Ingest multiple paths while preserving per-source failures."""
        path_list = [Path(path) for path in paths]
        if not path_list:
            raise ValueError("paths cannot be empty")
        results: list[IngestedSource] = []
        for path in path_list:
            identifier = (source_ids or {}).get(str(path), path.name)
            try:
                results.append(
                    self.ingest_path(path, source_id=identifier, source_type=source_type)
                )
            except (FileNotFoundError, ValueError) as exc:
                source_format, media_type = _EXTENSION_MAP.get(
                    path.suffix.lower(), ("unknown", "application/octet-stream")
                )
                results.append(
                    IngestedSource(
                        source_id=identifier,
                        path=str(path),
                        source_type=source_type,
                        source_format=source_format,
                        media_type=media_type,
                        content_sha256=hashlib.sha256(b"").hexdigest(),
                        status="failed",
                        error=str(exc),
                    )
                )
        return IngestionBatch(sources=results)


def _decode_content(raw: bytes, source_format: SourceFormat) -> str:
    text = raw.decode("utf-8-sig")
    if source_format == "csv":
        return _csv_as_markdown(text)
    if source_format == "json":
        try:
            return json.dumps(json.loads(text), ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            return text
    return text


def _decode_with_docling(path: Path) -> str:
    """Convert an office/PDF source through Docling without importing it at startup."""
    from docling.document_converter import DocumentConverter

    result = DocumentConverter().convert(str(path))
    return cast(str, result.document.export_to_markdown())


def _decode_pdf_text(raw: bytes) -> str:
    """Extract simple literal text operators without claiming layout support."""
    text = raw.decode("latin-1", errors="ignore")
    blocks = re.findall(r"BT(.*?)ET", text, flags=re.DOTALL)
    values: list[str] = []
    for block in blocks:
        for match in re.finditer(r"\(((?:\\.|[^\\)])*)\)\s*Tj", block):
            value = match.group(1)
            value = re.sub(r"\\([\\()\\])", r"\1", value)
            value = value.replace(r"\n", "\n").replace(r"\r", "\r")
            if value.strip():
                values.append(value)
    if not values:
        raise ValueError("no literal PDF text operators found")
    return "\n".join(values)


def _decode_with_stdlib_office(path: Path, source_format: SourceFormat) -> str:
    """Extract basic text from OOXML files without importing an Office package."""
    if source_format not in {"docx", "pptx", "xlsx"}:
        raise ModuleNotFoundError("stdlib office fallback does not support this format")
    with zipfile.ZipFile(path) as archive:
        if source_format == "docx":
            return _docx_text(archive.read("word/document.xml"))
        if source_format == "pptx":
            slide_names = sorted(
                (name for name in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)),
                key=_slide_number,
            )
            return "\n".join(
                text
                for name in slide_names
                if (text := _xml_text(archive.read(name)))
            )
        return _xlsx_text(archive)


def _docx_text(raw: bytes) -> str:
    root = ET.fromstring(raw)
    paragraphs = []
    for paragraph in root.findall(".//{*}p"):
        text = "".join(node.text or "" for node in _local_nodes(paragraph, "t")).strip()
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs)


def _xml_text(raw: bytes) -> str:
    root = ET.fromstring(raw)
    return " ".join(node.text or "" for node in _local_nodes(root, "t")).strip()


def _slide_number(name: str) -> int:
    match = re.search(r"slide(\d+)", name)
    return int(match.group(1)) if match else 0


def _xlsx_text(archive: zipfile.ZipFile) -> str:
    shared: list[str] = []
    if "xl/sharedStrings.xml" in archive.namelist():
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        shared = [
            " ".join(node.text or "" for node in _local_nodes(item, "t"))
            for item in _local_nodes(root, "si")
        ]
    rows: list[str] = []
    sheet_names = sorted(name for name in archive.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", name))
    for name in sheet_names:
        root = ET.fromstring(archive.read(name))
        for row in _local_nodes(root, "row"):
            cells: list[str] = []
            for cell in _local_nodes(row, "c"):
                value = next((node.text or "" for node in _local_nodes(cell, "v")), "")
                if cell.get("t") == "s" and value.isdigit() and int(value) < len(shared):
                    value = shared[int(value)]
                cells.append(value)
            if cells:
                rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)


def _local_nodes(root: ET.Element, local_name: str) -> list[ET.Element]:
    return [
        node
        for node in root.iter()
        if isinstance(node.tag, str) and node.tag.rsplit("}", 1)[-1] == local_name
    ]


def _office_result(
    identifier: str,
    path: Path,
    source_format: SourceFormat,
    media_type: str,
    digest: str,
    content: str,
    *,
    parser: str,
) -> IngestedSource:
    return IngestedSource(
        source_id=identifier,
        path=str(path),
        source_type="document",
        source_format=source_format,
        media_type=media_type,
        content=content,
        content_sha256=digest,
        metadata={
            "file_name": path.name,
            "size_bytes": path.stat().st_size,
            "line_count": content.count("\n") + (1 if content else 0),
            "parser": parser,
        },
    )


def _failed_office_result(
    identifier: str,
    path: Path,
    source_format: SourceFormat,
    media_type: str,
    digest: str,
    error: Exception,
) -> IngestedSource:
    return IngestedSource(
        source_id=identifier,
        path=str(path),
        source_type="document",
        source_format=source_format,
        media_type=media_type,
        content_sha256=digest,
        status="failed",
        error=f"stdlib office fallback failed for {path.name}: {error}",
    )


def _csv_as_markdown(text: str) -> str:
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    normalized = [row + [""] * (width - len(row)) for row in rows]
    header = normalized[0]
    separator = ["---"] * width
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(separator) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in normalized[1:])
    return "\n".join(lines)


def _csv_row_count(text: str) -> int:
    return max(0, sum(1 for _ in csv.reader(io.StringIO(text))) - 1)
