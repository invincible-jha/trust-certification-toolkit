# AumOS Trust Certification Toolkit

[![Governance Score](https://img.shields.io/badge/governance-self--assessed-blue)](https://github.com/aumos-ai/trust-certification-toolkit)
[![PyPI](https://img.shields.io/pypi/v/aumos-certify)](https://pypi.org/project/aumos-certify/)
[![npm](https://img.shields.io/npm/v/@aumos/badge-generator)](https://www.npmjs.com/package/@aumos/badge-generator)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

Self-assessment tools, conformance test automation, badge generation, and certification submission for the "AumOS Certified" badge program.

**Package:** `aumos-certify` (Python CLI) + `@aumos/badge-generator` (TypeScript)
**License:** Apache 2.0
**Status:** v0.1.0

---

## Why Does This Exist?

### The Problem: "We Support AI Governance" Means Nothing

Every AI platform claims to support governance, safety, and responsible AI. There are no standard definitions, no public criteria, and no independent way to check whether a claim is true. When a procurement team asks "is your AI system governed?", the only available answers are marketing copy.

This is the same problem manufacturing had before ISO standards, finance had before GAAP, and software security had before SOC 2. Without a published, testable standard, "compliant" is whatever the vendor says it is.

### The Solution: A Testable, Public Standard With Machine-Readable Results

The AumOS Trust Certification Toolkit gives governance implementers — SDK authors, platform builders, enterprise teams — a way to measure their implementation against published conformance requirements and generate a machine-readable report.

Think of it like ISO certification for a factory. ISO publishes the standard. Any factory can run the inspection against its own processes. If they pass, they get a certificate that says which standard they met, at which level, on which date. Customers can verify the claim by reading the report.

The AumOS Certified badge program works the same way:
- Conformance requirements are fully public — no secret thresholds
- The test runner is open source — you can read every check
- Badges are labeled "Self-Assessed" — they reflect your own test results, not a third-party audit
- Reports are machine-readable JSON — any system can parse and verify them

### What Happens Without This

Without a certification standard:
- Governance claims are unverifiable marketing
- Enterprise procurement cannot compare implementations
- Developers have no target to build toward
- The ecosystem fragments into incompatible "governance" implementations that share only the name

---

## Certification Levels

| Level    | Minimum Score | Required Protocols              | Badge Color |
|----------|---------------|----------------------------------|-------------|
| Bronze   | 60%           | ATP                              | `#CD7F32`   |
| Silver   | 75%           | ATP, AEAP, AOAP                  | `#C0C0C0`   |
| Gold     | 90%           | ATP, AIP, AEAP, AMGP, AOAP       | `#FFD700`   |
| Platinum | 95%           | ATP, AIP, ASP, AEAP, AMGP, AOAP, ALCP | `#E5E4E2` |

See [docs/certification-levels.md](docs/certification-levels.md) for full protocol requirements and scoring breakdown.

---

## Quick Start

### Prerequisites (Python CLI)

- Python 3.10+
- `pip install aumos-certify`
- An adapter file that wraps your governance implementation (see [docs/writing-an-adapter.md](docs/writing-an-adapter.md))

### Minimal Working Example — Python CLI

```bash
pip install aumos-certify

# Run conformance checks against your implementation
aumos-certify run --implementation path/to/adapter.py --level gold
```

Expected output:

```
AumOS Conformance Runner v0.1.0
Level target: Gold (90% required)

Running ATP checks.......... 10/10 passed
Running AIP checks.......... 8/9 passed
Running AEAP checks......... 9/9 passed
Running AMGP checks......... 7/8 passed
Running AOAP checks......... 6/6 passed

Overall score: 92.1%
Achieved level: Gold

Generating report: ./aumos-certification-report.json
```

**What just happened?**

1. The runner loaded conformance vectors for each required protocol.
2. It called your adapter for each check — your adapter translates the vector into a call to your implementation.
3. Results were scored against the Gold threshold (90%).
4. A machine-readable JSON report was written locally. No data was sent anywhere.

```bash
# Generate a badge SVG from the result
aumos-certify badge --level gold --output ./aumos-gold.svg

# Generate a human-readable Markdown report
aumos-certify report --format md

# Generate a machine-readable JSON report
aumos-certify report --format json
```

### Minimal Working Example — Badge Generator (TypeScript)

```bash
npm install @aumos/badge-generator
```

```typescript
import { generateBadge } from "@aumos/badge-generator";
import { writeFileSync } from "fs";

const svg = generateBadge("gold");
writeFileSync("aumos-certified-gold.svg", svg);
```

---

## Architecture Overview

```mermaid
graph TD
    A[aumos-certify CLI] --> B[ConformanceRunner]
    A --> C[CertificationScorer]
    A --> D[ReportGenerator]

    B --> E[Protocol Checks]
    E --> E1[atp.py]
    E --> E2[aip.py]
    E --> E3[aeap.py]
    E --> E4[amgp.py]
    E --> E5[aoap.py]

    B -->|calls| F[ImplementationAdapter<br/>your code here]
    F -->|results| C
    C --> G[CertificationResult<br/>level + score]
    G --> D
    D --> H1[Markdown Report<br/>local file]
    D --> H2[JSON Report<br/>local file]

    I[@aumos/badge-generator] --> J[SVG Badge<br/>Bronze / Silver / Gold / Platinum]

    style A fill:#4A90D9,color:#fff
    style B fill:#5CB85C,color:#fff
    style F fill:#F0AD4E,color:#fff
    style I fill:#9B59B6,color:#fff
```

Dependency direction flows one way: `cli → runner/scorer/report → types/levels → protocols`. Your adapter is the only external boundary — the runner calls it; everything else is local.

In the AumOS ecosystem, the certification toolkit is the quality gate: teams building on `aumos-core`, `aumos-sdks`, or any AumOS protocol implementation use the toolkit to verify they meet the published standard before shipping.

---

## Repository Structure

```
trust-certification-toolkit/
├── python/              # aumos-certify CLI package
│   └── src/aumos_certify/
│       ├── cli.py       # Typer CLI entry point
│       ├── runner.py    # ConformanceRunner
│       ├── scorer.py    # CertificationScorer
│       ├── report.py    # Markdown + JSON report generation
│       ├── levels.py    # Level definitions (Bronze–Platinum)
│       ├── types.py     # Pydantic models and interfaces
│       └── protocols/   # Per-protocol check implementations
├── badges/
│   ├── generator/       # @aumos/badge-generator TypeScript package
│   └── assets/          # Pre-generated SVG badge files
├── examples/            # Example: certifying the AumOS Python SDK
└── docs/                # Certification documentation
```

---

## Who Is This For?

**Developers** building governance-aware SDKs, agent frameworks, or MCP implementations who want a concrete target and a way to demonstrate compliance to their users.

**Enterprise teams** evaluating AI governance products who need a reproducible, auditable way to compare implementations against a published standard.

Both groups benefit from the fully open criteria: every check is in the source code, every threshold is in the docs, and every report is a local file you control.

---

## Related Projects

| Repo | How it relates |
|------|---------------|
| [aumos-core](https://github.com/aumos-ai/aumos-core) | The governance protocols this toolkit tests |
| [aumos-sdks](https://github.com/aumos-ai/aumos-sdks) | SDKs whose governance implementations can be certified |
| [mcp-server-trust-gate](https://github.com/aumos-ai/mcp-server-trust-gate) | MCP governance layer that can be certified with this toolkit |
| [aumos-edge-runtime](https://github.com/aumos-ai/aumos-edge-runtime) | Edge runtime that can be certified for offline governance |

---

## Fire Line

Self-assessment is LOCAL ONLY — no data is sent anywhere during any operation. See [FIRE_LINE.md](FIRE_LINE.md) for the complete scope boundary.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

Apache License, Version 2.0
See https://www.apache.org/licenses/LICENSE-2.0 for full text.
Copyright (c) 2026 MuVeraAI Corporation
