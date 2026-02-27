# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
Certification expiry, renewal, and revocation engine for the AumOS Certified
badge program.

Manages the full lifecycle of a certification record — from initial issuance
through renewal, suspension, reinstatement, and revocation. All state is held
in-memory. No network calls are made by any operation in this module. Expiry
processing is NOT automatic — the operator must call ``check_expirations()``
explicitly.

Example usage::

    from certification_lifecycle import (
        CertificationLifecycleManager,
        RenewalPolicy,
    )

    policy = RenewalPolicy(validity_period_days=730, grace_period_days=30)
    manager = CertificationLifecycleManager(policy=policy)

    record = manager.issue(
        agent_id="agent-001",
        certification_level="silver",
        assessment_report_hash="a3b4c5d6..." * 8,  # 64-char SHA-256
    )

    # Later — renew before expiry
    renewed = manager.renew(record.record_id, new_assessment_report_hash="e7f8...")

    # Explicit expiry sweep (call this on a schedule chosen by the operator)
    newly_expired = manager.check_expirations()
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class CertificationState(str, Enum):
    """All valid states a ``CertificationRecord`` may occupy."""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    PENDING_RENEWAL = "pending_renewal"


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class CertificationRecord(BaseModel, frozen=True):
    """Immutable snapshot of a single certification record.

    Because the model is frozen, each state transition produces a new
    ``CertificationRecord`` instance. The registry in
    ``CertificationLifecycleManager`` is updated to store the latest snapshot.
    """

    record_id: str = Field(description="UUID v4 identifier for this certification record.")
    agent_id: str = Field(description="Stable identifier of the agent holding this record.")
    certification_level: str = Field(
        description="The certification level (e.g., 'bronze', 'silver', 'gold', 'platinum')."
    )
    issued_at: datetime = Field(description="Timestamp when this record was first issued.")
    expires_at: datetime = Field(description="Timestamp when this record expires.")
    state: CertificationState = Field(description="Current lifecycle state of the record.")
    renewal_count: int = Field(
        default=0,
        description="Number of times this record has been renewed.",
        ge=0,
    )
    revocation_reason: str | None = Field(
        default=None,
        description="Human-readable reason for revocation, if applicable.",
    )
    assessment_report_hash: str = Field(
        description=(
            "SHA-256 hex digest of the assessment report that underpins this record. "
            "Allows independent verification that the report on file matches this record."
        )
    )


class RenewalPolicy(BaseModel, frozen=True):
    """Policy governing certification validity and renewal behaviour."""

    validity_period_days: int = Field(
        default=730,
        description=(
            "Number of days a newly issued or renewed certification remains valid. "
            "Defaults to 730 days (approximately two years)."
        ),
        gt=0,
    )
    grace_period_days: int = Field(
        default=30,
        description=(
            "Number of days after expiry during which a renewal is still permitted. "
            "Within the grace period the record state is still treated as renewable "
            "even though it has technically expired."
        ),
        ge=0,
    )
    max_renewals: int = Field(
        default=10,
        description=(
            "Maximum number of times a record may be renewed. "
            "Once reached, a new assessment and issuance is required."
        ),
        ge=0,
    )
    require_reassessment: bool = Field(
        default=True,
        description=(
            "When True, a new ``assessment_report_hash`` must be provided on renewal, "
            "indicating the agent has been re-assessed. When False, the existing hash "
            "is carried forward."
        ),
    )


class LifecycleEvent(BaseModel, frozen=True):
    """A single immutable event in a certification record's lifecycle history."""

    event_id: str = Field(description="UUID v4 identifier for this event.")
    record_id: str = Field(description="The record this event belongs to.")
    event_type: Literal[
        "issued", "renewed", "expired", "revoked", "suspended", "reinstated"
    ] = Field(description="Category of lifecycle transition.")
    occurred_at: datetime = Field(description="Timestamp when this event occurred.")
    details: str = Field(description="Human-readable description of the event.")


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------


