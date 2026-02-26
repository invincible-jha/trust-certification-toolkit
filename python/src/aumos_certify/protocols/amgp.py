# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
AMGP (Agent Memory Governance Protocol) conformance checks.

Verifies that an implementation satisfies the normative requirements defined
in AMGP-001. Checks cover memory record retention policies, deletion
obligations, and consent requirements.
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
    Run all AMGP conformance checks against the provided adapter.

    Returns a ProtocolResult with per-check detail.
    """
    checks: list[CheckResult] = []

    checks.append(await _check_memory_record_write(adapter))
    checks.append(await _check_retention_policy_query(adapter))
    checks.append(await _check_memory_deletion(adapter))
    checks.append(await _check_consent_required_for_retention(adapter))

    passed = sum(1 for c in checks if c.status == ConformanceStatus.PASS)
    failed = sum(1 for c in checks if c.status == ConformanceStatus.FAIL)
    skipped = sum(1 for c in checks if c.status == ConformanceStatus.SKIP)
    errors = sum(1 for c in checks if c.status == ConformanceStatus.ERROR)

    return ProtocolResult(
        protocol="amgp",
        checks=checks,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
    )


async def _check_memory_record_write(adapter: ImplementationAdapter) -> CheckResult:
    """AMGP-MUST-001: Implementation MUST support writing a memory record."""
    try:
        response = await adapter.invoke(
            protocol="amgp",
            operation="write_memory_record",
            payload={
                "agent_id": "test-agent-amgp-001",
                "record_type": "observation",
                "content": {"data": "test-memory-content"},
                "retention_policy": "session",
            },
        )
        if response.get("written") is True and "record_id" in response:
            return CheckResult(
                check_id="AMGP-MUST-001",
                description="Memory record writing with retention policy is supported",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="AMGP-MUST-001",
            description="Memory record writing with retention policy is supported",
            status=ConformanceStatus.FAIL,
            message=f"write_memory_record must return written=true and record_id. Got: {response}",
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="AMGP-MUST-001",
            description="Memory record writing with retention policy is supported",
            status=ConformanceStatus.FAIL,
            message="Operation 'write_memory_record' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="AMGP-MUST-001",
            description="Memory record writing with retention policy is supported",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )


async def _check_retention_policy_query(adapter: ImplementationAdapter) -> CheckResult:
    """AMGP-MUST-002: Implementation MUST support querying records by retention policy."""
    try:
        response = await adapter.invoke(
            protocol="amgp",
            operation="query_memory_records",
            payload={
                "agent_id": "test-agent-amgp-001",
                "retention_policy": "session",
            },
        )
        if "records" in response and isinstance(response["records"], list):
            return CheckResult(
                check_id="AMGP-MUST-002",
                description="Memory records can be queried by retention policy",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="AMGP-MUST-002",
            description="Memory records can be queried by retention policy",
            status=ConformanceStatus.FAIL,
            message=f"query_memory_records must return a 'records' list. Got: {response}",
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="AMGP-MUST-002",
            description="Memory records can be queried by retention policy",
            status=ConformanceStatus.FAIL,
            message="Operation 'query_memory_records' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="AMGP-MUST-002",
            description="Memory records can be queried by retention policy",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )


async def _check_memory_deletion(adapter: ImplementationAdapter) -> CheckResult:
    """AMGP-MUST-003: Implementation MUST support deleting memory records on request."""
    try:
        response = await adapter.invoke(
            protocol="amgp",
            operation="delete_memory_record",
            payload={
                "record_id": "test-record-amgp-delete",
                "requested_by": "owner-001",
            },
        )
        if response.get("deleted") is True:
            return CheckResult(
                check_id="AMGP-MUST-003",
                description="Memory record deletion is supported",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="AMGP-MUST-003",
            description="Memory record deletion is supported",
            status=ConformanceStatus.FAIL,
            message=f"delete_memory_record must return deleted=true. Got: {response}",
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="AMGP-MUST-003",
            description="Memory record deletion is supported",
            status=ConformanceStatus.FAIL,
            message="Operation 'delete_memory_record' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="AMGP-MUST-003",
            description="Memory record deletion is supported",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )


async def _check_consent_required_for_retention(adapter: ImplementationAdapter) -> CheckResult:
    """AMGP-SHOULD-001: Implementations SHOULD enforce consent before long-term retention."""
    try:
        response = await adapter.invoke(
            protocol="amgp",
            operation="write_memory_record",
            payload={
                "agent_id": "test-agent-amgp-001",
                "record_type": "observation",
                "content": {"data": "test-long-term-content"},
                "retention_policy": "long_term",
                "consent_token": None,
            },
        )
        # Without consent, long-term retention should be refused
        if response.get("written") is False and "consent" in str(response).lower():
            return CheckResult(
                check_id="AMGP-SHOULD-001",
                description="Long-term retention requires a consent token",
                status=ConformanceStatus.PASS,
                conformance_level="SHOULD",
            )
        # If it simply succeeds or has a different model, skip gracefully
        return CheckResult(
            check_id="AMGP-SHOULD-001",
            description="Long-term retention requires a consent token",
            status=ConformanceStatus.SKIP,
            message=(
                "Implementation did not enforce consent for long-term retention "
                "(SHOULD, not MUST). Consider adding consent enforcement."
            ),
            conformance_level="SHOULD",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="AMGP-SHOULD-001",
            description="Long-term retention requires a consent token",
            status=ConformanceStatus.SKIP,
            message="Operation not implemented (SHOULD, not MUST)",
            conformance_level="SHOULD",
        )
    except Exception as exc:
        return CheckResult(
            check_id="AMGP-SHOULD-001",
            description="Long-term retention requires a consent token",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="SHOULD",
        )
