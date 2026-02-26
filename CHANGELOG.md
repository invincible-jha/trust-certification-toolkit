# Changelog

All notable changes to `trust-certification-toolkit` will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.1.0] — 2026-02-26

### Added

- `aumos-certify` Python CLI with `run`, `badge`, and `report` subcommands
- `ConformanceRunner` — executes per-protocol conformance checks against an
  `ImplementationAdapter`, returns structured `RunResult`
- `CertificationScorer` — deterministic mapping from `RunResult` to
  `CertificationResult` based on score threshold and required protocol list
- `CertificationLevel` enum: Bronze, Silver, Gold, Platinum with documented
  score thresholds and required protocol sets
- Per-protocol check modules: `atp`, `aip`, `aeap`, `amgp`, `aoap`, and
  `cross_protocol`
- `ReportGenerator` — produces Markdown and JSON certification reports offline
- `ImplementationAdapter` — generic abstract base for connecting any implementation
  to the runner; not AumOS-specific
- `@aumos/badge-generator` TypeScript package — `generateBadge()` produces SVG
  badges for each certification level
- Pre-generated SVG assets for Bronze, Silver, Gold, and Platinum levels
- Example: certifying the AumOS Python SDK (`examples/certify_sdk.py`)
- Documentation: certification levels, self-assessment guide, submission guide,
  and badge usage guide
- `scripts/fire-line-audit.sh` — forbidden identifier audit script
- Apache 2.0 license, `FIRE_LINE.md`, `CONTRIBUTING.md`

### Notes

- All self-assessment runs LOCAL ONLY — no network communication
- Badges are labeled "Self-Assessed" — not official third-party audits
- Certification criteria are fully public — no secret thresholds

[Unreleased]: https://github.com/aumos-ai/trust-certification-toolkit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/aumos-ai/trust-certification-toolkit/releases/tag/v0.1.0
