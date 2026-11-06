"""SQLite capability registry with verified-only promotion."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from algo_weaver.schemas.capability import AlgorithmCapability
from algo_weaver.schemas.registry import CapabilityVersion
from algo_weaver.schemas.validation import ValidationReport


class CapabilityRegistry:
    """Persist capability snapshots without requiring a database server."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        if str(self.database_path) != ":memory:":
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def save(self, capability: AlgorithmCapability) -> CapabilityVersion:
        """Append a new immutable version for a capability."""
        payload = capability.model_dump(mode="json")
        created_at = datetime.now(UTC)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COALESCE(MAX(version), 0) FROM capabilities WHERE capability_id = ?",
                (capability.capability_id,),
            ).fetchone()
            version = int(row[0]) + 1
            connection.execute(
                """
                INSERT INTO capabilities
                    (capability_id, version, status, name, created_at, payload_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    capability.capability_id,
                    version,
                    capability.status,
                    capability.name,
                    created_at.isoformat(),
                    json.dumps(payload, ensure_ascii=False),
                ),
            )
        return CapabilityVersion(
            capability_id=capability.capability_id,
            version=version,
            status=capability.status,
            name=capability.name,
            created_at=created_at,
            capability=payload,
        )

    def promote_verified(
        self,
        capability_id: str,
        report: ValidationReport,
    ) -> CapabilityVersion:
        """Create a verified version only after an independent passing report."""
        if report.target_type != "capability" or report.target_id != capability_id:
            raise ValueError("validation report target does not match capability")
        if report.overall_status != "passed":
            raise ValueError("only a passing independent validation report can promote a capability")
        current = self.latest(capability_id)
        if current is None:
            raise KeyError(f"capability not found: {capability_id}")
        capability = AlgorithmCapability.model_validate(current.capability).model_copy(
            update={"status": "verified"}
        )
        return self.save(capability)

    def latest(self, capability_id: str) -> CapabilityVersion | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT capability_id, version, status, name, created_at, payload_json
                FROM capabilities
                WHERE capability_id = ?
                ORDER BY version DESC LIMIT 1
                """,
                (capability_id,),
            ).fetchone()
        return _row_to_version(row) if row else None

    def search(self, query: str, *, limit: int = 20) -> list[CapabilityVersion]:
        if not query.strip():
            raise ValueError("query cannot be empty")
        if limit < 1:
            raise ValueError("limit must be positive")
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT capability_id, version, status, name, created_at, payload_json
                FROM capabilities
                WHERE name LIKE ?
                ORDER BY created_at DESC, version DESC
                LIMIT ?
                """,
                (f"%{query.strip()}%", limit),
            ).fetchall()
        return [_row_to_version(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS capabilities (
                    capability_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY (capability_id, version)
                )
                """
            )


def _row_to_version(row: sqlite3.Row) -> CapabilityVersion:
    return CapabilityVersion(
        capability_id=row["capability_id"],
        version=row["version"],
        status=row["status"],
        name=row["name"],
        created_at=datetime.fromisoformat(row["created_at"]),
        capability=json.loads(row["payload_json"]),
    )
