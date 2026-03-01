# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
Markdown exporter for certification results.

Serializes a ``CertificationResult`` to a human-readable Markdown document
suitable for including in repository documentation, PR descriptions, or
attaching to release notes.

Example
-------
>>> exporter = MarkdownExporter()
>>> md_str = exporter.export(result)
>>> exporter.write(result, "output/cert-report.md")
"""

from __future__ import annotations

from pathlib import Path

from aumos_certify.levels import get_level_definition
from aumos_certify.types import CertificationResult, ConformanceStatus

__all__ = ["MarkdownExporter"]

# Map ConformanceStatus to Markdown-friendly display strings
_STATUS_LABEL: dict[ConformanceStatus, str] = {
    ConformanceStatus.PASS: "PASS",
    ConformanceStatus.FAIL: "FAIL",
    ConformanceStatus.SKIP: "SKIP",
    ConformanceStatus.ERROR: "ERROR",
}


class MarkdownExporter:
    """Exports a ``CertificationResult`` as a Markdown document.

    The output is a self-contained Markdown report covering the summary
    table, per-protocol check details, and level-by-level evaluation.

    Parameters
    ----------
    include_level_detail:
        When True (default), includes the level-by-level evaluation section
        at the end of the document. Set to False for a shorter output.
    """

    def __init__(self, include_level_detail: bool = True) -> None:
        self._include_level_detail = include_level_detail

    def export(self, result: CertificationResult) -> str:
        """Serialize *result* to a Markdown string.

        Parameters
        ----------
        result:
            The certification result to export.

        Returns
        -------
        str:
            Markdown-formatted certification report.
        """
        sections: list[str] = []
        sections.append(self._header(result))
        sections.append(self._summary_table(result))
        sections.append(self._protocol_results(result))
        if self._include_level_detail and result.level_detail:
            sections.append(self._level_detail(result))
        sections.append(self._footer())
        return "\n\n".join(sections)

    def write(self, result: CertificationResult, path: str | Path) -> None:
        """Write the Markdown export to *path*.

        Creates parent directories if they do not exist.

        Parameters
        ----------
        result:
            The certification result to export.
        path:
            File path to write the Markdown output to.
        """
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.export(result), encoding="utf-8")

    @staticmethod
    def _header(result: CertificationResult) -> str:
        """Render the document header and self-assessment notice."""
        run = result.run_result
        return (
            "# AumOS Certification Report\n\n"
            "> **This is a self-assessment report.** It is generated locally by "
            "`aumos-certify` and reflects the implementer's own test results.\n"
            "> The badge is labeled \"Self-Assessed\" — this is not an official third-party audit.\n\n"
            "---\n\n"
            f"**Implementation:** {run.implementation_name}  \n"
            f"**Run ID:** `{run.run_id}`  \n"
            f"**Date:** {run.started_at.strftime('%Y-%m-%d %H:%M UTC')}"
        )

    @staticmethod
    def _summary_table(result: CertificationResult) -> str:
        """Render the top-level summary table."""
        run = result.run_result
        level_label = (
            result.achieved_level.value.capitalize()
            if result.achieved_level is not None
            else "None"
        )
        level_def = (
            get_level_definition(result.achieved_level)
            if result.achieved_level is not None
            else None
        )

        rows: list[str] = [
            "## Summary",
            "",
            "| Field | Value |",
            "|---|---|",
            f"| Overall Score | **{result.score_pct:.1f}%** |",
            f"| Achieved Level | **{level_label}** |",
            f"| Protocols Run | {len(run.protocols_run)} |",
            f"| Required Protocols Satisfied | {'Yes' if result.required_protocols_satisfied else 'No'} |",
        ]

        if level_def is not None:
            rows.append(f"| Display Name | {level_def.display_name} |")
            rows.append(f"| Badge Color | `{level_def.badge_color}` |")

        if result.missing_protocols:
            rows.append(f"| Missing Protocols | {', '.join(result.missing_protocols)} |")

        return "\n".join(rows)

    @staticmethod
    def _protocol_results(result: CertificationResult) -> str:
        """Render the per-protocol check results section."""
        run = result.run_result
        lines: list[str] = ["## Protocol Results", ""]

        if not run.protocols_run:
            lines.append("*No protocols were run.*")
            return "\n".join(lines)

        for protocol_id in run.protocols_run:
            proto_result = run.protocol_results.get(protocol_id)
            if proto_result is None:
                continue

            score_pct = proto_result.score * 100.0
            lines += [
                f"### {protocol_id.upper()}",
                "",
                f"**Score:** {score_pct:.1f}% "
                f"({proto_result.passed}/{proto_result.total} checks passed)",
                "",
                "| Check ID | Description | Level | Status | Message |",
                "|---|---|---|---|---|",
            ]

            for check in proto_result.checks:
                status_label = _STATUS_LABEL.get(check.status, check.status.value)
                message = (check.message or "").replace("|", "\\|")
                description = check.description.replace("|", "\\|")
                lines.append(
                    f"| `{check.check_id}` | {description} "
                    f"| {check.conformance_level} | {status_label} | {message} |"
                )

            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _level_detail(result: CertificationResult) -> str:
        """Render the level-by-level evaluation section."""
        lines: list[str] = ["## Level Detail", ""]

        for level_id, detail in result.level_detail.items():
            if not isinstance(detail, dict):
                continue
            satisfied = detail.get("satisfied", False)
            status = "ACHIEVED" if satisfied else "not satisfied"
            lines += [
                f"### {level_id.capitalize()} — {status}",
                "",
                f"- Minimum score required: {detail.get('minimum_score_pct')}%",
                f"- Actual score: {detail.get('actual_score_pct')}%",
                f"- Required protocols: {', '.join(detail.get('required_protocols', []))}",
            ]
            missing = detail.get("missing_protocols", [])
            if missing:
                lines.append(f"- Missing protocols: {', '.join(missing)}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _footer() -> str:
        """Render the document footer."""
        return (
            "---\n\n"
            "*Generated by [aumos-certify](https://github.com/aumos-ai/trust-certification-toolkit). "
            "Self-assessment only — not an official audit.*\n\n"
            "Apache License, Version 2.0 — "
            "Copyright (c) 2026 MuVeraAI Corporation"
        )
