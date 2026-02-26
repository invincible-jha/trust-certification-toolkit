# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
aumos-certify CLI — self-assessment toolkit for the AumOS Certified badge program.

Commands:
  run     Run conformance checks against an implementation adapter
  badge   Generate an SVG badge for a given certification level
  report  Generate a certification report (Markdown or JSON)
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Annotated, Optional

import anyio
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aumos_certify.levels import ALL_PROTOCOL_IDS, LEVEL_DEFINITIONS, get_level_definition
from aumos_certify.report import ReportGenerator
from aumos_certify.runner import ConformanceRunner
from aumos_certify.scorer import CertificationScorer
from aumos_certify.types import CertificationLevel, CertificationResult, ImplementationAdapter

app = typer.Typer(
    name="aumos-certify",
    help=(
        "AumOS self-assessment toolkit. "
        "All operations are LOCAL ONLY — no data is sent anywhere."
    ),
    add_completion=False,
)

console = Console()
error_console = Console(stderr=True, style="bold red")

# State shared between commands within a session
_last_result: CertificationResult | None = None


@app.command(name="run")
def run_command(
    implementation: Annotated[
        str,
        typer.Option(
            "--implementation",
            "-i",
            help=(
                "Path to a Python file or importable module that exposes "
                "an ImplementationAdapter subclass as 'adapter'."
            ),
        ),
    ],
    level: Annotated[
        Optional[str],
        typer.Option(
            "--level",
            "-l",
            help=(
                "Target certification level (bronze, silver, gold, platinum). "
                "If provided, only the protocols required for that level are run."
            ),
        ),
    ] = None,
    protocols: Annotated[
        Optional[str],
        typer.Option(
            "--protocols",
            "-p",
            help="Comma-separated list of protocol IDs to run (e.g., atp,aeap,aoap).",
        ),
    ] = None,
) -> None:
    """Run conformance checks against an implementation adapter."""
    global _last_result  # noqa: PLW0603

    adapter = _load_adapter(implementation)

    # Determine which protocols to run
    if protocols is not None:
        protocol_list = [p.strip() for p in protocols.split(",")]
    elif level is not None:
        try:
            target_level = CertificationLevel(level.lower())
        except ValueError:
            error_console.print(f"Unknown level '{level}'. Choose from: bronze, silver, gold, platinum")
            raise typer.Exit(code=1) from None
        level_def = get_level_definition(target_level)
        protocol_list = list(level_def.required_protocols)
    else:
        protocol_list = list(ALL_PROTOCOL_IDS)

    console.print(Panel(
        f"[bold]AumOS Self-Assessment[/bold]\n"
        f"Implementation: {adapter.get_implementation_name()}\n"
        f"Protocols: {', '.join(protocol_list)}",
        title="aumos-certify run",
        border_style="blue",
    ))

    runner = ConformanceRunner(implementation=adapter)
    run_result = anyio.from_thread.run_sync(
        lambda: anyio.run(runner.run, protocol_list)
    )

    scorer = CertificationScorer()
    cert_result = scorer.score(run_result)
    _last_result = cert_result

    _print_run_summary(cert_result)

    if cert_result.achieved_level is None:
        raise typer.Exit(code=1)


@app.command(name="badge")
def badge_command(
    level: Annotated[
        str,
        typer.Option(
            "--level",
            "-l",
            help="Certification level (bronze, silver, gold, platinum).",
        ),
    ],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output file path for the generated SVG badge.",
        ),
    ] = "aumos-badge.svg",
) -> None:
    """Generate an SVG badge for a given certification level."""
    try:
        target_level = CertificationLevel(level.lower())
    except ValueError:
        error_console.print(f"Unknown level '{level}'. Choose from: bronze, silver, gold, platinum")
        raise typer.Exit(code=1) from None

    level_def = get_level_definition(target_level)
    svg = _generate_svg_badge(target_level, level_def.badge_color, level_def.display_name)

    output_path = Path(output)
    output_path.write_text(svg, encoding="utf-8")

    console.print(
        f"[green]Badge generated:[/green] {output_path.resolve()}\n"
        f"Level: {level_def.display_name}\n"
        f"Color: {level_def.badge_color}"
    )


