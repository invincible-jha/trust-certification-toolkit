# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
Enterprise certification dashboard for the AumOS Certified badge program.

Aggregates certification status across an organisation's agent fleet using
purely in-memory, local storage. No network calls are made by any operation
in this module.

Example usage::

    from datetime import datetime, timezone
    from enterprise_dashboard import AgentCertificationStatus, EnterpriseDashboard
    from aumos_certify.types import CertificationLevel

    dashboard = EnterpriseDashboard(org_name="Acme Corp")

    status = AgentCertificationStatus(
        agent_id="agent-001",
        agent_name="Support Agent",
        certification_level=CertificationLevel.SILVER,
        last_assessment_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        expiry_date=datetime(2028, 2, 1, tzinfo=timezone.utc),
        protocols_passed=["atp", "aeap", "aoap"],
        protocols_failed=[],
        pass_rate=0.85,
    )
    dashboard.register_agent(status)

    summary = dashboard.generate_summary()
    print(dashboard.export_summary_markdown(summary))
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator

from aumos_certify.types import CertificationLevel


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class AgentCertificationStatus(BaseModel, frozen=True):
    """Snapshot of a single agent's certification state within the fleet."""

    agent_id: str = Field(description="Stable unique identifier for the agent.")
    agent_name: str = Field(description="Human-readable name of the agent.")
    certification_level: CertificationLevel = Field(
        description="The self-assessed certification level currently held."
    )
    last_assessment_date: datetime = Field(
        description="Timestamp of the most recent completed self-assessment."
    )
    expiry_date: datetime = Field(
        description="Date and time at which the current certification expires."
    )
    protocols_passed: list[str] = Field(
        default_factory=list,
        description="Protocol identifiers that passed in the last assessment.",
    )
    protocols_failed: list[str] = Field(
        default_factory=list,
        description="Protocol identifiers that failed in the last assessment.",
    )
    pass_rate: float = Field(
        description="Overall pass rate from the last assessment, in the range [0.0, 1.0].",
        ge=0.0,
        le=1.0,
    )

    @field_validator("expiry_date")
    @classmethod
    def expiry_must_be_after_assessment(
        cls, expiry_date: datetime, info: Any
    ) -> datetime:
        """Expiry date must be strictly after the assessment date."""
        assessment_date: datetime | None = (
            info.data.get("last_assessment_date") if info.data else None
        )
        if assessment_date is not None and expiry_date <= assessment_date:
            raise ValueError(
                "expiry_date must be strictly after last_assessment_date"
            )
        return expiry_date


class DashboardSummary(BaseModel, frozen=True):
    """Fleet-wide aggregation of certification status across all registered agents."""

    total_agents: int = Field(
        description="Total number of agents registered in the dashboard."
    )
    certified_agents: int = Field(
        description="Number of agents whose certification has not yet expired."
    )
    expired_agents: int = Field(
        description="Number of agents whose certification expiry date has passed."
    )
    level_distribution: dict[str, int] = Field(
        description=(
            "Count of active (non-expired) agents per certification level. "
            "Keys are level values from CertificationLevel (e.g., 'bronze')."
        )
    )
    protocols_coverage: dict[str, float] = Field(
        description=(
            "Average pass rate per protocol across all registered agents that "
            "include that protocol in their assessment. Keys are protocol IDs."
        )
    )
    upcoming_expirations: list[AgentCertificationStatus] = Field(
        description="Agents whose certification expires within 30 days of the reference date.",
        default_factory=list,
    )


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


