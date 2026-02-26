# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
Certification level definitions for the AumOS Certified badge program.

All thresholds and required protocol lists are publicly documented here.
There are no secret criteria.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from aumos_certify.types import CertificationLevel


@dataclass(frozen=True)
class LevelDefinition:
    """Definition of a single certification level."""

    level: CertificationLevel
    minimum_score_pct: float
    required_protocols: tuple[str, ...]
    badge_color: str
    display_name: str
    description: str


# Publicly documented certification level definitions.
# These are the complete, unambiguous criteria — no hidden requirements.
LEVEL_DEFINITIONS: dict[CertificationLevel, LevelDefinition] = {
    CertificationLevel.BRONZE: LevelDefinition(
        level=CertificationLevel.BRONZE,
        minimum_score_pct=60.0,
        required_protocols=("atp",),
        badge_color="#CD7F32",
        display_name="AumOS Certified — Bronze (Self-Assessed)",
        description=(
            "Implementation satisfies at least 60% of all conformance checks "
            "and covers the Agent Trust Protocol (ATP) requirements."
        ),
    ),
    CertificationLevel.SILVER: LevelDefinition(
        level=CertificationLevel.SILVER,
        minimum_score_pct=75.0,
        required_protocols=("atp", "aeap", "aoap"),
        badge_color="#C0C0C0",
        display_name="AumOS Certified — Silver (Self-Assessed)",
        description=(
            "Implementation satisfies at least 75% of all conformance checks "
            "and covers ATP, AEAP, and AOAP requirements."
        ),
    ),
    CertificationLevel.GOLD: LevelDefinition(
        level=CertificationLevel.GOLD,
        minimum_score_pct=90.0,
        required_protocols=("atp", "aip", "aeap", "amgp", "aoap"),
        badge_color="#FFD700",
        display_name="AumOS Certified — Gold (Self-Assessed)",
        description=(
            "Implementation satisfies at least 90% of all conformance checks "
            "and covers ATP, AIP, AEAP, AMGP, and AOAP requirements."
        ),
    ),
    CertificationLevel.PLATINUM: LevelDefinition(
        level=CertificationLevel.PLATINUM,
        minimum_score_pct=95.0,
        required_protocols=("atp", "aip", "asp", "aeap", "amgp", "aoap", "alcp"),
        badge_color="#E5E4E2",
        display_name="AumOS Certified — Platinum (Self-Assessed)",
        description=(
            "Implementation satisfies at least 95% of all conformance checks "
            "and covers all seven AumOS governance protocols."
        ),
    ),
}

# Ordered from highest to lowest for scorer iteration
LEVELS_DESCENDING: list[LevelDefinition] = [
    LEVEL_DEFINITIONS[CertificationLevel.PLATINUM],
    LEVEL_DEFINITIONS[CertificationLevel.GOLD],
    LEVEL_DEFINITIONS[CertificationLevel.SILVER],
    LEVEL_DEFINITIONS[CertificationLevel.BRONZE],
]

# All recognised protocol identifiers
ALL_PROTOCOL_IDS: tuple[str, ...] = ("atp", "aip", "asp", "aeap", "amgp", "aoap", "alcp")


def get_level_definition(level: CertificationLevel) -> LevelDefinition:
    """Return the definition for a given certification level."""
    return LEVEL_DEFINITIONS[level]
