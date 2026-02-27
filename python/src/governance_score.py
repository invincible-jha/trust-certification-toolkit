# SPDX-License-Identifier: BSL-1.1
# Copyright (c) 2026 MuVeraAI Corporation
"""
Governance scoring engine for the AumOS trust-certification-toolkit.

Computes a 0-100 governance score from a GovernanceProfile, mapping the result
to a Bronze/Silver/Gold/Platinum certification level and a hosted badge URL.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class GovernanceScoreResult:
    """Computed governance score with per-dimension breakdowns and certification level."""

    overall: int  # 0-100
    trust_coverage: int  # 0-100
    budget_coverage: int  # 0-100
    consent_coverage: int  # 0-100
    audit_coverage: int  # 0-100
    linter_score: int  # 0-100
    level: str  # Bronze/Silver/Gold/Platinum
    badge_url: str
    details: Sequence[str]


@dataclass(frozen=True)
class GovernanceProfile:
    """
    Input descriptor for governance score computation.

    All coverage percentages are in the range [0.0, 100.0].
    Setting a ``has_*`` flag to ``False`` treats that dimension as 0 regardless
    of the accompanying coverage value, which correctly penalises agents that
    have not adopted the relevant governance feature at all.
    """

    has_trust_levels: bool
    trust_level_coverage_pct: float
    has_budget_enforcement: bool
    budget_coverage_pct: float
    has_consent_management: bool
    consent_coverage_pct: float
    has_audit_trail: bool
    audit_coverage_pct: float
    linter_warnings: int
    linter_total_checks: int
    has_conformance_tests: bool
    conformance_level: str  # "none" | "basic" | "standard" | "full"
    has_shadow_mode: bool


def compute_governance_score(profile: GovernanceProfile) -> GovernanceScoreResult:
    """Compute a 0-100 governance score from a governance profile.

    Scoring is a weighted average of five dimensions:
    - trust_coverage   (25 %)
    - budget_coverage  (20 %)
    - consent_coverage (20 %)
    - audit_coverage   (25 %)
    - linter_score     (10 %)

    Optional bonuses are added for conformance test coverage (+2/+5/+10) and
    shadow-mode adoption (+3), capped at 100.

    Args:
        profile: A fully-populated GovernanceProfile describing the agent's
                 current governance posture.

    Returns:
        A GovernanceScoreResult with an overall score, per-dimension breakdowns,
        a certification level, a hosted badge URL, and actionable detail messages.
    """
    trust_score = int(profile.trust_level_coverage_pct) if profile.has_trust_levels else 0
    budget_score = int(profile.budget_coverage_pct) if profile.has_budget_enforcement else 0
    consent_score = int(profile.consent_coverage_pct) if profile.has_consent_management else 0
    audit_score = int(profile.audit_coverage_pct) if profile.has_audit_trail else 0

    linter_score = 100
    if profile.linter_total_checks > 0:
        linter_score = int(
            ((profile.linter_total_checks - profile.linter_warnings) / profile.linter_total_checks)
            * 100
        )

    # Weighted average across the five governance dimensions
    weights: dict[str, float] = {
        "trust": 0.25,
        "budget": 0.20,
        "consent": 0.20,
        "audit": 0.25,
        "linter": 0.10,
    }

    overall = int(
        trust_score * weights["trust"]
        + budget_score * weights["budget"]
        + consent_score * weights["consent"]
        + audit_score * weights["audit"]
        + linter_score * weights["linter"]
    )

    # Bonus for conformance tests and shadow mode
    if profile.has_conformance_tests:
        conformance_bonus: dict[str, int] = {
            "none": 0,
            "basic": 2,
            "standard": 5,
            "full": 10,
        }
        overall = min(100, overall + conformance_bonus.get(profile.conformance_level, 0))

    if profile.has_shadow_mode:
        overall = min(100, overall + 3)

    level = _score_to_level(overall)

    details: list[str] = []
    if trust_score < 50:
        details.append("Low trust level coverage — configure trust levels for more tool calls")
    if budget_score < 50:
        details.append(
            "Low budget coverage — add budget enforcement to spending-heavy operations"
        )
    if consent_score < 50:
        details.append(
            "Low consent coverage — add consent checks for data-sensitive operations"
        )
    if audit_score < 50:
        details.append(
            "Low audit coverage — enable audit logging for compliance evidence"
        )

    return GovernanceScoreResult(
        overall=overall,
        trust_coverage=trust_score,
        budget_coverage=budget_score,
        consent_coverage=consent_score,
        audit_coverage=audit_score,
        linter_score=linter_score,
        level=level,
        badge_url=f"https://badge.aumos.ai/score/{overall}",
        details=details,
    )


def _score_to_level(score: int) -> str:
    """Map a 0-100 governance score to a certification level name.

    Args:
        score: Integer score in [0, 100].

    Returns:
        One of "Platinum", "Gold", "Silver", "Bronze", or "Unrated".
    """
    if score >= 90:
        return "Platinum"
    if score >= 75:
        return "Gold"
    if score >= 50:
        return "Silver"
    if score >= 25:
        return "Bronze"
    return "Unrated"
