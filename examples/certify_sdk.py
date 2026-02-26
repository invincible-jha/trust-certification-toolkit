# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
certify_sdk.py — Example: run AumOS certification checks against a mock implementation.

This script demonstrates the full self-assessment workflow using aumos-certify:

1. Implement ImplementationAdapter over a mock in-memory system.
2. Run conformance checks for a target set of protocols.
3. Score the run to determine the achieved certification level.
4. Print a summary report to stdout.

Run from the repository root after installing the package:

    cd python/
    pip install -e ".[dev]"
    python ../examples/certify_sdk.py

No network calls are made. All operations are local and offline.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

from aumos_certify.runner import ConformanceRunner
from aumos_certify.scorer import CertificationScorer
from aumos_certify.types import ImplementationAdapter


# ---------------------------------------------------------------------------
# Mock implementation
#
# MockAgentSystem is a minimal in-memory implementation that satisfies the
# MUST-level checks for ATP, AIP, AEAP, and AOAP. It intentionally does not
# implement ASP, ALCP, or the cross-protocol operations so the example
# demonstrates a realistic partial implementation (targeting Silver level).
# ---------------------------------------------------------------------------


class MockAgentSystem(ImplementationAdapter):
    """
    Minimal in-memory agent governance system used as a conformance target.

    Trust levels and budget limits are static — set once by the owner, never
    modified automatically. The implementation deliberately excludes adaptive
    logic to stay within the open-source IP boundary.
    """

    def __init__(self) -> None:
        self._trust_levels: dict[str, str] = {}
        self._audit_log: list[dict[str, Any]] = []
        self._identity_registry: dict[str, dict[str, Any]] = {}
        self._spend_ledger: list[dict[str, Any]] = []
        self._memory_records: dict[str, dict[str, Any]] = {}

        # Static spend limit per agent per period — set by the owner, never computed
        self._spend_limit_usd: float = 500.0

    def get_implementation_name(self) -> str:
        return "MockAgentSystem v0.1.0 (example)"

    async def setup(self) -> None:
        # Seed a well-known agent so lookup checks pass without prior registration
        self._trust_levels["test-agent-001"] = "L2"
        self._identity_registry["test-agent-aip-001"] = {
            "identity_id": "iid-test-aip-001",
            "agent_id": "test-agent-aip-001",
            "public_key": "test-public-key-placeholder",
            "status": "active",
        }

    async def teardown(self) -> None:
        # No external resources to release in the mock
        pass

    # ------------------------------------------------------------------
    # Router
    # ------------------------------------------------------------------

    async def invoke(
        self,
        protocol: str,
        operation: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Dispatch a protocol operation to the appropriate handler."""
        handler_name = f"_handle_{protocol}_{operation}"
        handler = getattr(self, handler_name, None)
        if handler is None:
            raise NotImplementedError(
                f"Operation '{operation}' is not implemented for protocol '{protocol}'"
            )
        return await handler(payload)

    # ------------------------------------------------------------------
    # ATP — Agent Trust Protocol
    # ------------------------------------------------------------------

    async def _handle_atp_set_trust_level(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        agent_id: str = payload["agent_id"]
        level: str = payload["level"]
        self._trust_levels[agent_id] = level
        self._audit_log.append(
            {"event": "set_trust_level", "agent_id": agent_id, "level": level}
        )
        return {"success": True}

    async def _handle_atp_check_trust_requirement(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        agent_id: str = payload["agent_id"]
        required_level: str = payload["required_level"]
        current_level: str = payload.get(
            "current_level", self._trust_levels.get(agent_id, "L1")
        )
        # Level ordering: L1 < L2 < L3 < L4 < L5
        level_rank = {"L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5}
        current_rank = level_rank.get(current_level, 0)
        required_rank = level_rank.get(required_level, 99)
        allowed = current_rank >= required_rank
        self._audit_log.append(
            {
                "event": "check_trust_requirement",
                "agent_id": agent_id,
                "required_level": required_level,
                "current_level": current_level,
                "allowed": allowed,
            }
        )
        if allowed:
            return {"allowed": True}
        return {
            "allowed": False,
            "reason": (
                f"Agent '{agent_id}' has trust level {current_level}, "
                f"but {required_level} is required."
            ),
        }

    async def _handle_atp_change_trust_level(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        agent_id: str = payload["agent_id"]
        new_level: str = payload["new_level"]
        authorized_by: str = payload["authorized_by"]
        self._trust_levels[agent_id] = new_level
        self._audit_log.append(
            {
                "event": "change_trust_level",
                "agent_id": agent_id,
                "new_level": new_level,
                "authorized_by": authorized_by,
            }
        )
        return {"success": True, "authorized_by": authorized_by}

    async def _handle_atp_get_recent_audit_entries(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        limit: int = payload.get("limit", 10)
        return {"entries": self._audit_log[-limit:]}

    # ------------------------------------------------------------------
    # AIP — Agent Identity Protocol
    # ------------------------------------------------------------------

    async def _handle_aip_register_identity(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        agent_id: str = payload["agent_id"]
        identity_id = f"iid-{uuid.uuid4().hex[:12]}"
        self._identity_registry[agent_id] = {
            "identity_id": identity_id,
            "agent_id": agent_id,
            "public_key": payload.get("public_key", ""),
            "metadata": payload.get("metadata", {}),
            "status": "active",
        }
        return {"registered": True, "identity_id": identity_id}

    async def _handle_aip_lookup_identity(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        agent_id: str = payload["agent_id"]
        record = self._identity_registry.get(agent_id)
        if record is None:
            return {"agent_id": agent_id, "status": "not_found"}
        return record

    async def _handle_aip_validate_credential(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        # Test vectors: credentials containing "invalid" are always rejected
        credential_value: str = payload.get("credential_value", "")
        if "invalid" in credential_value.lower():
            return {"valid": False, "reason": "Credential failed validation"}
        return {"valid": True}

    async def _handle_aip_revoke_identity(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        agent_id: str = payload["agent_id"]
        reason: str = payload.get("reason", "unspecified")
        revoked_by: str = payload.get("revoked_by", "unknown")
        if agent_id in self._identity_registry:
            self._identity_registry[agent_id]["status"] = "revoked"
        self._audit_log.append(
            {
                "event": "revoke_identity",
                "agent_id": agent_id,
                "reason": reason,
                "revoked_by": revoked_by,
            }
        )
        return {"revoked": True, "agent_id": agent_id, "revoked_by": revoked_by}

    # ------------------------------------------------------------------
    # AEAP — Agent Economic Action Protocol
    # ------------------------------------------------------------------

    async def _handle_aeap_check_spend_allowed(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        amount: float = float(payload.get("amount", 0))
        # Static limit — owner-configured, never auto-adjusted
        if amount > self._spend_limit_usd:
            return {
                "allowed": False,
                "reason": (
                    f"Requested amount {amount} USD exceeds the static limit "
                    f"of {self._spend_limit_usd} USD."
                ),
            }
        return {"allowed": True}

    async def _handle_aeap_record_spend(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        spend_id = f"spend-{uuid.uuid4().hex[:12]}"
        self._spend_ledger.append(
            {
                "spend_id": spend_id,
                "agent_id": payload.get("agent_id"),
                "amount": payload.get("amount"),
                "currency": payload.get("currency", "USD"),
                "description": payload.get("description", ""),
            }
        )
        return {"recorded": True, "spend_id": spend_id}

    async def _handle_aeap_get_budget_status(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        agent_id: str = payload.get("agent_id", "")
        total_spent = sum(
            entry["amount"]
            for entry in self._spend_ledger
            if entry.get("agent_id") == agent_id and isinstance(entry.get("amount"), (int, float))
        )
        remaining = max(0.0, self._spend_limit_usd - total_spent)
        return {
            "agent_id": agent_id,
            "limit": self._spend_limit_usd,
            "spent": total_spent,
            "remaining": remaining,
            "currency": "USD",
        }

    # ------------------------------------------------------------------
    # AOAP — Agent Observability and Accountability Protocol
    # ------------------------------------------------------------------

    async def _handle_aoap_append_audit_entry(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        entry_id = f"entry-{uuid.uuid4().hex[:12]}"
        self._audit_log.append({**payload, "entry_id": entry_id})
        return {"appended": True, "entry_id": entry_id}

    async def _handle_aoap_export_audit_log(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        agent_id: str | None = payload.get("agent_id")
        entries = (
            [entry for entry in self._audit_log if entry.get("agent_id") == agent_id]
            if agent_id
            else list(self._audit_log)
        )
        return {"entries": entries, "format": payload.get("format", "json")}

    async def _handle_aoap_verify_audit_chain(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        # Simple mock: always reports as valid (no actual hash chain in the example)
        return {"valid": True, "entries_checked": len(self._audit_log)}

    async def _handle_aoap_query_audit_entries(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        agent_id: str | None = payload.get("agent_id")
        event_type: str | None = payload.get("event_type")
        entries = list(self._audit_log)
        if agent_id:
            entries = [e for e in entries if e.get("agent_id") == agent_id]
        if event_type:
            entries = [e for e in entries if e.get("event_type") == event_type]
        return {"entries": entries}

    # ------------------------------------------------------------------
    # AMGP — Agent Memory Governance Protocol
    # ------------------------------------------------------------------

    async def _handle_amgp_write_memory_record(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        retention_policy: str = payload.get("retention_policy", "session")
        consent_token: object = payload.get("consent_token")
        if retention_policy == "long_term" and consent_token is None:
            return {
                "written": False,
                "reason": "Long-term retention requires a consent token.",
            }
        record_id = f"rec-{uuid.uuid4().hex[:12]}"
        self._memory_records[record_id] = {
            "record_id": record_id,
            "agent_id": payload.get("agent_id"),
            "record_type": payload.get("record_type"),
            "content": payload.get("content"),
            "retention_policy": retention_policy,
        }
        return {"written": True, "record_id": record_id}

    async def _handle_amgp_query_memory_records(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        agent_id: str | None = payload.get("agent_id")
        retention_policy: str | None = payload.get("retention_policy")
        records = list(self._memory_records.values())
        if agent_id:
            records = [r for r in records if r.get("agent_id") == agent_id]
        if retention_policy:
            records = [r for r in records if r.get("retention_policy") == retention_policy]
        return {"records": records}

    async def _handle_amgp_delete_memory_record(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        record_id: str = payload.get("record_id", "")
        self._memory_records.pop(record_id, None)
        return {"deleted": True, "record_id": record_id}


# ---------------------------------------------------------------------------
# Main: run Silver-level certification
# ---------------------------------------------------------------------------


async def main() -> None:
    """Run conformance checks and print the certification result."""
    implementation = MockAgentSystem()
    runner = ConformanceRunner(implementation=implementation)
    scorer = CertificationScorer()

    # Silver requires ATP + AEAP + AOAP at 75%+ pass rate.
    # We also run AIP and AMGP to demonstrate broader coverage.
    protocols_to_run = ["atp", "aip", "aeap", "amgp", "aoap"]

    print("AumOS Self-Assessment Toolkit — Example Run")
    print("=" * 52)
    print(f"Implementation : {implementation.get_implementation_name()}")
    print(f"Protocols      : {', '.join(protocols_to_run).upper()}")
    print()

    run_result = await runner.run(protocols=protocols_to_run)
    certification_result = scorer.score(run_result)

    # Per-protocol summary
    print("Protocol Results")
    print("-" * 40)
    for protocol_id, protocol_result in run_result.protocol_results.items():
        score_pct = round(protocol_result.score * 100, 1)
        print(
            f"  {protocol_id.upper():8}  {protocol_result.passed} passed, "
            f"{protocol_result.failed} failed, "
            f"{protocol_result.skipped} skipped  ({score_pct}%)"
        )
    print()

    # Overall result
    overall_pct = round(run_result.overall_score_pct, 1)
    print(f"Overall score  : {overall_pct}%")

    achieved = certification_result.achieved_level
    if achieved is not None:
        print(f"Achieved level : {achieved.value.upper()} (Self-Assessed)")
    else:
        print("Achieved level : None — below Bronze threshold")
        if certification_result.missing_protocols:
            print(
                f"Missing protocols: {', '.join(certification_result.missing_protocols).upper()}"
            )

    print()
    print(
        "Note: This is a self-assessed result. "
        "See docs/submission.md for information on official certification."
    )


if __name__ == "__main__":
    asyncio.run(main())