class CertificationLifecycleManager:
    """
    Manages the full lifecycle of certification records in memory.

    All operations are local — no network calls, no database access.
    Expiry transitions are NOT automatic: the operator must call
    ``check_expirations()`` on a schedule of their choosing.

    Args:
        policy: The ``RenewalPolicy`` governing validity and renewal limits.
            Defaults to a ``RenewalPolicy()`` with its documented defaults.
    """

    def __init__(self, policy: RenewalPolicy | None = None) -> None:
        self._policy: RenewalPolicy = policy if policy is not None else RenewalPolicy()
        self._records: dict[str, CertificationRecord] = {}
        self._events: dict[str, list[LifecycleEvent]] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _now(self) -> datetime:
        """Return the current time in UTC. Extracted for testability."""
        return datetime.now(tz=timezone.utc)

    def _new_event(
        self,
        record_id: str,
        event_type: Literal[
            "issued", "renewed", "expired", "revoked", "suspended", "reinstated"
        ],
        details: str,
        occurred_at: datetime | None = None,
    ) -> LifecycleEvent:
        """Create and store a ``LifecycleEvent`` for ``record_id``."""
        event = LifecycleEvent(
            event_id=str(uuid4()),
            record_id=record_id,
            event_type=event_type,
            occurred_at=occurred_at if occurred_at is not None else self._now(),
            details=details,
        )
        self._events.setdefault(record_id, []).append(event)
        return event

    def _store(self, record: CertificationRecord) -> None:
        """Persist the latest snapshot of a record in the registry."""
        self._records[record.record_id] = record

    # ------------------------------------------------------------------
    # Issuance
    # ------------------------------------------------------------------

    def issue(
        self,
        agent_id: str,
        certification_level: str,
        assessment_report_hash: str,
    ) -> CertificationRecord:
        """Create a new ``ACTIVE`` certification record for an agent.

        The expiry date is calculated as ``now + policy.validity_period_days``.
        A corresponding ``"issued"`` lifecycle event is recorded.

        Args:
            agent_id: Stable identifier of the agent receiving the certification.
            certification_level: The level being issued (e.g., ``"silver"``).
            assessment_report_hash: SHA-256 hex digest of the assessment report.

        Returns:
            The newly created ``CertificationRecord``.
        """
        now: datetime = self._now()
        record_id: str = str(uuid4())
        expires_at: datetime = now + timedelta(days=self._policy.validity_period_days)

        record = CertificationRecord(
            record_id=record_id,
            agent_id=agent_id,
            certification_level=certification_level,
            issued_at=now,
            expires_at=expires_at,
            state=CertificationState.ACTIVE,
            renewal_count=0,
            revocation_reason=None,
            assessment_report_hash=assessment_report_hash,
        )
        self._store(record)
        self._new_event(
            record_id=record_id,
            event_type="issued",
            details=(
                f"Certification issued at level '{certification_level}' for agent "
                f"'{agent_id}'. Expires {expires_at.date().isoformat()}."
            ),
            occurred_at=now,
        )
        return record

    # ------------------------------------------------------------------
    # Renewal
    # ------------------------------------------------------------------

    def renew(
        self,
        record_id: str,
        new_assessment_report_hash: str | None = None,
    ) -> CertificationRecord:
        """Renew an existing certification record, extending its expiry.

        Renewal is permitted when the record is ``ACTIVE`` or when it is
        ``EXPIRED`` but still within the grace period defined by
        ``policy.grace_period_days``.

        Args:
            record_id: The UUID of the record to renew.
            new_assessment_report_hash: SHA-256 hex digest of the new assessment
                report. Required when ``policy.require_reassessment`` is ``True``.
                When not provided and reassessment is not required, the existing
                hash is carried forward.

        Returns:
            The updated ``CertificationRecord`` with an extended expiry date.

        Raises:
            KeyError: If ``record_id`` is not found in the registry.
            ValueError: If the record is ``REVOKED``, if the maximum number of
                renewals has been reached, if the record is ``SUSPENDED``, or
                if the record has expired beyond the grace period.
        """
        record: CertificationRecord | None = self._records.get(record_id)
        if record is None:
            raise KeyError(f"No record found with record_id '{record_id}'.")

        now: datetime = self._now()

        if record.state == CertificationState.REVOKED:
            raise ValueError(
                f"Record '{record_id}' has been revoked and cannot be renewed. "
                "A new assessment and issuance is required."
            )

        if record.state == CertificationState.SUSPENDED:
            raise ValueError(
                f"Record '{record_id}' is suspended. Reinstate the record before renewing."
            )

        if record.renewal_count >= self._policy.max_renewals:
            raise ValueError(
                f"Record '{record_id}' has reached the maximum renewal limit "
                f"({self._policy.max_renewals}). A new assessment and issuance is required."
            )

        # Allow renewal if ACTIVE, or if EXPIRED but within grace period.
        grace_deadline: datetime = record.expires_at + timedelta(
            days=self._policy.grace_period_days
        )
        if record.state == CertificationState.EXPIRED and now > grace_deadline:
            raise ValueError(
                f"Record '{record_id}' expired on {record.expires_at.date().isoformat()} "
                f"and the grace period ({self._policy.grace_period_days} days) has passed. "
                "A new assessment and issuance is required."
            )

        # Determine which report hash to carry forward.
        if self._policy.require_reassessment:
            if new_assessment_report_hash is None:
                raise ValueError(
                    "Policy requires a new assessment report hash on renewal. "
                    "Provide 'new_assessment_report_hash'."
                )
            report_hash: str = new_assessment_report_hash
        else:
            report_hash = (
                new_assessment_report_hash
                if new_assessment_report_hash is not None
                else record.assessment_report_hash
            )

        new_expires_at: datetime = now + timedelta(days=self._policy.validity_period_days)
        renewed_record = record.model_copy(
            update={
                "expires_at": new_expires_at,
                "state": CertificationState.ACTIVE,
                "renewal_count": record.renewal_count + 1,
                "assessment_report_hash": report_hash,
            }
        )
        self._store(renewed_record)
        self._new_event(
            record_id=record_id,
            event_type="renewed",
            details=(
                f"Certification renewed (renewal #{renewed_record.renewal_count}). "
                f"New expiry: {new_expires_at.date().isoformat()}."
            ),
            occurred_at=now,
        )
        return renewed_record

    # ------------------------------------------------------------------
    # Revocation
    # ------------------------------------------------------------------

    def revoke(self, record_id: str, reason: str) -> CertificationRecord:
        """Permanently revoke a certification record.

        A revoked record cannot be renewed. A fresh assessment and issuance
        is required to obtain a new certification.

        Args:
            record_id: The UUID of the record to revoke.
            reason: Human-readable explanation of the revocation.

        Returns:
            The updated ``CertificationRecord`` in ``REVOKED`` state.

        Raises:
            KeyError: If ``record_id`` is not found.
            ValueError: If the record is already ``REVOKED``.
        """
        record: CertificationRecord | None = self._records.get(record_id)
        if record is None:
            raise KeyError(f"No record found with record_id '{record_id}'.")

        if record.state == CertificationState.REVOKED:
            raise ValueError(f"Record '{record_id}' is already revoked.")

        now: datetime = self._now()
        revoked_record = record.model_copy(
            update={
                "state": CertificationState.REVOKED,
                "revocation_reason": reason,
            }
        )
        self._store(revoked_record)
        self._new_event(
            record_id=record_id,
            event_type="revoked",
            details=f"Certification revoked. Reason: {reason}",
            occurred_at=now,
        )
        return revoked_record

    # ------------------------------------------------------------------
    # Suspension and reinstatement
    # ------------------------------------------------------------------

    def suspend(self, record_id: str, reason: str) -> CertificationRecord:
        """Temporarily suspend a certification record.

        A suspended record can be reinstated. Suspension differs from
        revocation in that it is reversible.

        Args:
            record_id: The UUID of the record to suspend.
            reason: Human-readable explanation of the suspension.

        Returns:
            The updated ``CertificationRecord`` in ``SUSPENDED`` state.

        Raises:
            KeyError: If ``record_id`` is not found.
            ValueError: If the record is already ``SUSPENDED`` or ``REVOKED``.
        """
        record: CertificationRecord | None = self._records.get(record_id)
        if record is None:
            raise KeyError(f"No record found with record_id '{record_id}'.")

        if record.state == CertificationState.SUSPENDED:
            raise ValueError(f"Record '{record_id}' is already suspended.")

        if record.state == CertificationState.REVOKED:
            raise ValueError(
                f"Record '{record_id}' is revoked and cannot be suspended. "
                "Revocation is terminal."
            )

        now: datetime = self._now()
        suspended_record = record.model_copy(
            update={"state": CertificationState.SUSPENDED}
        )
        self._store(suspended_record)
        self._new_event(
            record_id=record_id,
            event_type="suspended",
            details=f"Certification suspended. Reason: {reason}",
            occurred_at=now,
        )
        return suspended_record

    def reinstate(self, record_id: str) -> CertificationRecord:
        """Reinstate a suspended certification record to ``ACTIVE`` state.

        Only records in ``SUSPENDED`` state may be reinstated. Revoked records
        are terminal and require a new issuance.

        Args:
            record_id: The UUID of the record to reinstate.

        Returns:
            The updated ``CertificationRecord`` in ``ACTIVE`` state.

        Raises:
            KeyError: If ``record_id`` is not found.
            ValueError: If the record is not currently in ``SUSPENDED`` state.
        """
        record: CertificationRecord | None = self._records.get(record_id)
        if record is None:
            raise KeyError(f"No record found with record_id '{record_id}'.")

        if record.state != CertificationState.SUSPENDED:
            raise ValueError(
                f"Only SUSPENDED records can be reinstated. "
                f"Record '{record_id}' is currently in state '{record.state.value}'."
            )

        now: datetime = self._now()
        reinstated_record = record.model_copy(
            update={"state": CertificationState.ACTIVE}
        )
        self._store(reinstated_record)
        self._new_event(
            record_id=record_id,
            event_type="reinstated",
            details="Certification reinstated from SUSPENDED to ACTIVE.",
            occurred_at=now,
        )
        return reinstated_record

    # ------------------------------------------------------------------
    # Expiry sweep
    # ------------------------------------------------------------------

    def check_expirations(
        self, reference_date: datetime | None = None
    ) -> list[CertificationRecord]:
        """Scan all records and transition expired ``ACTIVE`` records to ``EXPIRED``.

        This method must be called explicitly by the operator — there is no
        automatic background expiry processing. The operator is responsible for
        scheduling calls to this method on an appropriate interval.

        Only records in ``ACTIVE`` state whose ``expires_at`` is before
        ``reference_date`` are transitioned. Records in other states are left
        unchanged.

        Args:
            reference_date: The point-in-time to use for expiry evaluation.
                Defaults to ``datetime.now(tz=timezone.utc)`` if not provided.

        Returns:
            A list of ``CertificationRecord`` objects that were newly transitioned
            to ``EXPIRED`` during this call. Empty list if none expired.
        """
        now: datetime = (
            reference_date
            if reference_date is not None
            else self._now()
        )
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        newly_expired: list[CertificationRecord] = []

        for record_id, record in list(self._records.items()):
            if record.state == CertificationState.ACTIVE and record.expires_at < now:
                expired_record = record.model_copy(
                    update={"state": CertificationState.EXPIRED}
                )
                self._store(expired_record)
                self._new_event(
                    record_id=record_id,
                    event_type="expired",
                    details=(
                        f"Certification expired. Expiry date was "
                        f"{record.expires_at.date().isoformat()}."
                    ),
                    occurred_at=now,
                )
                newly_expired.append(expired_record)

        return newly_expired

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get_record(self, record_id: str) -> CertificationRecord | None:
        """Return the current snapshot of a record, or ``None`` if not found.

        Args:
            record_id: The UUID of the record to retrieve.

        Returns:
            The ``CertificationRecord`` if found, otherwise ``None``.
        """
        return self._records.get(record_id)

    def get_records_for_agent(self, agent_id: str) -> list[CertificationRecord]:
        """Return all records associated with a given agent, newest first.

        Args:
            agent_id: The stable identifier of the agent to look up.

        Returns:
            A list of ``CertificationRecord`` objects issued to that agent,
            ordered by ``issued_at`` descending.
        """
        return sorted(
            (r for r in self._records.values() if r.agent_id == agent_id),
            key=lambda r: r.issued_at,
            reverse=True,
        )

    def get_events(self, record_id: str) -> list[LifecycleEvent]:
        """Return all lifecycle events for a record in chronological order.

        Args:
            record_id: The UUID of the record whose events to retrieve.

        Returns:
            A list of ``LifecycleEvent`` objects ordered by ``occurred_at``
            ascending. Returns an empty list if the record has no events.
        """
        events: list[LifecycleEvent] = self._events.get(record_id, [])
        return sorted(events, key=lambda e: e.occurred_at)

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_events_json(self, record_id: str) -> str:
        """Serialise all lifecycle events for a record to a JSON string.

        The output uses ISO 8601 datetime formatting and 2-space indentation.

        Args:
            record_id: The UUID of the record whose events to export.

        Returns:
            A JSON array string containing all lifecycle events, in
            chronological order. Returns ``"[]"`` if no events exist.
        """
        events: list[LifecycleEvent] = self.get_events(record_id)
        payload: list[dict[str, object]] = [
            json.loads(event.model_dump_json()) for event in events
        ]
        return json.dumps(payload, indent=2)
