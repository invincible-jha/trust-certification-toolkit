# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
Tests for trust-certification-toolkit — types, levels, scorer, and protocol results.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from aumos_certify.levels import (
    LEVELS_DESCENDING,
    LEVEL_DEFINITIONS,
    LevelDefinition,
    get_level_definition,
)
from aumos_certify.scorer import CertificationScorer
from aumos_certify.types import (
    CertificationLevel,
    CertificationResult,
    CheckResult,
    ConformanceStatus,
    ProtocolResult,
    RunResult,
)
from tests.conftest import _make_protocol_result


# ---------------------------------------------------------------------------
# TestProtocolResult
# ---------------------------------------------------------------------------


class TestProtocolResult:
    def test_total_excludes_skips(self) -> None:
        result = ProtocolResult(
            protocol="atp",
            passed=4,
            failed=1,
            skipped=3,
            errors=0,
        )
        assert result.total == 5  # passed + failed + errors

    def test_score_with_all_passing(self) -> None:
        result = ProtocolResult(protocol="atp", passed=5, failed=0)
        assert result.score == 1.0

    def test_score_with_no_checks(self) -> None:
        result = ProtocolResult(protocol="atp", passed=0, failed=0)
        assert result.score == 0.0

    def test_score_partial(self) -> None:
        result = ProtocolResult(protocol="atp", passed=3, failed=1)
        assert abs(result.score - 0.75) < 1e-9


# ---------------------------------------------------------------------------
# TestRunResult
# ---------------------------------------------------------------------------


class TestRunResult:
    def test_overall_score_empty_protocols(self) -> None:
        now = datetime.now(tz=timezone.utc)
        run = RunResult(
            implementation_name="Test",
            run_id="r1",
            started_at=now,
            completed_at=now,
            protocols_run=[],
            protocol_results={},
        )
        assert run.overall_score == 0.0

    def test_overall_score_perfect(self, perfect_run_result: RunResult) -> None:
        assert perfect_run_result.overall_score == 1.0

    def test_overall_score_pct_is_percentage(self, perfect_run_result: RunResult) -> None:
        assert perfect_run_result.overall_score_pct == 100.0


# ---------------------------------------------------------------------------
# TestLevelDefinitions
# ---------------------------------------------------------------------------


class TestLevelDefinitions:
    def test_all_four_levels_defined(self) -> None:
        for level in CertificationLevel:
            assert level in LEVEL_DEFINITIONS

    def test_bronze_minimum_is_60_pct(self) -> None:
        bronze_def = get_level_definition(CertificationLevel.BRONZE)
        assert bronze_def.minimum_score_pct == 60.0

    def test_silver_minimum_is_75_pct(self) -> None:
        silver_def = get_level_definition(CertificationLevel.SILVER)
        assert silver_def.minimum_score_pct == 75.0

    def test_gold_minimum_is_90_pct(self) -> None:
        gold_def = get_level_definition(CertificationLevel.GOLD)
        assert gold_def.minimum_score_pct == 90.0

    def test_platinum_minimum_is_95_pct(self) -> None:
        platinum_def = get_level_definition(CertificationLevel.PLATINUM)
        assert platinum_def.minimum_score_pct == 95.0

    def test_levels_descending_order(self) -> None:
        scores = [ld.minimum_score_pct for ld in LEVELS_DESCENDING]
        assert scores == sorted(scores, reverse=True)

    def test_bronze_requires_atp(self) -> None:
        bronze_def = get_level_definition(CertificationLevel.BRONZE)
        assert "atp" in bronze_def.required_protocols

    def test_gold_requires_five_protocols(self) -> None:
        gold_def = get_level_definition(CertificationLevel.GOLD)
        assert len(gold_def.required_protocols) == 5

    def test_level_definitions_are_frozen(self) -> None:
        bronze_def = get_level_definition(CertificationLevel.BRONZE)
        with pytest.raises((AttributeError, TypeError)):
            bronze_def.minimum_score_pct = 0.0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# TestCertificationScorer
# ---------------------------------------------------------------------------


class TestCertificationScorer:
    def test_perfect_run_achieves_gold_or_above(
        self, perfect_run_result: RunResult
    ) -> None:
        scorer = CertificationScorer()
        result = scorer.score(perfect_run_result)
        assert result.achieved_level is not None
        assert result.achieved_level in (CertificationLevel.GOLD, CertificationLevel.PLATINUM)

    def test_bronze_run_achieves_bronze(self, bronze_run_result: RunResult) -> None:
        scorer = CertificationScorer()
        result = scorer.score(bronze_run_result)
        assert result.achieved_level == CertificationLevel.BRONZE

    def test_below_bronze_threshold_returns_none_level(self) -> None:
        now = datetime.now(tz=timezone.utc)
        # 50% pass rate — below Bronze threshold of 60%
        poor_result = ProtocolResult(
            protocol="atp",
            checks=[
                CheckResult(
                    check_id="atp-must-001",
                    description="MUST check",
                    status=ConformanceStatus.PASS,
                    conformance_level="MUST",
                )
            ],
            passed=1,
            failed=1,
        )
        run = RunResult(
            implementation_name="PoorImpl",
            run_id="r-poor",
            started_at=now,
            completed_at=now,
            protocols_run=["atp"],
            protocol_results={"atp": poor_result},
        )
        scorer = CertificationScorer()
        result = scorer.score(run)
        assert result.achieved_level is None

    def test_missing_required_protocol_prevents_certification(self) -> None:
        now = datetime.now(tz=timezone.utc)
        # 100% but only ran 'atp' — missing other required protocols for Silver
        atp_result = _make_protocol_result("atp", passed=10)
        run = RunResult(
            implementation_name="PartialImpl",
            run_id="r-partial",
            started_at=now,
            completed_at=now,
            protocols_run=["atp"],
            protocol_results={"atp": atp_result},
        )
        scorer = CertificationScorer()
        result = scorer.score(run)
        # Can achieve Bronze but not Silver (missing aeap, aoap)
        assert result.achieved_level == CertificationLevel.BRONZE

    def test_score_pct_is_set_in_result(self, perfect_run_result: RunResult) -> None:
        scorer = CertificationScorer()
        result = scorer.score(perfect_run_result)
        assert result.score_pct == 100.0

    def test_level_detail_contains_all_levels(
        self, perfect_run_result: RunResult
    ) -> None:
        scorer = CertificationScorer()
        result = scorer.score(perfect_run_result)
        for level in CertificationLevel:
            assert level.value in result.level_detail

    def test_protocol_without_must_checks_not_counted(self) -> None:
        now = datetime.now(tz=timezone.utc)
        # Protocol result with only SHOULD-level checks
        should_only = ProtocolResult(
            protocol="atp",
            checks=[
                CheckResult(
                    check_id="atp-should-001",
                    description="SHOULD check",
                    status=ConformanceStatus.PASS,
                    conformance_level="SHOULD",
                )
            ],
            passed=1,
            failed=0,
        )
        run = RunResult(
            implementation_name="ShouldOnlyImpl",
            run_id="r-should",
            started_at=now,
            completed_at=now,
            protocols_run=["atp"],
            protocol_results={"atp": should_only},
        )
        scorer = CertificationScorer()
        result = scorer.score(run)
        # atp protocol with no MUST checks that passed → not satisfied
        assert result.achieved_level is None

    def test_certification_result_has_required_protocols_satisfied_field(
        self, perfect_run_result: RunResult
    ) -> None:
        scorer = CertificationScorer()
        result = scorer.score(perfect_run_result)
        assert isinstance(result.required_protocols_satisfied, bool)
