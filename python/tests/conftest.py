# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""Shared fixtures for trust-certification-toolkit tests."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from aumos_certify.types import (
    CertificationLevel,
    CheckResult,
    ConformanceStatus,
    ProtocolResult,
    RunResult,
)


def _make_protocol_result(
    protocol: str,
    passed: int = 5,
    failed: int = 0,
    skipped: int = 0,
    errors: int = 0,
    include_must_pass: bool = True,
) -> ProtocolResult:
    checks: list[CheckResult] = []
    if include_must_pass:
        checks.append(
            CheckResult(
                check_id=f"{protocol}-must-001",
                description=f"MUST check for {protocol}",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        )
    for i in range(passed - (1 if include_must_pass else 0)):
        checks.append(
            CheckResult(
                check_id=f"{protocol}-check-{i:03d}",
                description=f"Check {i} for {protocol}",
                status=ConformanceStatus.PASS,
            )
        )
    for i in range(failed):
        checks.append(
            CheckResult(
                check_id=f"{protocol}-fail-{i:03d}",
                description=f"Failing check {i}",
                status=ConformanceStatus.FAIL,
            )
        )
    return ProtocolResult(
        protocol=protocol,
        checks=checks,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
    )


@pytest.fixture
def now() -> datetime:
    return datetime.now(tz=timezone.utc)


@pytest.fixture
def perfect_run_result(now: datetime) -> RunResult:
    """RunResult with 100% pass rate across atp, aip, aeap, amgp, aoap."""
    protocols = ["atp", "aip", "aeap", "amgp", "aoap"]
    protocol_results = {p: _make_protocol_result(p, passed=5) for p in protocols}
    return RunResult(
        implementation_name="TestImpl",
        run_id="run-001",
        started_at=now,
        completed_at=now,
        protocols_run=protocols,
        protocol_results=protocol_results,
    )


@pytest.fixture
def bronze_run_result(now: datetime) -> RunResult:
    """RunResult with ~65% pass rate — qualifies for Bronze only."""
    protocol_results = {
        "atp": _make_protocol_result("atp", passed=4, failed=2),
    }
    return RunResult(
        implementation_name="BronzeImpl",
        run_id="run-bronze",
        started_at=now,
        completed_at=now,
        protocols_run=["atp"],
        protocol_results=protocol_results,
    )
