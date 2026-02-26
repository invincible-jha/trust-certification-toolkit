# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
AOAP (Agent Observability and Accountability Protocol) conformance checks.

Verifies that an implementation satisfies the normative requirements defined
in AOAP-001. Audit logging is RECORDING ONLY — these checks do not test
or expect anomaly detection or counterfactual generation.
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
    Run all AOAP conformance checks against the provided adapter.

    Returns a ProtocolResult with per-check detail.
    """
    checks: list[CheckResult] = []

    checks.append(await _check_audit_log_append(adapter))
    checks.append(await _check_audit_log_export(adapter))
    checks.append(await _check_audit_log_integrity(adapter))
    checks.append(await _check_audit_log_query(adapter))

    passed = sum(1 for c in checks if c.status == ConformanceStatus.PASS)
    failed = sum(1 for c in checks if c.status == ConformanceStatus.FAIL)
    skipped = sum(1 for c in checks if c.status == ConformanceStatus.SKIP)
    errors = sum(1 for c in checks if c.status == ConformanceStatus.ERROR)

    return ProtocolResult(
        protocol="aoap",
        checks=checks,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
    )


async def _check_audit_log_append(adapter: ImplementationAdapter) -> CheckResult:
    """AOAP-MUST-001: Implementation MUST support appending to the audit log."""
    try:
        response = await adapter.invoke(
            protocol="aoap",
            operation="append_audit_entry",
            payload={
                "agent_id": "test-agent-aoap-001",
                "event_type": "tool_call",
                "decision": "allow",
                "context": {"tool": "read_file", "path": "/tmp/test"},
            },
        )
        if response.get("appended") is True and "entry_id" in response:
            return CheckResult(
                check_id="AOAP-MUST-001",
                description="Audit log append is supported with entry identifier",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="AOAP-MUST-001",
            description="Audit log append is supported with entry identifier",
            status=ConformanceStatus.FAIL,
            message=f"append_audit_entry must return appended=true and entry_id. Got: {response}",
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="AOAP-MUST-001",
            description="Audit log append is supported with entry identifier",
            status=ConformanceStatus.FAIL,
            message="Operation 'append_audit_entry' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="AOAP-MUST-001",
            description="Audit log append is supported with entry identifier",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )


async def _check_audit_log_export(adapter: ImplementationAdapter) -> CheckResult:
    """AOAP-MUST-002: Implementation MUST support exporting the audit log as JSON."""
    try:
        response = await adapter.invoke(
            protocol="aoap",
            operation="export_audit_log",
            payload={"format": "json", "agent_id": "test-agent-aoap-001"},
        )
        if "entries" in response and isinstance(response["entries"], list):
            return CheckResult(
                check_id="AOAP-MUST-002",
                description="Audit log JSON export is supported",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="AOAP-MUST-002",
            description="Audit log JSON export is supported",
            status=ConformanceStatus.FAIL,
            message=f"export_audit_log must return an 'entries' list. Got: {response}",
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="AOAP-MUST-002",
            description="Audit log JSON export is supported",
            status=ConformanceStatus.FAIL,
            message="Operation 'export_audit_log' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="AOAP-MUST-002",
            description="Audit log JSON export is supported",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )


async def _check_audit_log_integrity(adapter: ImplementationAdapter) -> CheckResult:
    """AOAP-SHOULD-001: Implementations SHOULD support offline integrity verification."""
    try:
        response = await adapter.invoke(
            protocol="aoap",
            operation="verify_audit_chain",
            payload={"agent_id": "test-agent-aoap-001"},
        )
        if "valid" in response:
            return CheckResult(
                check_id="AOAP-SHOULD-001",
                description="Offline audit log integrity verification is supported",
                status=ConformanceStatus.PASS,
                conformance_level="SHOULD",
            )
        return CheckResult(
            check_id="AOAP-SHOULD-001",
            description="Offline audit log integrity verification is supported",
            status=ConformanceStatus.SKIP,
            message=(
                "verify_audit_chain did not return a 'valid' field "
                "(SHOULD, not MUST). Consider adding hash-chain integrity."
            ),
            conformance_level="SHOULD",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="AOAP-SHOULD-001",
            description="Offline audit log integrity verification is supported",
            status=ConformanceStatus.SKIP,
            message="Operation not implemented (SHOULD, not MUST)",
            conformance_level="SHOULD",
        )
    except Exception as exc:
        return CheckResult(
            check_id="AOAP-SHOULD-001",
            description="Offline audit log integrity verification is supported",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="SHOULD",
        )


async def _check_audit_log_query(adapter: ImplementationAdapter) -> CheckResult:
    """AOAP-MUST-003: Implementation MUST support querying audit entries by event type."""
    try:
        response = await adapter.invoke(
            protocol="aoap",
            operation="query_audit_entries",
            payload={
                "agent_id": "test-agent-aoap-001",
                "event_type": "tool_call",
            },
        )
        if "entries" in response and isinstance(response["entries"], list):
            return CheckResult(
                check_id="AOAP-MUST-003",
                description="Audit log query by event type is supported",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="AOAP-MUST-003",
            description="Audit log query by event type is supported",
            status=ConformanceStatus.FAIL,
            message=f"query_audit_entries must return an 'entries' list. Got: {response}",
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="AOAP-MUST-003",
            description="Audit log query by event type is supported",
            status=ConformanceStatus.FAIL,
            message="Operation 'query_audit_entries' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="AOAP-MUST-003",
            description="Audit log query by event type is supported",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )
