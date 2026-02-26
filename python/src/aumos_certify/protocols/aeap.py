# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
AEAP (Agent Economic Action Protocol) conformance checks.

Verifies that an implementation satisfies the normative requirements defined
in AEAP-001. All budget limits checked here are static — no adaptive or
ML-based allocation is tested or expected.
"""

from __future__ import annotations

from aumos_certify.types import (
    CheckResult,
    ConformanceStatus,
    ImplementationAdapter,
    ProtocolResult,
)


async def run_checks(adapter: ImplementationAdapter) -> ProtocolResult:
    """
    Run all AEAP conformance checks against the provided adapter.

    Returns a ProtocolResult with per-check detail.
    """
    checks: list[CheckResult] = []

    checks.append(await _check_budget_limit_enforcement(adapter))
    checks.append(await _check_spend_recording(adapter))
    checks.append(await _check_budget_query(adapter))
    checks.append(await _check_spend_exceeds_limit(adapter))

    passed = sum(1 for c in checks if c.status == ConformanceStatus.PASS)
    failed = sum(1 for c in checks if c.status == ConformanceStatus.FAIL)
    skipped = sum(1 for c in checks if c.status == ConformanceStatus.SKIP)
    errors = sum(1 for c in checks if c.status == ConformanceStatus.ERROR)

    return ProtocolResult(
        protocol="aeap",
        checks=checks,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
    )


async def _check_budget_limit_enforcement(adapter: ImplementationAdapter) -> CheckResult:
    """AEAP-MUST-001: Implementation MUST enforce a static spend limit per period."""
    try:
        response = await adapter.invoke(
            protocol="aeap",
            operation="check_spend_allowed",
            payload={
                "agent_id": "test-agent-aeap-001",
                "amount": 100,
                "currency": "USD",
                "period": "daily",
            },
        )
        if "allowed" in response:
            return CheckResult(
                check_id="AEAP-MUST-001",
                description="Static spend limit enforcement is supported",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="AEAP-MUST-001",
            description="Static spend limit enforcement is supported",
            status=ConformanceStatus.FAIL,
            message=f"check_spend_allowed must return 'allowed' field. Got: {response}",
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="AEAP-MUST-001",
            description="Static spend limit enforcement is supported",
            status=ConformanceStatus.FAIL,
            message="Operation 'check_spend_allowed' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="AEAP-MUST-001",
            description="Static spend limit enforcement is supported",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )


async def _check_spend_recording(adapter: ImplementationAdapter) -> CheckResult:
    """AEAP-MUST-002: Implementation MUST record each spend event."""
    try:
        response = await adapter.invoke(
            protocol="aeap",
            operation="record_spend",
            payload={
                "agent_id": "test-agent-aeap-001",
                "amount": 10,
                "currency": "USD",
                "description": "test-spend-event",
            },
        )
        if response.get("recorded") is True and "spend_id" in response:
            return CheckResult(
                check_id="AEAP-MUST-002",
                description="Spend events are recorded with a unique identifier",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="AEAP-MUST-002",
            description="Spend events are recorded with a unique identifier",
            status=ConformanceStatus.FAIL,
            message=f"record_spend must return recorded=true and spend_id. Got: {response}",
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="AEAP-MUST-002",
            description="Spend events are recorded with a unique identifier",
            status=ConformanceStatus.FAIL,
            message="Operation 'record_spend' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="AEAP-MUST-002",
            description="Spend events are recorded with a unique identifier",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )


async def _check_budget_query(adapter: ImplementationAdapter) -> CheckResult:
    """AEAP-MUST-003: Implementation MUST support querying remaining budget."""
    try:
        response = await adapter.invoke(
            protocol="aeap",
            operation="get_budget_status",
            payload={"agent_id": "test-agent-aeap-001", "period": "daily"},
        )
        if "remaining" in response and "limit" in response:
            return CheckResult(
                check_id="AEAP-MUST-003",
                description="Budget status query returns remaining and limit fields",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="AEAP-MUST-003",
            description="Budget status query returns remaining and limit fields",
            status=ConformanceStatus.FAIL,
            message=f"get_budget_status must return 'remaining' and 'limit'. Got: {response}",
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="AEAP-MUST-003",
            description="Budget status query returns remaining and limit fields",
            status=ConformanceStatus.FAIL,
            message="Operation 'get_budget_status' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="AEAP-MUST-003",
            description="Budget status query returns remaining and limit fields",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )


async def _check_spend_exceeds_limit(adapter: ImplementationAdapter) -> CheckResult:
    """AEAP-MUST-004: Implementation MUST deny spend requests that exceed the static limit."""
    try:
        # Request a spend far above any reasonable limit
        response = await adapter.invoke(
            protocol="aeap",
            operation="check_spend_allowed",
            payload={
                "agent_id": "test-agent-aeap-001",
                "amount": 999_999_999,
                "currency": "USD",
                "period": "daily",
            },
        )
        if response.get("allowed") is False:
            return CheckResult(
                check_id="AEAP-MUST-004",
                description="Spend requests exceeding the static limit are denied",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="AEAP-MUST-004",
            description="Spend requests exceeding the static limit are denied",
            status=ConformanceStatus.FAIL,
            message=(
                "check_spend_allowed should deny an amount of 999999999, "
                f"but returned: {response}"
            ),
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="AEAP-MUST-004",
            description="Spend requests exceeding the static limit are denied",
            status=ConformanceStatus.FAIL,
            message="Operation 'check_spend_allowed' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="AEAP-MUST-004",
            description="Spend requests exceeding the static limit are denied",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )
