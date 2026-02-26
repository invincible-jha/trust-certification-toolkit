# CLAUDE.md — trust-certification-toolkit

## Project Identity

Package (Python): `aumos-certify`
Package (TypeScript): `@aumos/badge-generator`
Purpose: Self-assessment toolkit for the "AumOS Certified" badge program.
Repo: `github.com/aumos-ai/trust-certification-toolkit`

---

## CRITICAL: Fire Line

Read `FIRE_LINE.md` before touching ANY source file.

The absolute rules for this project:

- **Self-assessment is LOCAL ONLY** — no network calls during any operation
- **Badges say "Self-Assessed"** — never "Officially Certified"
- **NO automatic submission** to any external service
- **NEVER** implement behavioral scoring, adaptive levels, or automatic promotion
- **NEVER** reference PWM, MAE, STP, CognitiveLoop, GOVERNANCE_PIPELINE

### Forbidden Identifiers — MUST NEVER APPEAR in any source file

```
progressLevel      promoteLevel       computeTrustScore  behavioralScore
adaptiveBudget     optimizeBudget     predictSpending
detectAnomaly      generateCounterfactual
PersonalWorldModel MissionAlignment   SocialTrust
CognitiveLoop      AttentionFilter    GOVERNANCE_PIPELINE
```

---

## Architecture

### Python (`python/src/aumos_certify/`)

```
types.py          — Pydantic models: CertificationLevel, RunResult, ProtocolResult,
                    ImplementationAdapter (ABC)
levels.py         — Level definitions: thresholds, required protocols, badge colors
runner.py         — ConformanceRunner: loads vectors, calls adapter, returns RunResult
scorer.py         — CertificationScorer: maps RunResult → CertificationResult
report.py         — ReportGenerator: Markdown + JSON offline report
cli.py            — Typer CLI: aumos-certify run | badge | report
protocols/
  atp.py          — ATP conformance checks
  aip.py          — AIP conformance checks
  aeap.py         — AEAP conformance checks
  amgp.py         — AMGP conformance checks
  aoap.py         — AOAP conformance checks
  cross_protocol.py — Cross-protocol conformance checks
```

Dependency direction: `cli → runner/scorer/report → types/levels → protocols`

### TypeScript (`badges/generator/src/`)

```
badge.ts   — generateBadge(level) → SVG string
index.ts   — Barrel exports
```

---

## Code Standards

### Python
- Python 3.10+, Pydantic v2, Typer
- Type hints on EVERY function signature
- `ruff` linting, zero warnings
- `mypy --strict`, zero errors
- Every source file starts with:
  ```python
  # SPDX-License-Identifier: Apache-2.0
  # Copyright (c) 2026 MuVeraAI Corporation
  ```

### TypeScript
- Strict mode, no `any`, no `@ts-ignore`
- Named exports only
- Zod for runtime validation at system boundaries
- Every source file starts with:
  ```typescript
  // SPDX-License-Identifier: Apache-2.0
  // Copyright (c) 2026 MuVeraAI Corporation
  ```

---

## Common Tasks

### Python CLI

```bash
cd python/
pip install -e ".[dev]"

# Run checks
aumos-certify run --implementation examples/certify_sdk.py --level gold

# Generate badge
aumos-certify badge --level silver --output ./badge.svg

# Generate report
aumos-certify report --format md
aumos-certify report --format json
```

### Badge Generator

```bash
cd badges/generator/
npm install
npm run build
npm run typecheck
```

---

## Commit Convention

```
feat(trust-cert): description
fix(trust-cert): description
docs(trust-cert): description
chore(trust-cert): description
```

---

Copyright (c) 2026 MuVeraAI Corporation. Apache 2.0.
