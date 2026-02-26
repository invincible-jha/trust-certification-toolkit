# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
Core types for the aumos-certify toolkit.

Defines the data models and the ImplementationAdapter interface that connects
any AumOS protocol implementation to the ConformanceRunner.
"""

from __future__ import annotations

import abc
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CertificationLevel(str, Enum):
    """Achievable certification levels in the AumOS Certified badge program."""

    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class ConformanceStatus(str, Enum):
    """Result of a single conformance check."""

    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


class CheckResult(BaseModel):
    """Result of a single conformance check within a protocol."""

    check_id: str = Field(description="Unique identifier for this check")
    description: str = Field(description="Human-readable description of what was checked")
    status: ConformanceStatus = Field(description="Outcome of the check")
    message: str | None = Field(
        default=None,
        description="Optional detail message explaining the result",
    )
    conformance_level: str = Field(
        default="MUST",
        description="RFC 2119 conformance level of this requirement (MUST/SHOULD/MAY)",
    )


class ProtocolResult(BaseModel):
    """Aggregated results for a single protocol's conformance checks."""

    protocol: str = Field(description="Protocol identifier (e.g., 'atp', 'aip')")
    checks: list[CheckResult] = Field(default_factory=list)
    passed: int = Field(default=0, description="Number of checks that passed")
    failed: int = Field(default=0, description="Number of checks that failed")
    skipped: int = Field(default=0, description="Number of checks that were skipped")
    errors: int = Field(default=0, description="Number of checks that errored")

    @property
    def total(self) -> int:
        """Total number of checks executed (excluding skips)."""
        return self.passed + self.failed + self.errors

    @property
    def score(self) -> float:
        """Pass rate for this protocol (0.0–1.0). Returns 0.0 if no checks ran."""
        if self.total == 0:
            return 0.0
        return self.passed / self.total


class RunResult(BaseModel):
    """Complete result set from a ConformanceRunner execution."""

    implementation_name: str = Field(description="Name of the implementation under test")
    run_id: str = Field(description="Unique identifier for this run")
    started_at: datetime = Field(description="Timestamp when the run began")
    completed_at: datetime = Field(description="Timestamp when the run completed")
    protocols_run: list[str] = Field(description="List of protocol identifiers that were checked")
    protocol_results: dict[str, ProtocolResult] = Field(
        default_factory=dict,
        description="Per-protocol results keyed by protocol identifier",
    )

    @property
    def overall_score(self) -> float:
        """Aggregate pass rate across all protocols (0.0–1.0)."""
        results = list(self.protocol_results.values())
        if not results:
            return 0.0
        total_checks = sum(r.total for r in results)
        if total_checks == 0:
            return 0.0
        total_passed = sum(r.passed for r in results)
        return total_passed / total_checks

    @property
    def overall_score_pct(self) -> float:
        """Overall score as a percentage (0–100)."""
        return self.overall_score * 100.0


class CertificationResult(BaseModel):
    """Output of CertificationScorer — the achieved level and supporting detail."""

    run_result: RunResult = Field(description="The run result this certification is based on")
    achieved_level: CertificationLevel | None = Field(
        default=None,
        description="The highest certification level achieved, or None if below Bronze",
    )
    score_pct: float = Field(description="Overall score as a percentage (0–100)")
    required_protocols_satisfied: bool = Field(
        description="Whether all required protocols for the achieved level were run and passed",
    )
    missing_protocols: list[str] = Field(
        default_factory=list,
        description="Required protocols that were not run or did not pass",
    )
    level_detail: dict[str, Any] = Field(
        default_factory=dict,
        description="Per-level pass/fail detail for reporting",
    )


class ImplementationAdapter(abc.ABC):
    """
    Abstract base class for connecting any implementation to the ConformanceRunner.

    Implementers subclass this and provide the protocol-specific invocations.
    The adapter is deliberately generic — it is not limited to AumOS implementations.
    """

    @abc.abstractmethod
    def get_implementation_name(self) -> str:
        """Return a human-readable name for the implementation under test."""
        ...

    @abc.abstractmethod
    async def invoke(
        self,
        protocol: str,
        operation: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Invoke a single protocol operation on the implementation.

        Args:
            protocol: Protocol identifier (e.g., "atp", "aip").
            operation: Operation name within the protocol.
            payload: Input data for the operation.

        Returns:
            A dict containing the implementation's response. Structure
            is protocol and operation-specific.
        """
        ...

    async def setup(self) -> None:
        """
        Optional hook called once before any checks are run.

        Override to perform test fixture setup (e.g., start a local server,
        initialise in-memory state). Default implementation is a no-op.
        """

    async def teardown(self) -> None:
        """
        Optional hook called once after all checks have completed.

        Override to clean up resources. Default implementation is a no-op.
        """
