# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
AIP (Agent Identity Protocol) conformance checks.

Verifies that an implementation satisfies the normative requirements defined
in AIP-001. Checks cover identity registration, credential validation,
and identity lifecycle management.
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
    Run all AIP conformance checks against the provided adapter.

    Returns a ProtocolResult with per-check detail.
    """
    checks: list[CheckResult] = []

    checks.append(await _check_identity_registration(adapter))
    checks.append(await _check_identity_lookup(adapter))
    checks.append(await _check_credential_validation(adapter))
    checks.append(await _check_identity_revocation(adapter))

    passed = sum(1 for c in checks if c.status == ConformanceStatus.PASS)
    failed = sum(1 for c in checks if c.status == ConformanceStatus.FAIL)
    skipped = sum(1 for c in checks if c.status == ConformanceStatus.SKIP)
    errors = sum(1 for c in checks if c.status == ConformanceStatus.ERROR)

    return ProtocolResult(
        protocol="aip",
        checks=checks,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
    )


async def _check_identity_registration(adapter: ImplementationAdapter) -> CheckResult:
    """AIP-MUST-001: Implementation MUST support registering a new agent identity."""
    try:
        response = await adapter.invoke(
            protocol="aip",
            operation="register_identity",
            payload={
                "agent_id": "test-agent-aip-001",
                "public_key": "test-public-key-placeholder",
                "metadata": {"version": "1.0"},
            },
        )
        if response.get("registered") is True and "identity_id" in response:
            return CheckResult(
                check_id="AIP-MUST-001",
                description="Agent identity registration is supported",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="AIP-MUST-001",
            description="Agent identity registration is supported",
            status=ConformanceStatus.FAIL,
            message=f"register_identity returned unexpected response: {response}",
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="AIP-MUST-001",
            description="Agent identity registration is supported",
            status=ConformanceStatus.FAIL,
            message="Operation 'register_identity' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="AIP-MUST-001",
            description="Agent identity registration is supported",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )


async def _check_identity_lookup(adapter: ImplementationAdapter) -> CheckResult:
    """AIP-MUST-002: Implementation MUST support looking up a registered agent identity."""
    try:
        response = await adapter.invoke(
            protocol="aip",
            operation="lookup_identity",
            payload={"agent_id": "test-agent-aip-001"},
        )
        if "identity_id" in response or "agent_id" in response:
            return CheckResult(
                check_id="AIP-MUST-002",
                description="Agent identity lookup is supported",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="AIP-MUST-002",
            description="Agent identity lookup is supported",
            status=ConformanceStatus.FAIL,
            message=f"lookup_identity returned unexpected response: {response}",
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="AIP-MUST-002",
            description="Agent identity lookup is supported",
            status=ConformanceStatus.FAIL,
            message="Operation 'lookup_identity' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="AIP-MUST-002",
            description="Agent identity lookup is supported",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )


async def _check_credential_validation(adapter: ImplementationAdapter) -> CheckResult:
    """AIP-MUST-003: Implementation MUST validate credentials before granting identity claims."""
    try:
        response = await adapter.invoke(
            protocol="aip",
            operation="validate_credential",
            payload={
                "agent_id": "test-agent-aip-001",
                "credential_type": "api_key",
                "credential_value": "invalid-credential-for-test",
            },
        )
        # An invalid credential must be rejected
        if response.get("valid") is False:
            return CheckResult(
                check_id="AIP-MUST-003",
                description="Credential validation rejects invalid credentials",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="AIP-MUST-003",
            description="Credential validation rejects invalid credentials",
            status=ConformanceStatus.FAIL,
            message=(
                "validate_credential should reject an invalid credential, "
                f"but returned: {response}"
            ),
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="AIP-MUST-003",
            description="Credential validation rejects invalid credentials",
            status=ConformanceStatus.FAIL,
            message="Operation 'validate_credential' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="AIP-MUST-003",
            description="Credential validation rejects invalid credentials",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )


async def _check_identity_revocation(adapter: ImplementationAdapter) -> CheckResult:
    """AIP-MUST-004: Implementation MUST support revoking an agent identity."""
    try:
        response = await adapter.invoke(
            protocol="aip",
            operation="revoke_identity",
            payload={
                "agent_id": "test-agent-aip-revoke",
                "reason": "test-revocation",
                "revoked_by": "owner-001",
            },
        )
        if response.get("revoked") is True:
            return CheckResult(
                check_id="AIP-MUST-004",
                description="Agent identity revocation is supported",
                status=ConformanceStatus.PASS,
                conformance_level="MUST",
            )
        return CheckResult(
            check_id="AIP-MUST-004",
            description="Agent identity revocation is supported",
            status=ConformanceStatus.FAIL,
            message=f"revoke_identity returned unexpected response: {response}",
            conformance_level="MUST",
        )
    except NotImplementedError:
        return CheckResult(
            check_id="AIP-MUST-004",
            description="Agent identity revocation is supported",
            status=ConformanceStatus.FAIL,
            message="Operation 'revoke_identity' raised NotImplementedError",
            conformance_level="MUST",
        )
    except Exception as exc:
        return CheckResult(
            check_id="AIP-MUST-004",
            description="Agent identity revocation is supported",
            status=ConformanceStatus.ERROR,
            message=f"Unexpected error: {exc}",
            conformance_level="MUST",
        )
