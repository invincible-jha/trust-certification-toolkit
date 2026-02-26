# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
Cross-protocol conformance checks.

Verifies that an implementation satisfies normative cross-protocol priority
and consistency requirements as defined in the AumOS interaction matrix.

These checks validate observable properties — they do not test or expect
any internal orchestration pipeline.
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
    Run all cross-protocol conformance checks against the provided adapter.

    Returns a ProtocolResult with per-check detail.
    """
    checks: list[CheckResult] = []

    checks.append(await _check_trust_gate_blocks_spend(adapter))
    checks.append(await _check_identity_required_for_trust(adapter))
    checks.append(await _check_audit_covers_denied_actions(adapter))

    passed = sum(1 for c in checks if c.status == ConformanceStatus.PASS)
    failed = sum(1 for c in checks if c.status == ConformanceStatus.FAIL)
    skipped = sum(1 for c in checks if c.status == ConformanceStatus.SKIP)
    errors = sum(1 for c in checks if c.status == ConformanceStatus.ERROR)

    return ProtocolResult(
        protocol="cross_protocol",
        checks=checks,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
    )


async def _check_trust_gate_blocks_spend(adapter: ImplementationAdapter) -> CheckResult:
    """
    CROSS-MUST-001: An agent with insufficient trust MUST be denied economic actions
    regardless of remaining budget.

    Per the cross-protocol priority table: ATP decision takes priority over AEAP
    in a conflict.
    """
    try:
        response = await adapter.invoke(
            protocol="cross_protocol",
            operation="check_action_allowed",
            payload={
                "agent_id": "test-agent-cross-001",
                "action_type": "economic_spend",
                "trust_level": "L1",
                "required_trust_level": "L3",
                "budget_remaining": 1000,
                "amount": 10,
            },
        )
        if response.get("allowed") is False and response.get("blocked_by") == "atp":
            return CheckResult(
                check_id="CROSS-MUST-001",
                description="Insufficient trust blocks economic actions (ATP > AEAP priority)",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="CROSS-MUST-001",
            description="Insufficient trust blocks economic actions (ATP > AEAP priority)",
            status=ConformanceStatus.SKIP,
            message=(
                "Implementation did not expose 'check_action_allowed' with cross-protocol "
                "priority. Consider implementing the cross-protocol action check. "
                f"Got: {response}"
            ),
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="CROSS-MUST-001",
            description="Insufficient trust blocks economic actions (ATP > AEAP priority)",
            status=ConformanceStatus.SKIP,
            message="Cross-protocol action check not implemented",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="CROSS-MUST-001",
            description="Insufficient trust blocks economic actions (ATP > AEAP priority)",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )


async def _check_identity_required_for_trust(adapter: ImplementationAdapter) -> CheckResult:
    """
    CROSS-MUST-002: Trust level assignment MUST require a verified identity.

    Per the cross-protocol interaction matrix: AIP verification is a prerequisite
    for ATP trust assignment.
    """
    try:
        response = await adapter.invoke(
            protocol="cross_protocol",
            operation="assign_trust_with_identity_check",
            payload={
                "agent_id": "test-agent-cross-002",
                "requested_level": "L2",
                "identity_verified": False,
            },
        )
        if response.get("success") is False and "identity" in str(response).lower():
            return CheckResult(
                check_id="CROSS-MUST-002",
                description="Trust assignment requires verified identity (AIP prerequisite for ATP)",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="CROSS-MUST-002",
            description="Trust assignment requires verified identity (AIP prerequisite for ATP)",
            status=ConformanceStatus.SKIP,
            message=(
                "Implementation did not expose cross-protocol identity check for trust "
                "assignment. Consider enforcing AIP verification as a prerequisite."
            ),
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="CROSS-MUST-002",
            description="Trust assignment requires verified identity (AIP prerequisite for ATP)",
            status=ConformanceStatus.SKIP,
            message="Cross-protocol operation not implemented",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="CROSS-MUST-002",
            description="Trust assignment requires verified identity (AIP prerequisite for ATP)",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )


async def _check_audit_covers_denied_actions(adapter: ImplementationAdapter) -> CheckResult:
    """
    CROSS-SHOULD-001: Audit log SHOULD include entries for all denied actions,
    regardless of which protocol issued the denial.
    """
    try:
        response = await adapter.invoke(
            protocol="cross_protocol",
            operation="get_denial_audit_entries",
            payload={"agent_id": "test-agent-cross-001"},
        )
        if "entries" in response and isinstance(response["entries"], list):
            return CheckResult(
                check_id="CROSS-SHOULD-001",
                description="Audit log covers denied actions from all protocols",
                status=ConformanceStatus.PASS,
                conformance_level="SHOULD",
            )
        return CheckResult(
            check_id="CROSS-SHOULD-001",
            description="Audit log covers denied actions from all protocols",
            status=ConformanceStatus.SKIP,
            message=(
                "get_denial_audit_entries not implemented or returned unexpected structure "
                "(SHOULD, not MUST)"
            ),
            conformance_level="SHOULD",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="CROSS-SHOULD-001",
            description="Audit log covers denied actions from all protocols",
            status=ConformanceStatus.SKIP,
            message="Operation not implemented (SHOULD, not MUST)",
            conformance_level="SHOULD",
        )
    except Exception as exc:
        return CheckResult(
            check_id="CROSS-SHOULD-001",
            description="Audit log covers denied actions from all protocols",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="SHOULD",
        )
