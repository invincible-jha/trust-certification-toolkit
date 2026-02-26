# AumOS Trust Certification Toolkit

Self-assessment tools, conformance test automation, badge generation, and certification
submission for the "AumOS Certified" badge program.

**Package:** `aumos-certify` (Python CLI) + `@aumos/badge-generator` (TypeScript)
**License:** Apache 2.0
**Status:** v0.1.0

---

## Overview

The Trust Certification Toolkit allows any AumOS protocol implementation to self-assess
against the published conformance requirements and generate a machine-readable
certification report. Badges are labeled **"Self-Assessed"** — they reflect the
implementer's own test results, not an official third-party audit.

Certification criteria are fully public. There are no secret thresholds.

---

## Certification Levels

| Level    | Minimum Score | Required Protocols              | Badge Color |
|----------|---------------|----------------------------------|-------------|
| Bronze   | 60%           | ATP                              | `#CD7F32`   |
| Silver   | 75%           | ATP, AEAP, AOAP                  | `#C0C0C0`   |
| Gold     | 90%           | ATP, AIP, AEAP, AMGP, AOAP       | `#FFD700`   |
| Platinum | 95%           | ATP, AIP, ASP, AEAP, AMGP, AOAP, ALCP | `#E5E4E2` |

See [docs/certification-levels.md](docs/certification-levels.md) for full details.

---

## Quick Start

### Python CLI

```bash
pip install aumos-certify

# Run conformance checks against your implementation
aumos-certify run --implementation path/to/adapter.py --level gold

# Generate a badge SVG
aumos-certify badge --level silver --output ./aumos-silver.svg

# Generate a certification report
aumos-certify report --format md
aumos-certify report --format json
```

### Badge Generator (TypeScript)

```bash
npm install @aumos/badge-generator

import { generateBadge } from "@aumos/badge-generator";

const svg = generateBadge("gold");
fs.writeFileSync("aumos-certified-gold.svg", svg);
```

---

## Architecture

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

## Fire Line

Self-assessment is LOCAL ONLY — no data is sent anywhere.
See [FIRE_LINE.md](FIRE_LINE.md) for the complete scope boundary.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

Apache License, Version 2.0
See https://www.apache.org/licenses/LICENSE-2.0 for full text.
Copyright (c) 2026 MuVeraAI Corporation
