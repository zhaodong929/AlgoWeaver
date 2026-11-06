"""Small, dependency-free source ingestion service for the first vertical slice."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Final

from algo_weaver.schemas.ingestion import IngestedSource, SourceFormat

_EXTENSION_MAP: Final[dict[str, tuple[SourceFormat, str]]] = {
    ".txt": ("text", "text/plain"),
    ".md": ("markdown", "text/markdown"),
    ".markdown": ("markdown", "text/markdown"),
    ".py": ("python", "text/x-python"),
    ".csv": ("csv", "text/csv"),
    ".json": ("json", "application/json"),
    ".yaml": ("yaml", "application/yaml"),
    ".yml": ("yaml", "application/yaml"),
}


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
