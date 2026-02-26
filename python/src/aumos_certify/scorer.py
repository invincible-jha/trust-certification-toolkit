# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
CertificationScorer — maps a RunResult to a CertificationResult.

Scoring is deterministic: a level is achieved when the overall pass rate meets
the minimum threshold AND all required protocols for that level were run and passed
their MUST-level checks.
"""

from __future__ import annotations

from aumos_certify.levels import LEVELS_DESCENDING, LevelDefinition
from aumos_certify.types import (
    CertificationLevel,
    CertificationResult,
    ConformanceStatus,
    RunResult,
)


class CertificationScorer:
    """
    Maps a RunResult to a CertificationResult.

    The scoring logic is fully deterministic and matches the publicly documented
    criteria in levels.py. There are no hidden thresholds or adaptive adjustments.
    """

    def score(self, run_result: RunResult) -> CertificationResult:
        """
        Evaluate a RunResult and return the corresponding CertificationResult.

        The highest level whose criteria are fully satisfied is awarded.
        If no level's criteria are met, achieved_level is None.

        Args:
            run_result: The result of a ConformanceRunner.run() call.

        Returns:
            CertificationResult containing the achieved level and supporting detail.
        """
        score_pct = run_result.overall_score_pct
        level_detail = self._build_level_detail(run_result, score_pct)

        achieved_level: CertificationLevel | None = None
        missing_protocols: list[str] = []

        for level_def in LEVELS_DESCENDING:
            passes, missing = self._level_is_satisfied(run_result, score_pct, level_def)
            if passes:
                achieved_level = level_def.level
                missing_protocols = []
                break
            # Track the missing protocols from the highest attempted level for reporting
            if achieved_level is None:
                missing_protocols = missing

        required_protocols_satisfied = len(missing_protocols) == 0 and achieved_level is not None

        return CertificationResult(
            run_result=run_result,
            achieved_level=achieved_level,
            score_pct=score_pct,
            required_protocols_satisfied=required_protocols_satisfied,
            missing_protocols=missing_protocols,
            level_detail=level_detail,
        )

    def _level_is_satisfied(
        self,
        run_result: RunResult,
        score_pct: float,
        level_def: LevelDefinition,
    ) -> tuple[bool, list[str]]:
        """
        Check whether a single level's criteria are met.

        Returns:
            (True, []) if satisfied, or (False, list_of_missing_protocols) if not.
        """
        if score_pct < level_def.minimum_score_pct:
            return False, list(level_def.required_protocols)

        missing: list[str] = []
        for required_protocol in level_def.required_protocols:
            protocol_result = run_result.protocol_results.get(required_protocol)
            if protocol_result is None:
                missing.append(required_protocol)
                continue
            # The protocol must have run at least one MUST check and passed it
            must_checks = [
                c for c in protocol_result.checks if c.conformance_level == "MUST"
            ]
            must_passes = [
                c for c in must_checks if c.status == ConformanceStatus.PASS
            ]
            if not must_checks or len(must_passes) == 0:
                missing.append(required_protocol)

        if missing:
            return False, missing
        return True, []

    def _build_level_detail(
        self,
        run_result: RunResult,
        score_pct: float,
    ) -> dict[str, object]:
        """Build a per-level pass/fail summary for inclusion in the report."""
        detail: dict[str, object] = {}
        for level_def in LEVELS_DESCENDING:
            passes, missing = self._level_is_satisfied(run_result, score_pct, level_def)
            detail[level_def.level.value] = {
                "minimum_score_pct": level_def.minimum_score_pct,
                "actual_score_pct": round(score_pct, 2),
                "score_satisfies_threshold": score_pct >= level_def.minimum_score_pct,
                "required_protocols": list(level_def.required_protocols),
                "missing_protocols": missing,
                "satisfied": passes,
            }
        return detail
