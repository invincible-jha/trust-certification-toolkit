# FIRE LINE — trust-certification-toolkit

This document defines the exact boundary between what is permitted in this open-source
package and what is reserved or explicitly excluded.

---

## IN SCOPE (safe to implement and ship)

| Feature | Implementation |
|---|---|
| Self-assessment against published conformance requirements | LOCAL only — no network calls |
| Protocol check execution via `ImplementationAdapter` | Generic interface, works with any implementation |
| Scoring to certification levels | Deterministic mapping: score + required protocols → level |
| Markdown and JSON report generation | Offline file generation only |
| SVG badge generation | Local SVG rendering, no external services |
| Certification levels publicly documented | Bronze, Silver, Gold, Platinum — no secret criteria |

---

## EXCLUDED (never implement in this package)

### Automatic Trust or Score Computation
- Behavioral scoring or automated trust score computation of any kind
- Automatic level promotion based on observed behavior
- Any form of `computeTrustScore`, `behavioralScore`, or `progressLevel`

### Adaptive or ML-Based Features
- Adaptive budget allocation
- ML-based spending prediction
- Dynamic threshold adjustment
- Any form of `adaptiveBudget`, `optimizeBudget`, or `predictSpending`

### Audit Intelligence
- Anomaly detection over certification results
- Counterfactual generation
- Any form of `detectAnomaly` or `generateCounterfactual`

### External Communication
- Automatic submission to any AumOS service
- Network calls during self-assessment
- Telemetry or usage reporting

### Reserved Internal Systems
- PWM (Personal World Model) integration
- MAE (Mission Alignment Engine) integration
- STP (Social Trust Protocol) integration
- GOVERNANCE_PIPELINE orchestration
- Three-tier attention filters

---

## Forbidden Identifiers

The following identifiers MUST NEVER appear in any source file in this repository:

```
progressLevel          promoteLevel           computeTrustScore
behavioralScore        adaptiveBudget         optimizeBudget
predictSpending        detectAnomaly          generateCounterfactual
PersonalWorldModel     MissionAlignment       SocialTrust
CognitiveLoop          AttentionFilter        GOVERNANCE_PIPELINE
```

---

## Key Rules

1. **Self-assessment is LOCAL ONLY** — no server communication during any operation
2. **Badges say "Self-Assessed"** — not "Officially Certified"
3. **NO automatic submission** to any AumOS service
4. **Certification levels are publicly documented** — no secret criteria
5. **Adapter interface is generic** — works with any implementation, not AumOS-specific

---

## Enforcement

- `scripts/fire-line-audit.sh` scans all source files for forbidden identifiers
- CI pipeline runs the audit on every pull request
- Any PR that crosses the fire line must be closed — do not merge

---

*Last updated: 2026-02-26*

Copyright (c) 2026 MuVeraAI Corporation. Apache 2.0.
