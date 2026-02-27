# Governance Score Badge

The AumOS governance score badge lets you display your agent's governance
posture in any README, documentation site, or CI dashboard. Scores are
computed locally using the `governance_score` module and then rendered on
demand by the hosted badge service at `badge.aumos.ai`.

---

## Quick start

### 1. Compute your governance score

```python
from governance_score import GovernanceProfile, compute_governance_score

profile = GovernanceProfile(
    has_trust_levels=True,
    trust_level_coverage_pct=88.0,
    has_budget_enforcement=True,
    budget_coverage_pct=80.0,
    has_consent_management=True,
    consent_coverage_pct=90.0,
    has_audit_trail=True,
    audit_coverage_pct=85.0,
    linter_warnings=3,
    linter_total_checks=100,
    has_conformance_tests=True,
    conformance_level="standard",
    has_shadow_mode=True,
)

result = compute_governance_score(profile)
print(f"Score: {result.overall}/100  Level: {result.level}")
print(f"Badge: {result.badge_url}")
```

### 2. Embed the badge in your README

Once you have the score, embed the hosted badge using a Markdown image link:

```markdown
![AumOS Governance Score](https://badge.aumos.ai/score/82)
```

Or link directly to the certification level badge:

```markdown
![AumOS Certified Gold](https://badge.aumos.ai/cert/Gold)
```

---

## Scoring model

The overall score (0–100) is a weighted average of five governance dimensions,
with optional bonuses for conformance test coverage and shadow-mode adoption.

| Dimension          | Weight |
| ------------------ | ------ |
| Trust level coverage  | 25 %   |
| Budget enforcement    | 20 %   |
| Consent management    | 20 %   |
| Audit trail coverage  | 25 %   |
| Linter pass rate      | 10 %   |

### Bonus points

| Feature                                   | Bonus |
| ----------------------------------------- | ----- |
| Conformance tests — basic                 | +2    |
| Conformance tests — standard              | +5    |
| Conformance tests — full                  | +10   |
| Shadow mode enabled                       | +3    |

Bonus points are capped so the total cannot exceed 100.

---

## Certification levels

| Level    | Score range |
| -------- | ----------- |
| Platinum | 90–100      |
| Gold     | 75–89       |
| Silver   | 50–74       |
| Bronze   | 25–49       |
| Unrated  | 0–24        |

---

## Hosted badge service

The badge service is a Cloudflare Worker deployed at `badge.aumos.ai`.

### Routes

| Route            | Description                                         | Cache TTL |
| ---------------- | --------------------------------------------------- | --------- |
| `/score/:score`  | Score badge — e.g., `/score/82` renders `82/100 Gold` | 5 min     |
| `/cert/:level`   | Level badge — e.g., `/cert/Gold`                    | 60 min    |

### Badge colours

| Level    | Colour      |
| -------- | ----------- |
| Platinum | `#e5e4e2`   |
| Gold     | `#ffd700`   |
| Silver   | `#c0c0c0`   |
| Bronze   | `#cd7f32`   |
| Unrated  | `#9e9e9e`   |

---

## Self-hosting the badge service

The Cloudflare Worker source lives in `badge-service/`.

```bash
cd badge-service/
npm install -g wrangler
wrangler deploy
```

The `wrangler.toml` in that directory controls the worker name and entry point.
Update the `name` field if you want to deploy under a different subdomain.

---

## GovernanceProfile reference

| Field                    | Type    | Description |
| ------------------------ | ------- | ----------- |
| `has_trust_levels`       | `bool`  | Agent has at least one trust level configured |
| `trust_level_coverage_pct` | `float` | Percentage of tool calls covered by a trust level |
| `has_budget_enforcement` | `bool`  | Agent enforces spending budgets on operations |
| `budget_coverage_pct`    | `float` | Percentage of spending-capable operations covered |
| `has_consent_management` | `bool`  | Agent performs consent checks before data-sensitive actions |
| `consent_coverage_pct`   | `float` | Percentage of data-sensitive operations covered |
| `has_audit_trail`        | `bool`  | Agent emits audit log entries for operations |
| `audit_coverage_pct`     | `float` | Percentage of operations that produce audit records |
| `linter_warnings`        | `int`   | Number of linter warnings in the latest scan |
| `linter_total_checks`    | `int`   | Total number of linter checks executed |
| `has_conformance_tests`  | `bool`  | Agent ships AumOS conformance tests |
| `conformance_level`      | `str`   | `"none"` / `"basic"` / `"standard"` / `"full"` |
| `has_shadow_mode`        | `bool`  | Agent supports governance shadow / dry-run mode |

---

## Example output

```
Score  : 82/100
Level  : Gold
Badge  : https://badge.aumos.ai/score/82

Dimension breakdown:
  Trust coverage  : 88/100
  Budget coverage : 80/100
  Consent         : 90/100
  Audit           : 85/100
  Linter score    : 97/100
```

See `examples/score-example.py` for a runnable demonstration covering
well-governed, partially-governed, and ungoverned agent profiles.

---

## License

BSL-1.1 — Copyright (c) 2026 MuVeraAI Corporation.
