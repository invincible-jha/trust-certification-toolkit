# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
JSON exporter for certification results.

Serializes a ``CertificationResult`` to a machine-readable JSON document
suitable for downstream tooling, CI pipeline consumption, or API responses.

Example
-------
>>> exporter = JsonExporter()
>>> json_str = exporter.export(result)
>>> exporter.write(result, "output/cert.json")
"""

from __future__ import annotations

import json
from pathlib import Path

from aumos_certify.types import CertificationResult

__all__ = ["JsonExporter"]


class JsonExporter:
    """Exports a ``CertificationResult`` as a JSON document.

    The output is self-contained: all fields from the result including
    per-protocol check results and score details are serialized.

    Parameters
    ----------
    indent:
        JSON indentation level. Defaults to 2 for human-readable output.
        Set to ``None`` for compact single-line JSON.
    """

    def __init__(self, indent: int | None = 2) -> None:
        self._indent = indent

    def export(self, result: CertificationResult) -> str:
        """Serialize *result* to a JSON string.

        Parameters
        ----------
        result:
            The certification result to export.

        Returns
        -------
        str:
            JSON-formatted certification data.
        """
        payload = self._build_payload(result)
        return json.dumps(payload, indent=self._indent, default=str)

    def write(self, result: CertificationResult, path: str | Path) -> None:
        """Write the JSON export to *path*.

        Creates parent directories if they do not exist.

        Parameters
        ----------
        result:
            The certification result to export.
        path:
            File path to write the JSON output to.
        """
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.export(result), encoding="utf-8")

    @staticmethod
    def _build_payload(result: CertificationResult) -> dict[str, object]:
        """Build the raw dict structure for JSON serialization."""
        run = result.run_result
        protocol_results = {}

        for protocol_id, proto_result in run.protocol_results.items():
            checks = [
                {
                    "check_id": c.check_id,
                    "description": c.description,
                    "status": c.status.value,
                    "message": c.message,
                    "conformance_level": c.conformance_level,
                }
                for c in proto_result.checks
            ]
            protocol_results[protocol_id] = {
                "protocol": proto_result.protocol,
                "passed": proto_result.passed,
                "failed": proto_result.failed,
                "skipped": proto_result.skipped,
                "errors": proto_result.errors,
                "score": proto_result.score,
                "checks": checks,
            }

        return {
            "implementation_name": run.implementation_name,
            "run_id": run.run_id,
            "started_at": run.started_at.isoformat(),
            "completed_at": run.completed_at.isoformat(),
            "protocols_run": run.protocols_run,
            "overall_score_pct": run.overall_score_pct,
            "achieved_level": (
                result.achieved_level.value if result.achieved_level else None
            ),
            "score_pct": result.score_pct,
            "required_protocols_satisfied": result.required_protocols_satisfied,
            "missing_protocols": result.missing_protocols,
            "level_detail": result.level_detail,
            "protocol_results": protocol_results,
        }
