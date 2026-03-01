# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
"""
aumos-certify — AumOS self-assessment toolkit for the AumOS Certified badge program.

Public API surface:

    from aumos_certify import ConformanceRunner, CertificationScorer, ReportGenerator
    from aumos_certify import ImplementationAdapter, CertificationLevel
    from aumos_certify import CertificationResult, RunResult, ProtocolResult

All self-assessment operations are LOCAL ONLY — no data is sent anywhere.
"""

from __future__ import annotations

from aumos_certify.exporters import HtmlExporter, JsonExporter, MarkdownExporter
from aumos_certify.history import CertHistory, CertHistoryEntry
from aumos_certify.levels import LEVEL_DEFINITIONS, LevelDefinition, get_level_definition
from aumos_certify.report import ReportGenerator
from aumos_certify.runner import ConformanceRunner
from aumos_certify.scorer import CertificationScorer
from aumos_certify.types import (
    CertificationLevel,
    CertificationResult,
    CheckResult,
    ConformanceStatus,
    ImplementationAdapter,
    ProtocolResult,
    RunResult,
)

__version__ = "0.1.0"

__all__ = [
    # core types
    "CertificationLevel",
    "CertificationResult",
    "CheckResult",
    "ConformanceStatus",
    "ImplementationAdapter",
    "ProtocolResult",
    "RunResult",
    # levels
    "LEVEL_DEFINITIONS",
    "LevelDefinition",
    "get_level_definition",
    # runner / scorer / report
    "CertificationScorer",
    "ConformanceRunner",
    "ReportGenerator",
    # exporters
    "HtmlExporter",
    "JsonExporter",
    "MarkdownExporter",
    # history
    "CertHistory",
    "CertHistoryEntry",
]
