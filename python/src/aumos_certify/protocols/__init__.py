# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
Per-protocol conformance check modules.

Each module exposes a single async function with the signature:

    async def run_checks(adapter: ImplementationAdapter) -> ProtocolResult

The function runs all checks for its protocol and returns a ProtocolResult.
"""

from __future__ import annotations
