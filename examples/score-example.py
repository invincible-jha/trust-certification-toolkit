# SPDX-License-Identifier: BSL-1.1
# Copyright (c) 2026 MuVeraAI Corporation
"""
score-example.py — Governance score usage example for the AumOS
trust-certification-toolkit.

Demonstrates how to build a GovernanceProfile from real agent metadata and
pass it to compute_governance_score() to obtain a GovernanceScoreResult with
an overall 0-100 score, per-dimension breakdowns, certification level, and a
hosted badge URL.

Run:
    python examples/score-example.py
"""

from __future__ import annotations

import sys
import os

# Allow running this file directly from the repo root without installing the package.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python", "src"))

from governance_score import GovernanceProfile, compute_governance_score


def main() -> None:
    """Run a set of example governance profiles and print their scores."""

    # --- Example 1: Well-governed production agent ---
    production_profile = GovernanceProfile(
        has_trust_levels=True,
        trust_level_coverage_pct=90.0,
        has_budget_enforcement=True,
        budget_coverage_pct=85.0,
        has_consent_management=True,
        consent_coverage_pct=95.0,
        has_audit_trail=True,
        audit_coverage_pct=88.0,
        linter_warnings=2,
        linter_total_checks=100,
        has_conformance_tests=True,
        conformance_level="full",
        has_shadow_mode=True,
    )
    production_result = compute_governance_score(production_profile)
    _print_result("Production agent (well-governed)", production_result)

    # --- Example 2: Early-stage agent with partial governance ---
    early_stage_profile = GovernanceProfile(
        has_trust_levels=True,
        trust_level_coverage_pct=60.0,
        has_budget_enforcement=False,
        budget_coverage_pct=0.0,
        has_consent_management=False,
        consent_coverage_pct=0.0,
        has_audit_trail=True,
        audit_coverage_pct=40.0,
        linter_warnings=15,
        linter_total_checks=100,
        has_conformance_tests=True,
        conformance_level="basic",
        has_shadow_mode=False,
    )
    early_stage_result = compute_governance_score(early_stage_profile)
    _print_result("Early-stage agent (partial governance)", early_stage_result)

    # --- Example 3: Ungoverned agent ---
    ungoverned_profile = GovernanceProfile(
        has_trust_levels=False,
        trust_level_coverage_pct=0.0,
        has_budget_enforcement=False,
        budget_coverage_pct=0.0,
        has_consent_management=False,
        consent_coverage_pct=0.0,
        has_audit_trail=False,
        audit_coverage_pct=0.0,
        linter_warnings=50,
        linter_total_checks=100,
        has_conformance_tests=False,
        conformance_level="none",
        has_shadow_mode=False,
    )
    ungoverned_result = compute_governance_score(ungoverned_profile)
    _print_result("Ungoverned agent", ungoverned_result)


def _print_result(label: str, result: object) -> None:
    """Pretty-print a GovernanceScoreResult."""
    from governance_score import GovernanceScoreResult

    assert isinstance(result, GovernanceScoreResult)

    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print(f"{'=' * 60}")
    print(f"  Overall score  : {result.overall}/100")
    print(f"  Level          : {result.level}")
    print(f"  Badge URL      : {result.badge_url}")
    print(f"  Trust coverage : {result.trust_coverage}/100")
    print(f"  Budget coverage: {result.budget_coverage}/100")
    print(f"  Consent        : {result.consent_coverage}/100")
    print(f"  Audit          : {result.audit_coverage}/100")
    print(f"  Linter score   : {result.linter_score}/100")
    if result.details:
        print("  Recommendations:")
        for detail in result.details:
            print(f"    - {detail}")
    else:
        print("  No recommendations — all dimensions look healthy.")


if __name__ == "__main__":
    main()