class EnterpriseDashboard:
    """
    In-memory enterprise certification dashboard.

    Maintains a registry of agent certification statuses and provides
    aggregation, filtering, and export capabilities. All operations are
    purely local — no network calls are made.

    Args:
        org_name: Display name for the organisation owning this fleet.
    """

    def __init__(self, org_name: str) -> None:
        self._org_name: str = org_name
        self._registry: dict[str, AgentCertificationStatus] = {}

    # ------------------------------------------------------------------
    # Registry management
    # ------------------------------------------------------------------

    def register_agent(self, status: AgentCertificationStatus) -> None:
        """Add or update an agent's certification status in the registry.

        If an agent with the same ``agent_id`` already exists it is replaced
        with the new status. This is the expected path for recording a
        re-assessment result.

        Args:
            status: The current certification status to register.
        """
        self._registry[status.agent_id] = status

    def remove_agent(self, agent_id: str) -> None:
        """Remove an agent from the registry.

        Silently does nothing if ``agent_id`` is not present.

        Args:
            agent_id: The stable identifier of the agent to remove.
        """
        self._registry.pop(agent_id, None)

    def get_agent(self, agent_id: str) -> AgentCertificationStatus | None:
        """Return the status for a single agent, or ``None`` if not found.

        Args:
            agent_id: The stable identifier of the agent to look up.

        Returns:
            The ``AgentCertificationStatus`` for that agent, or ``None``.
        """
        return self._registry.get(agent_id)

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def agents_expiring_within(self, days: int) -> list[AgentCertificationStatus]:
        """Return agents whose certification expires within the next ``days`` days.

        The reference point is the current wall-clock time in UTC.

        Args:
            days: Number of days from now to use as the expiry window.

        Returns:
            List of ``AgentCertificationStatus`` objects ordered by expiry date
            ascending (soonest first).
        """
        now: datetime = datetime.now(tz=timezone.utc)
        cutoff: datetime = now + timedelta(days=days)
        expiring = [
            status
            for status in self._registry.values()
            if now <= status.expiry_date <= cutoff
        ]
        return sorted(expiring, key=lambda s: s.expiry_date)

    def agents_by_level(self, level: str) -> list[AgentCertificationStatus]:
        """Return all agents whose certification level matches ``level``.

        Args:
            level: A ``CertificationLevel`` value string, e.g. ``"silver"``.

        Returns:
            List of matching ``AgentCertificationStatus`` objects, ordered by
            agent name ascending.
        """
        return sorted(
            (s for s in self._registry.values() if s.certification_level.value == level),
            key=lambda s: s.agent_name,
        )

    # ------------------------------------------------------------------
    # Summary generation
    # ------------------------------------------------------------------

    def generate_summary(
        self, reference_date: datetime | None = None
    ) -> DashboardSummary:
        """Compute a fleet-wide summary of certification status.

        Args:
            reference_date: The point-in-time to use for expiry calculations.
                Defaults to ``datetime.now(tz=timezone.utc)`` if not provided.

        Returns:
            A ``DashboardSummary`` instance containing fleet-wide aggregations.
        """
        now: datetime = (
            reference_date
            if reference_date is not None
            else datetime.now(tz=timezone.utc)
        )
        # Ensure the reference date is timezone-aware for consistent comparisons.
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        all_statuses: list[AgentCertificationStatus] = list(self._registry.values())
        total_agents: int = len(all_statuses)

        expired: list[AgentCertificationStatus] = [
            s for s in all_statuses if s.expiry_date < now
        ]
        active: list[AgentCertificationStatus] = [
            s for s in all_statuses if s.expiry_date >= now
        ]
        certified_count: int = len(active)
        expired_count: int = len(expired)

        # Level distribution counts only active (non-expired) agents.
        level_distribution: dict[str, int] = {
            level.value: 0 for level in CertificationLevel
        }
        for status in active:
            level_distribution[status.certification_level.value] += 1

        # Protocol coverage: average pass rate per protocol across all agents
        # (including expired ones, since the pass rate is a historical fact).
        protocol_totals: dict[str, list[float]] = {}
        for status in all_statuses:
            all_protocol_ids = status.protocols_passed + status.protocols_failed
            for protocol_id in all_protocol_ids:
                if protocol_id not in protocol_totals:
                    protocol_totals[protocol_id] = []
            for protocol_id in status.protocols_passed:
                protocol_totals[protocol_id].append(status.pass_rate)
            for protocol_id in status.protocols_failed:
                protocol_totals[protocol_id].append(0.0)

        protocols_coverage: dict[str, float] = {
            protocol_id: (sum(rates) / len(rates) if rates else 0.0)
            for protocol_id, rates in protocol_totals.items()
        }

        # Upcoming expirations: active agents expiring within 30 days.
        thirty_day_cutoff: datetime = now + timedelta(days=30)
        upcoming_expirations: list[AgentCertificationStatus] = sorted(
            (s for s in active if s.expiry_date <= thirty_day_cutoff),
            key=lambda s: s.expiry_date,
        )

        return DashboardSummary(
            total_agents=total_agents,
            certified_agents=certified_count,
            expired_agents=expired_count,
            level_distribution=level_distribution,
            protocols_coverage=protocols_coverage,
            upcoming_expirations=upcoming_expirations,
        )

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_summary_json(self, summary: DashboardSummary) -> str:
        """Serialise a ``DashboardSummary`` to a JSON string.

        The output uses ISO 8601 datetime formatting and 2-space indentation
        for readability.

        Args:
            summary: The summary to serialise.

        Returns:
            A JSON string representing the summary.
        """
        return summary.model_dump_json(indent=2)

    def export_summary_markdown(self, summary: DashboardSummary) -> str:
        """Render a ``DashboardSummary`` as a Markdown report.

        Produces a human-readable report suitable for inclusion in CI output,
        pull request comments, or internal documentation.

        Args:
            summary: The summary to render.

        Returns:
            A Markdown-formatted string.
        """
        lines: list[str] = [
            f"# AumOS Certified — Fleet Dashboard",
            f"",
            f"**Organisation:** {self._org_name}",
            f"",
            f"## Fleet Overview",
            f"",
            f"| Metric | Value |",
            f"|---|---|",
            f"| Total agents | {summary.total_agents} |",
            f"| Certified (active) | {summary.certified_agents} |",
            f"| Expired | {summary.expired_agents} |",
            f"",
            f"## Certification Level Distribution",
            f"",
            f"| Level | Agent Count |",
            f"|---|---|",
        ]

        for level in CertificationLevel:
            count = summary.level_distribution.get(level.value, 0)
            lines.append(f"| {level.value.capitalize()} | {count} |")

        lines += [
            f"",
            f"## Protocol Coverage",
            f"",
            f"Average pass rate per protocol across the full fleet.",
            f"",
            f"| Protocol | Average Pass Rate |",
            f"|---|---|",
        ]

        if summary.protocols_coverage:
            for protocol_id, avg_rate in sorted(summary.protocols_coverage.items()):
                pct = avg_rate * 100.0
                lines.append(f"| {protocol_id.upper()} | {pct:.1f}% |")
        else:
            lines.append(f"| — | No protocol data available |")

        lines += [
            f"",
            f"## Upcoming Expirations (within 30 days)",
            f"",
        ]

        if summary.upcoming_expirations:
            lines += [
                f"| Agent | Level | Expiry Date |",
                f"|---|---|---|",
            ]
            for status in summary.upcoming_expirations:
                expiry_str = status.expiry_date.strftime("%Y-%m-%d")
                lines.append(
                    f"| {status.agent_name} "
                    f"| {status.certification_level.value.capitalize()} "
                    f"| {expiry_str} |"
                )
        else:
            lines.append("No certifications expiring within the next 30 days.")

        lines += [
            f"",
            f"---",
            f"",
            f"*All certifications are self-assessed. "
            f"No AumOS verification is implied.*",
        ]

        return "\n".join(lines)
