# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
Certification history — persists and retrieves past certification runs.

``CertHistory`` stores ``CertificationResult`` instances to a JSONL file
(one JSON object per line) so that teams can track how their conformance
score has changed over time.

All data stays local. No network calls are made.

Example
-------
>>> history = CertHistory("output/cert-history.jsonl")
>>> history.append(result)
>>> entries = history.load_all()
>>> print(entries[-1].run_result.implementation_name)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aumos_certify.types import (
    CertificationLevel,
    CertificationResult,
    CheckResult,
    ConformanceStatus,
    ProtocolResult,
    RunResult,
)

__all__ = ["CertHistory", "CertHistoryEntry"]


@dataclass(frozen=True)
class CertHistoryEntry:
    """A single record in the certification history.

    Attributes
    ----------
    result:
        The full ``CertificationResult`` for this run.
    recorded_at:
        UTC timestamp when this entry was appended to the history store.
    """

    result: CertificationResult
    recorded_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Serialize this entry to a plain dict suitable for JSON encoding."""
        run = self.result.run_result

        protocol_results_data: dict[str, Any] = {}
        for protocol_id, proto_result in run.protocol_results.items():
            protocol_results_data[protocol_id] = {
                "protocol": proto_result.protocol,
                "passed": proto_result.passed,
                "failed": proto_result.failed,
                "skipped": proto_result.skipped,
                "errors": proto_result.errors,
                "checks": [
                    {
                        "check_id": c.check_id,
                        "description": c.description,
                        "status": c.status.value,
                        "message": c.message,
                        "conformance_level": c.conformance_level,
                    }
                    for c in proto_result.checks
                ],
            }

        return {
            "recorded_at": self.recorded_at.isoformat(),
            "result": {
                "run_result": {
                    "implementation_name": run.implementation_name,
                    "run_id": run.run_id,
                    "started_at": run.started_at.isoformat(),
                    "completed_at": run.completed_at.isoformat(),
                    "protocols_run": run.protocols_run,
                    "protocol_results": protocol_results_data,
                },
                "achieved_level": (
                    self.result.achieved_level.value
                    if self.result.achieved_level is not None
                    else None
                ),
                "score_pct": self.result.score_pct,
                "required_protocols_satisfied": self.result.required_protocols_satisfied,
                "missing_protocols": self.result.missing_protocols,
                "level_detail": self.result.level_detail,
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CertHistoryEntry":
        """Reconstruct a ``CertHistoryEntry`` from a serialized dict."""
        recorded_at = datetime.fromisoformat(data["recorded_at"])
        result_data = data["result"]
        run_data = result_data["run_result"]

        protocol_results: dict[str, ProtocolResult] = {}
        for protocol_id, pr_data in run_data.get("protocol_results", {}).items():
            checks = [
                CheckResult(
                    check_id=c["check_id"],
                    description=c["description"],
                    status=ConformanceStatus(c["status"]),
                    message=c.get("message"),
                    conformance_level=c.get("conformance_level", "MUST"),
                )
                for c in pr_data.get("checks", [])
            ]
            protocol_results[protocol_id] = ProtocolResult(
                protocol=pr_data["protocol"],
                checks=checks,
                passed=pr_data.get("passed", 0),
                failed=pr_data.get("failed", 0),
                skipped=pr_data.get("skipped", 0),
                errors=pr_data.get("errors", 0),
            )

        run_result = RunResult(
            implementation_name=run_data["implementation_name"],
            run_id=run_data["run_id"],
            started_at=datetime.fromisoformat(run_data["started_at"]),
            completed_at=datetime.fromisoformat(run_data["completed_at"]),
            protocols_run=run_data.get("protocols_run", []),
            protocol_results=protocol_results,
        )

        achieved_level_raw = result_data.get("achieved_level")
        achieved_level = (
            CertificationLevel(achieved_level_raw)
            if achieved_level_raw is not None
            else None
        )

        result = CertificationResult(
            run_result=run_result,
            achieved_level=achieved_level,
            score_pct=result_data["score_pct"],
            required_protocols_satisfied=result_data["required_protocols_satisfied"],
            missing_protocols=result_data.get("missing_protocols", []),
            level_detail=result_data.get("level_detail", {}),
        )

        return cls(result=result, recorded_at=recorded_at)


@dataclass
class CertHistory:
    """Persistent certification history backed by a JSONL file.

    Each call to ``append`` writes one JSON line to the file. ``load_all``
    reads every line and reconstructs the entries. The file grows append-only
    — no entries are ever overwritten or deleted.

    Parameters
    ----------
    path:
        File path for the JSONL history store. The parent directory is
        created automatically if it does not exist.

    Example
    -------
    >>> history = CertHistory("output/history.jsonl")
    >>> history.append(result)
    >>> all_entries = history.load_all()
    >>> latest = history.latest()
    """

    path: Path = field(default=Path("cert-history.jsonl"))

    def __post_init__(self) -> None:
        self.path = Path(self.path)

    def append(self, result: CertificationResult) -> CertHistoryEntry:
        """Append *result* to the history store.

        Parameters
        ----------
        result:
            The ``CertificationResult`` to persist.

        Returns
        -------
        CertHistoryEntry:
            The entry that was written, including the ``recorded_at`` timestamp.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        entry = CertHistoryEntry(
            result=result,
            recorded_at=datetime.now(tz=timezone.utc),
        )
        line = json.dumps(entry.to_dict(), default=str)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        return entry

    def load_all(self) -> list[CertHistoryEntry]:
        """Load every entry from the history store, oldest first.

        Returns
        -------
        list[CertHistoryEntry]:
            All stored entries in chronological order. Returns an empty list
            if the history file does not exist yet.
        """
        if not self.path.exists():
            return []

        entries: list[CertHistoryEntry] = []
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entries.append(CertHistoryEntry.from_dict(data))
                except (json.JSONDecodeError, KeyError, ValueError):
                    # Skip malformed lines — don't crash on partially-written records
                    continue
        return entries

    def latest(self) -> CertHistoryEntry | None:
        """Return the most recently appended entry, or None if history is empty.

        Returns
        -------
        CertHistoryEntry | None:
            The last entry in the history file, or None.
        """
        entries = self.load_all()
        return entries[-1] if entries else None

    def count(self) -> int:
        """Return the number of entries in the history store.

        Returns
        -------
        int:
            Total number of stored entries.
        """
        return len(self.load_all())

    def for_implementation(
        self,
        implementation_name: str,
    ) -> list[CertHistoryEntry]:
        """Return all entries for a specific implementation name.

        Parameters
        ----------
        implementation_name:
            The ``implementation_name`` to filter by.

        Returns
        -------
        list[CertHistoryEntry]:
            Matching entries in chronological order.
        """
        return [
            e
            for e in self.load_all()
            if e.result.run_result.implementation_name == implementation_name
        ]