@app.command(name="report")
def report_command(
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: 'md' (Markdown) or 'json'.",
        ),
    ] = "md",
    output: Annotated[
        Optional[str],
        typer.Option(
            "--output",
            "-o",
            help="Output file path. If omitted, prints to stdout.",
        ),
    ] = None,
    implementation: Annotated[
        Optional[str],
        typer.Option(
            "--implementation",
            "-i",
            help="Path to adapter (required if no previous 'run' was executed in this session).",
        ),
    ] = None,
    protocols: Annotated[
        Optional[str],
        typer.Option("--protocols", "-p", help="Comma-separated protocol IDs to run."),
    ] = None,
) -> None:
    """Generate a certification report in Markdown or JSON format."""
    global _last_result  # noqa: PLW0603

    if format not in ("md", "json"):
        error_console.print(f"Unknown format '{format}'. Use 'md' or 'json'.")
        raise typer.Exit(code=1)

    cert_result = _last_result
    if cert_result is None:
        if implementation is None:
            error_console.print(
                "No previous run result found. "
                "Run 'aumos-certify run --implementation <path>' first, "
                "or provide --implementation to run now."
            )
            raise typer.Exit(code=1)

        adapter = _load_adapter(implementation)
        protocol_list = (
            [p.strip() for p in protocols.split(",")] if protocols else list(ALL_PROTOCOL_IDS)
        )
        runner = ConformanceRunner(implementation=adapter)
        run_result = anyio.run(runner.run, protocol_list)
        scorer = CertificationScorer()
        cert_result = scorer.score(run_result)
        _last_result = cert_result

    generator = ReportGenerator()
    # format is validated above; safe to pass as Literal
    report_text = generator.generate(cert_result, format=format)  # type: ignore[arg-type]

    if output is not None:
        output_path = Path(output)
        output_path.write_text(report_text, encoding="utf-8")
        console.print(f"[green]Report written to:[/green] {output_path.resolve()}")
    else:
        console.print(report_text)


def _load_adapter(path_or_module: str) -> ImplementationAdapter:
    """Load an ImplementationAdapter from a file path or importable module."""
    target_path = Path(path_or_module)
    if target_path.exists() and target_path.suffix == ".py":
        spec = importlib.util.spec_from_file_location("_aumos_adapter_module", target_path)
        if spec is None or spec.loader is None:
            error_console.print(f"Cannot load adapter from '{target_path}'")
            raise typer.Exit(code=1)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
    else:
        try:
            module = importlib.import_module(path_or_module)
        except ImportError as exc:
            error_console.print(f"Cannot import adapter module '{path_or_module}': {exc}")
            raise typer.Exit(code=1) from exc

    adapter = getattr(module, "adapter", None)
    if adapter is None:
        error_console.print(
            f"Module '{path_or_module}' does not expose an 'adapter' attribute. "
            "Define an ImplementationAdapter subclass instance named 'adapter'."
        )
        raise typer.Exit(code=1)

    if not isinstance(adapter, ImplementationAdapter):
        error_console.print(
            f"'adapter' in '{path_or_module}' must be an ImplementationAdapter instance."
        )
        raise typer.Exit(code=1)

    return adapter


def _print_run_summary(cert_result: CertificationResult) -> None:
    """Print a Rich-formatted summary of the certification result."""
    run = cert_result.run_result

    level_label = (
        cert_result.achieved_level.value.upper()
        if cert_result.achieved_level is not None
        else "NONE"
    )
    level_color = "green" if cert_result.achieved_level is not None else "red"

    console.print()
    console.print(
        Panel(
            f"[bold {level_color}]Achieved Level: {level_label}[/bold {level_color}]\n"
            f"Overall Score: {cert_result.score_pct:.1f}%",
            title="Certification Result",
            border_style=level_color,
        )
    )

    table = Table(title="Protocol Results", show_header=True, header_style="bold blue")
    table.add_column("Protocol")
    table.add_column("Score", justify="right")
    table.add_column("Passed", justify="right")
    table.add_column("Failed", justify="right")
    table.add_column("Skipped", justify="right")

    for protocol_id in run.protocols_run:
        pr = run.protocol_results.get(protocol_id)
        if pr is None:
            continue
        color = "green" if pr.failed == 0 else "red"
        table.add_row(
            protocol_id.upper(),
            f"[{color}]{pr.score * 100:.1f}%[/{color}]",
            str(pr.passed),
            f"[red]{pr.failed}[/red]" if pr.failed > 0 else "0",
            str(pr.skipped),
        )

    console.print(table)

    if cert_result.missing_protocols:
        console.print(
            f"\n[yellow]Missing protocols for next level:[/yellow] "
            f"{', '.join(cert_result.missing_protocols)}"
        )


def _generate_svg_badge(
    level: CertificationLevel,
    color: str,
    display_name: str,
) -> str:
    """Generate a minimal SVG badge for the given level."""
    level_label = level.value.capitalize()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="220" height="64" role="img" aria-label="{display_name}">
  <title>{display_name}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="220" height="64" rx="8" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="110" height="64" fill="#555"/>
    <rect x="110" width="110" height="64" fill="{color}"/>
    <rect width="220" height="64" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="13">
    <text x="55" y="22" fill="#010101" fill-opacity=".3">AumOS</text>
    <text x="55" y="21">AumOS</text>
    <text x="55" y="38" fill="#010101" fill-opacity=".3">Self-Assessed</text>
    <text x="55" y="37">Self-Assessed</text>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="15" font-weight="bold">
    <text x="165" y="37" fill="#010101" fill-opacity=".3">{level_label}</text>
    <text x="165" y="36">{level_label}</text>
  </g>
</svg>"""


if __name__ == "__main__":
    app()
