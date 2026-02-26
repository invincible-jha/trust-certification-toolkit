# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
ConformanceRunner — orchestrates protocol conformance checks against an
ImplementationAdapter and aggregates results into a RunResult.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from aumos_certify.protocols import aip, aeap, amgp, aoap, atp, cross_protocol
from aumos_certify.types import ImplementationAdapter, ProtocolResult, RunResult

if TYPE_CHECKING:
    pass

# Map of protocol identifier → check function
_PROTOCOL_REGISTRY: dict[
    str,
    object,
] = {
    "atp": atp.run_checks,
    "aip": aip.run_checks,
    "aeap": aeap.run_checks,
    "amgp": amgp.run_checks,
    "aoap": aoap.run_checks,
    "cross_protocol": cross_protocol.run_checks,
}


class ConformanceRunner:
    """
    Executes conformance checks against an ImplementationAdapter.

    Usage::

        runner = ConformanceRunner(implementation=my_adapter)
        result = await runner.run(protocols=["atp", "aeap", "aoap"])
    """

    def __init__(self, implementation: ImplementationAdapter) -> None:
        self._implementation = implementation

    async def run(
        self,
        protocols: list[str] | None = None,
    ) -> RunResult:
        """
        Run conformance checks for the specified protocols.

        Args:
            protocols: List of protocol identifiers to run (e.g., ["atp", "aip"]).
                       Pass None to run all registered protocols.

        Returns:
            A RunResult containing per-protocol results and overall scoring data.

        Raises:
            ValueError: If an unrecognised protocol identifier is provided.
        """
        requested_protocols = protocols if protocols is not None else list(_PROTOCOL_REGISTRY)

        unknown = [p for p in requested_protocols if p not in _PROTOCOL_REGISTRY]
        if unknown:
            raise ValueError(
                f"Unknown protocol(s): {unknown}. "
                f"Registered protocols: {list(_PROTOCOL_REGISTRY)}"
            )

        run_id = str(uuid.uuid4())
        started_at = datetime.now(tz=timezone.utc)

        await self._implementation.setup()

        protocol_results: dict[str, ProtocolResult] = {}
        try:
            for protocol_id in requested_protocols:
                check_fn = _PROTOCOL_REGISTRY[protocol_id]
                # All check functions are async callables; call dynamically
                result: ProtocolResult = await check_fn(self._implementation)  # type: ignore[operator]
                protocol_results[protocol_id] = result
        finally:
            await self._implementation.teardown()

        completed_at = datetime.now(tz=timezone.utc)

        return RunResult(
            implementation_name=self._implementation.get_implementation_name(),
            run_id=run_id,
            started_at=started_at,
            completed_at=completed_at,
            protocols_run=requested_protocols,
            protocol_results=protocol_results,
        )
