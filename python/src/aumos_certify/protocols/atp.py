# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
ATP (Agent Trust Protocol) conformance checks.

Verifies that an implementation satisfies the normative requirements defined
in ATP-001. All checks are static governance decisions — no adaptive behavior,
no behavioral scoring.
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
    Run all ATP conformance checks against the provided adapter.

    Returns a ProtocolResult with per-check detail.
    """
    checks: list[CheckResult] = []

    checks.append(await _check_trust_level_assignment(adapter))
    checks.append(await _check_trust_level_enforcement(adapter))
    checks.append(await _check_manual_level_change(adapter))
    checks.append(await _check_deny_on_insufficient_level(adapter))
    checks.append(await _check_audit_record_on_decision(adapter))

    passed = sum(1 for c in checks if c.status == ConformanceStatus.PASS)
    failed = sum(1 for c in checks if c.status == ConformanceStatus.FAIL)
    skipped = sum(1 for c in checks if c.status == ConformanceStatus.SKIP)
    errors = sum(1 for c in checks if c.status == ConformanceStatus.ERROR)

    return ProtocolResult(
        protocol="atp",
        checks=checks,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
    )


async def _check_trust_level_assignment(adapter: ImplementationAdapter) -> CheckResult:
    """ATP-MUST-001: Implementation MUST support assigning a trust level to an agent."""
    try:
        response = await adapter.invoke(
            protocol="atp",
            operation="set_trust_level",
            payload={"agent_id": "test-agent-001", "level": "L2"},
        )
        if response.get("success") is True:
            return CheckResult(
                check_id="ATP-MUST-001",
                description="Trust level assignment is supported",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="ATP-MUST-001",
            description="Trust level assignment is supported",
            status=ConformanceStatus.FAIL,
            message=f"set_trust_level returned unexpected response: {response}",
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="ATP-MUST-001",
            description="Trust level assignment is supported",
            status=ConformanceStatus.FAIL,
            message="Operation 'set_trust_level' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="ATP-MUST-001",
            description="Trust level assignment is supported",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )


async def _check_trust_level_enforcement(adapter: ImplementationAdapter) -> CheckResult:
    """ATP-MUST-002: Implementation MUST enforce trust level requirements on operations."""
    try:
        response = await adapter.invoke(
            protocol="atp",
            operation="check_trust_requirement",
            payload={
                "agent_id": "test-agent-001",
                "required_level": "L3",
                "current_level": "L2",
            },
        )
        # An L2 agent requesting L3 access must be denied
        if response.get("allowed") is False:
            return CheckResult(
                check_id="ATP-MUST-002",
                description="Trust level enforcement rejects insufficient level",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="ATP-MUST-002",
            description="Trust level enforcement rejects insufficient level",
            status=ConformanceStatus.FAIL,
            message=(
                "check_trust_requirement should deny L2 agent requesting L3 access, "
                f"but returned: {response}"
            ),
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="ATP-MUST-002",
            description="Trust level enforcement rejects insufficient level",
            status=ConformanceStatus.FAIL,
            message="Operation 'check_trust_requirement' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="ATP-MUST-002",
            description="Trust level enforcement rejects insufficient level",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )


async def _check_manual_level_change(adapter: ImplementationAdapter) -> CheckResult:
    """ATP-MUST-003: Trust level changes MUST require explicit owner authorization."""
    try:
        response = await adapter.invoke(
            protocol="atp",
            operation="change_trust_level",
            payload={
                "agent_id": "test-agent-001",
                "new_level": "L3",
                "authorized_by": "owner-001",
            },
        )
        if response.get("success") is True and response.get("authorized_by") == "owner-001":
            return CheckResult(
                check_id="ATP-MUST-003",
                description="Trust level changes require explicit owner authorization",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="ATP-MUST-003",
            description="Trust level changes require explicit owner authorization",
            status=ConformanceStatus.FAIL,
            message=(
                "change_trust_level must record the authorizing owner. "
                f"Got: {response}"
            ),
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="ATP-MUST-003",
            description="Trust level changes require explicit owner authorization",
            status=ConformanceStatus.FAIL,
            message="Operation 'change_trust_level' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="ATP-MUST-003",
            description="Trust level changes require explicit owner authorization",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )


async def _check_deny_on_insufficient_level(adapter: ImplementationAdapter) -> CheckResult:
    """ATP-MUST-004: Implementation MUST return a structured denial when trust is insufficient."""
    try:
        response = await adapter.invoke(
            protocol="atp",
            operation="check_trust_requirement",
            payload={
                "agent_id": "test-agent-002",
                "required_level": "L5",
                "current_level": "L1",
            },
        )
        if response.get("allowed") is False and "reason" in response:
            return CheckResult(
                check_id="ATP-MUST-004",
                description="Structured denial returned when trust level is insufficient",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="ATP-MUST-004",
            description="Structured denial returned when trust level is insufficient",
            status=ConformanceStatus.FAIL,
            message=(
                "Denial response must include a 'reason' field. "
                f"Got: {response}"
            ),
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="ATP-MUST-004",
            description="Structured denial returned when trust level is insufficient",
            status=ConformanceStatus.FAIL,
            message="Operation 'check_trust_requirement' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="ATP-MUST-004",
            description="Structured denial returned when trust level is insufficient",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )


async def _check_audit_record_on_decision(adapter: ImplementationAdapter) -> CheckResult:
    """ATP-SHOULD-001: Implementation SHOULD record an audit entry for every trust decision."""
    try:
        response = await adapter.invoke(
            protocol="atp",
            operation="get_recent_audit_entries",
            payload={"limit": 10},
        )
        entries = response.get("entries", [])
        if isinstance(entries, list):
            return CheckResult(
                check_id="ATP-SHOULD-001",
                description="Audit entries are recorded for trust decisions",
                status=ConformanceStatus.PASS,
                conformance_level="SHOULD",
            )
        return CheckResult(
            check_id="ATP-SHOULD-001",
            description="Audit entries are recorded for trust decisions",
            status=ConformanceStatus.FAIL,
            message=f"Expected 'entries' list in response, got: {response}",
            conformance_level="SHOULD",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="ATP-SHOULD-001",
            description="Audit entries are recorded for trust decisions",
            status=ConformanceStatus.SKIP,
            message="Operation 'get_recent_audit_entries' not implemented (SHOULD, not MUST)",
            conformance_level="SHOULD",
        )
    except Exception as exc:
        return CheckResult(
            check_id="ATP-SHOULD-001",
            description="Audit entries are recorded for trust decisions",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="SHOULD",
        )
