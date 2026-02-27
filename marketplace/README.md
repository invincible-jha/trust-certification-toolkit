# AumOS Certified Marketplace

The AumOS Certified Marketplace is a public directory of AI agents that have completed
the [AumOS Certified self-assessment](../docs/self-assessment.md). It allows vendors to
publicly declare their conformance level so that enterprise buyers can discover and
evaluate certified implementations.

## What the Marketplace Is

The marketplace is a **community-maintained directory of self-assessed agents**. Vendors
generate a conformance report using the `aumos-certify` CLI, compute a report hash for
integrity verification, and submit a listing JSON file that conforms to `schema.json`.

**All listings are self-assessed.** The AumOS team does not verify, audit, or endorse
any listing. The "Self-Assessed" label on all badges reflects this. See
[certification-fees.md](../docs/certification-fees.md) for information on the planned
verified certification tier (not yet available).

## How to Submit a Listing

### Step 1 — Run the self-assessment

```bash
pip install aumos-certify
aumos-certify run --implementation your_adapter.py --level silver
aumos-certify report --format json --output ./my-report.json
```

### Step 2 — Compute the report hash

```bash
# Linux / macOS
sha256sum ./my-report.json

# Windows (PowerShell)
Get-FileHash ./my-report.json -Algorithm SHA256
```

Copy the 64-character hex digest. This is your `report_hash`.

### Step 3 — Create your listing JSON

Create a file named `<your-agent-slug>.json` in this directory. The file must conform
to `schema.json`. Use `example-listing.json` as a starting point.

Required fields:

| Field | Description |
|---|---|
| `listing_id` | A UUID v4 you generate (e.g., via `python -c "import uuid; print(uuid.uuid4())"`) |
| `agent_name` | Human-readable name of your agent |
| `vendor` | Your organisation name |
| `certification_level` | `bronze`, `silver`, `gold`, or `platinum` |
| `certification_date` | ISO 8601 date of your assessment (YYYY-MM-DD) |
| `certification_expiry` | Two years from assessment date by convention |
| `protocols_passed` | Array of protocol IDs that passed (e.g., `["atp", "aeap", "aoap"]`) |
| `pass_rates` | Object mapping protocol ID to pass rate percentage |
| `self_assessed` | Must be `true` |
| `report_hash` | SHA-256 hex digest of your report JSON |

Optional fields: `description`, `badge_url`, `contact_url`, `tags`.

### Step 4 — Open a Pull Request

Submit your listing file via pull request to
`github.com/aumos-ai/trust-certification-toolkit`. The PR title should follow the
convention:

```
feat(marketplace): add listing for <agent-name> (<vendor>)
```

A maintainer will verify that:
- The JSON is valid against `schema.json`
- `self_assessed` is `true`
- The `listing_id` is unique
- No claim of AumOS verification is made

The report file referenced by `report_hash` does **not** need to be submitted —
only the hash is stored here.

## Keeping Your Listing Current

Listings expire on `certification_expiry`. Before that date, re-run your assessment,
update your listing JSON, and open a new PR. Expired listings are marked stale and
eventually removed.

## Important Notices

- **No AumOS verification is implied.** Listings represent the vendor's own assessment
  using the open-source `aumos-certify` tool.
- **Badges say "Self-Assessed".** Do not modify badge SVG text to remove or change
  this label.
- **The report hash enables independent verification.** Anyone with access to your
  report file can confirm it matches the hash on record.
- **Listings may be removed** if they are found to be materially inaccurate or if the
  vendor does not respond to a validity challenge within 30 days.

## Schema

The full JSON Schema is in `schema.json`. Validate your listing locally before
submitting:

```bash
pip install check-jsonschema
check-jsonschema --schemafile marketplace/schema.json marketplace/your-listing.json
```

---

Copyright (c) 2026 MuVeraAI Corporation. Apache-2.0 License.
