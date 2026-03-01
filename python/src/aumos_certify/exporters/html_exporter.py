# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
HTML exporter for certification results.

Serializes a ``CertificationResult`` to a standalone, self-contained HTML document
suitable for sharing, archiving, or embedding in CI pipeline artifacts. The HTML
document includes inline CSS and requires no external network resources.

Example
-------
>>> exporter = HtmlExporter()
>>> html_str = exporter.export(result)
>>> exporter.write(result, "output/cert-report.html")
"""

from __future__ import annotations

import html
from pathlib import Path

from aumos_certify.levels import get_level_definition
from aumos_certify.types import CertificationLevel, CertificationResult, ConformanceStatus

__all__ = ["HtmlExporter"]

# Badge colors per certification level
_LEVEL_COLORS: dict[CertificationLevel, str] = {
    CertificationLevel.BRONZE: "#CD7F32",
    CertificationLevel.SILVER: "#C0C0C0",
    CertificationLevel.GOLD: "#FFD700",
    CertificationLevel.PLATINUM: "#E5E4E2",
}

# CSS class per check status
_STATUS_CSS_CLASS: dict[ConformanceStatus, str] = {
    ConformanceStatus.PASS: "status-pass",
    ConformanceStatus.FAIL: "status-fail",
    ConformanceStatus.SKIP: "status-skip",
    ConformanceStatus.ERROR: "status-error",
}

_INLINE_CSS = """\
  :root { --font: system-ui, sans-serif; --border: #dee2e6; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: var(--font); font-size: 14px; color: #212529;
         background: #f8f9fa; padding: 32px; }
  .report { max-width: 900px; margin: 0 auto; background: #fff;
            border: 1px solid var(--border); border-radius: 8px;
            padding: 32px; }
  h1 { font-size: 1.6rem; margin-bottom: 8px; }
  h2 { font-size: 1.2rem; margin: 24px 0 12px; border-bottom: 1px solid var(--border);
       padding-bottom: 6px; }
  h3 { font-size: 1rem; margin: 16px 0 8px; }
  .notice { background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px;
            padding: 12px 16px; margin: 16px 0; font-size: 0.9rem; }
  .summary-table { width: 100%; border-collapse: collapse; margin: 12px 0; }
  .summary-table th, .summary-table td { border: 1px solid var(--border);
                                          padding: 8px 12px; text-align: left; }
  .summary-table th { background: #f1f3f5; font-weight: 600; }
  .level-badge { display: inline-block; padding: 4px 12px; border-radius: 12px;
                 font-weight: 700; font-size: 0.85rem; color: #212529; }
  .checks-table { width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 0.85rem; }
  .checks-table th, .checks-table td { border: 1px solid var(--border);
                                        padding: 6px 10px; text-align: left; }
  .checks-table th { background: #f1f3f5; font-weight: 600; }
  .status-pass { color: #198754; font-weight: 600; }
  .status-fail { color: #dc3545; font-weight: 600; }
  .status-skip { color: #6c757d; }
  .status-error { color: #fd7e14; font-weight: 600; }
  .level-satisfied { color: #198754; font-weight: 600; }
  .level-missing { color: #6c757d; }
  .meta { color: #6c757d; font-size: 0.85rem; margin-bottom: 16px; }
  footer { margin-top: 32px; font-size: 0.8rem; color: #6c757d; border-top: 1px solid var(--border);
           padding-top: 12px; }
"""


class HtmlExporter:
    """Exports a ``CertificationResult`` as a standalone HTML document.

    The HTML is self-contained (no external CSS or JS dependencies) and
    renders cleanly in any modern browser.

    Parameters
    ----------
    include_level_detail:
        When True (default), includes the level-by-level evaluation section.
        Set to False for a more compact output.
    """

    def __init__(self, include_level_detail: bool = True) -> None:
        self._include_level_detail = include_level_detail

    def export(self, result: CertificationResult) -> str:
        """Serialize *result* to an HTML string.

        Parameters
        ----------
        result:
            The certification result to export.

        Returns
        -------
        str:
            HTML-formatted certification report.
        """
        body_parts: list[str] = [
            self._render_header(result),
            self._render_summary(result),
            self._render_protocol_results(result),
        ]
        if self._include_level_detail and result.level_detail:
            body_parts.append(self._render_level_detail(result))
        body_parts.append(self._render_footer())

        body = "\n".join(body_parts)
        return self._wrap_document(result, body)

    def write(self, result: CertificationResult, path: str | Path) -> None:
        """Write the HTML export to *path*.

        Creates parent directories if they do not exist.

        Parameters
        ----------
        result:
            The certification result to export.
        path:
            File path to write the HTML output to.
        """
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.export(result), encoding="utf-8")

    @staticmethod
    def _wrap_document(result: CertificationResult, body: str) -> str:
        """Wrap *body* in a complete HTML5 document."""
        run = result.run_result
        title = html.escape(
            f"AumOS Certification Report — {run.implementation_name}"
        )
        return (
            "<!DOCTYPE html>\n"
            '<html lang="en">\n'
            "<head>\n"
            '  <meta charset="UTF-8">\n'
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f"  <title>{title}</title>\n"
            "<style>\n"
            f"{_INLINE_CSS}"
            "</style>\n"
            "</head>\n"
            "<body>\n"
            '<div class="report">\n'
            f"{body}\n"
            "</div>\n"
            "</body>\n"
            "</html>"
        )

    @staticmethod
    def _render_header(result: CertificationResult) -> str:
        """Render the document title, metadata, and self-assessment notice."""
        run = result.run_result
        date_str = html.escape(run.started_at.strftime("%Y-%m-%d %H:%M UTC"))
        impl_name = html.escape(run.implementation_name)
        run_id = html.escape(run.run_id)

        return (
            "<h1>AumOS Certification Report</h1>\n"
            '<div class="meta">'
            f"<strong>Implementation:</strong> {impl_name} &nbsp;|&nbsp; "
            f"<strong>Run ID:</strong> <code>{run_id}</code> &nbsp;|&nbsp; "
            f"<strong>Date:</strong> {date_str}"
            "</div>\n"
            '<div class="notice">'
            "<strong>Self-Assessment Notice:</strong> This report is generated "
            "locally by <code>aumos-certify</code> and reflects the implementer's "
            "own test results. The badge is labeled &ldquo;Self-Assessed&rdquo; — "
            "this is not an official third-party audit."
            "</div>"
        )

    @staticmethod
    def _render_summary(result: CertificationResult) -> str:
        """Render the summary table with level badge."""
        level_label = (
            result.achieved_level.value.capitalize()
            if result.achieved_level is not None
            else "None"
        )
        level_color = (
            _LEVEL_COLORS.get(result.achieved_level, "#adb5bd")
            if result.achieved_level is not None
            else "#adb5bd"
        )
        level_def = (
            get_level_definition(result.achieved_level)
            if result.achieved_level is not None
            else None
        )

        badge_html = (
            f'<span class="level-badge" style="background:{level_color}">'
            f"{html.escape(level_label)}</span>"
        )

        protocols_run = result.run_result.protocols_run
        satisfied_text = "Yes" if result.required_protocols_satisfied else "No"

        rows: list[str] = [
            "<h2>Summary</h2>",
            '<table class="summary-table">',
            "<thead><tr><th>Field</th><th>Value</th></tr></thead>",
            "<tbody>",
            f"  <tr><td>Overall Score</td><td><strong>{result.score_pct:.1f}%</strong></td></tr>",
            f"  <tr><td>Achieved Level</td><td>{badge_html}</td></tr>",
            f"  <tr><td>Protocols Run</td><td>{len(protocols_run)}</td></tr>",
            f"  <tr><td>Required Protocols Satisfied</td><td>{satisfied_text}</td></tr>",
        ]

        if level_def is not None:
            rows.append(
                f"  <tr><td>Display Name</td>"
                f"<td>{html.escape(level_def.display_name)}</td></tr>"
            )

        if result.missing_protocols:
            missing_str = html.escape(", ".join(result.missing_protocols))
            rows.append(f"  <tr><td>Missing Protocols</td><td>{missing_str}</td></tr>")

        rows += ["</tbody>", "</table>"]
        return "\n".join(rows)

    @staticmethod
    def _render_protocol_results(result: CertificationResult) -> str:
        """Render per-protocol check results."""
        run = result.run_result
        lines: list[str] = ["<h2>Protocol Results</h2>"]

        if not run.protocols_run:
            lines.append("<p><em>No protocols were run.</em></p>")
            return "\n".join(lines)

        for protocol_id in run.protocols_run:
            proto_result = run.protocol_results.get(protocol_id)
            if proto_result is None:
                continue

            score_pct = proto_result.score * 100.0
            lines += [
                f"<h3>{html.escape(protocol_id.upper())}</h3>",
                f"<p><strong>Score:</strong> {score_pct:.1f}% "
                f"({proto_result.passed}/{proto_result.total} checks passed)</p>",
                '<table class="checks-table">',
                "<thead><tr>"
                "<th>Check ID</th><th>Description</th>"
                "<th>Level</th><th>Status</th><th>Message</th>"
                "</tr></thead>",
                "<tbody>",
            ]

            for check in proto_result.checks:
                css_class = _STATUS_CSS_CLASS.get(check.status, "")
                status_label = check.status.value.upper()
                message = html.escape(check.message or "")
                description = html.escape(check.description)
                conformance = html.escape(check.conformance_level)
                check_id = html.escape(check.check_id)

                lines.append(
                    f"  <tr>"
                    f"<td><code>{check_id}</code></td>"
                    f"<td>{description}</td>"
                    f"<td>{conformance}</td>"
                    f'<td class="{css_class}">{status_label}</td>'
                    f"<td>{message}</td>"
                    f"</tr>"
                )

            lines += ["</tbody>", "</table>"]

        return "\n".join(lines)

    @staticmethod
    def _render_level_detail(result: CertificationResult) -> str:
        """Render the level-by-level evaluation section."""
        lines: list[str] = ["<h2>Level Detail</h2>"]

        for level_id, detail in result.level_detail.items():
            if not isinstance(detail, dict):
                continue
            satisfied = detail.get("satisfied", False)
            status_class = "level-satisfied" if satisfied else "level-missing"
            status_text = "ACHIEVED" if satisfied else "not satisfied"

            lines += [
                f'<h3>{html.escape(level_id.capitalize())} — '
                f'<span class="{status_class}">{status_text}</span></h3>',
                "<ul>",
                f"  <li>Minimum score required: {detail.get('minimum_score_pct')}%</li>",
                f"  <li>Actual score: {detail.get('actual_score_pct')}%</li>",
                f"  <li>Required protocols: "
                f"{html.escape(', '.join(detail.get('required_protocols', [])))}</li>",
            ]
            missing = detail.get("missing_protocols", [])
            if missing:
                lines.append(
                    f"  <li>Missing protocols: {html.escape(', '.join(missing))}</li>"
                )
            lines.append("</ul>")

        return "\n".join(lines)

    @staticmethod
    def _render_footer() -> str:
        """Render the document footer."""
        return (
            "<footer>\n"
            "Generated by "
            '<a href="https://github.com/aumos-ai/trust-certification-toolkit" '
            'rel="noopener noreferrer">aumos-certify</a>. '
            "Self-assessment only — not an official audit.<br>\n"
            "Apache License, Version 2.0 — Copyright &copy; 2026 MuVeraAI Corporation\n"
            "</footer>"
        )
