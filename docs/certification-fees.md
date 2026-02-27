# AumOS Certified — Fee Structure

This document describes the fee structure for the AumOS Certified badge program.

---

## Self-Assessment: Always Free

The self-assessment CLI tool (`aumos-certify`) is open source under the Apache-2.0
license. Running conformance checks, generating reports, and displaying the
"Self-Assessed" badge costs nothing — now and in the future.

```bash
pip install aumos-certify
aumos-certify run --implementation your_adapter.py --level gold
aumos-certify report --format md
```

There are no rate limits, no account requirements, and no telemetry. All
self-assessment processing happens locally on your machine.

---

## Verified Certification (Planned Feature)

> **Note:** Verified certification is a planned future feature. Only self-assessment
> is available today. This section documents the intended pricing for planning
> purposes — no verified certification service is currently operational.

Verified certification involves a review by the AumOS team, an independent compliance
report, and an upgrade of the badge label from "Self-Assessed" to "Verified".

### Standard Pricing (per agent, per year)

| Certification Level | Annual Fee |
|---|---|
| Bronze | $499 |
| Silver | $999 |
| Gold | $1,999 |
| Platinum | $4,999 |

Fees are invoiced annually per agent. Each agent requires a separate assessment.

### What Verified Certification Includes

- AumOS team review of your self-assessment report and adapter code
- Independent conformance report issued by MuVeraAI Corporation
- Badge upgrade: label changes from "Self-Assessed" to "Verified"
- Listing in the verified tier of the AumOS Certified Marketplace
- 12 months of validity from the date of the verified report
- One re-check during the validity period if you ship a conformance-relevant update

### What Verified Certification Does Not Include

- Access to proprietary AumOS product features
- SLA guarantees on your agent's runtime behaviour
- Any indemnification or warranty regarding the agent's actions

---

## Renewal Fees

Renewal fees apply to verified certification only. Self-assessment renewal is always
free — simply re-run the CLI and update your marketplace listing.

| Certification Level | Renewal Fee (per agent, per year) |
|---|---|
| Bronze | $249 |
| Silver | $499 |
| Gold | $999 |
| Platinum | $2,499 |

Renewal fees are 50% of the original certification fee. Renewals require a new
self-assessment run. The AumOS team will verify the updated report.

---

## Enterprise Fleet Pricing

Volume discounts apply to verified certification when an organisation certifies
multiple agents under a single enterprise agreement.

| Fleet Size | Discount |
|---|---|
| 10–49 agents | 15% off all levels |
| 50–99 agents | 25% off all levels |
| 100+ agents | 35% off all levels |

Discounts apply to both initial certification and renewal fees. Fleet pricing
requires a signed enterprise agreement. Contact your AumOS account representative
for a custom quote.

### Example: 20-agent fleet at Silver

Base fee per agent: $999
Discount (15%): −$150
Effective fee per agent: $849
Total for 20 agents: $16,980 per year

---

## Academic and Non-Profit Pricing

Qualifying academic institutions and registered non-profit organisations receive
a 50% discount on all verified certification tiers. The discount applies to both
initial certification and renewal fees.

To apply for the academic or non-profit rate, contact
[certification@aumos.ai](mailto:certification@aumos.ai) with:

- Proof of academic institution status (e.g., official domain, accreditation letter)
  or non-profit registration documents
- The agent name and intended certification level
- A brief description of the intended use

Self-assessment remains free for all organisations regardless of type.

---

## Summary Table

| Tier | Self-Assessment | Verified Certification |
|---|---|---|
| Bronze | Free | $499/agent/year |
| Silver | Free | $999/agent/year |
| Gold | Free | $1,999/agent/year |
| Platinum | Free | $4,999/agent/year |
| Renewal | Free | 50% of original fee |
| Enterprise (10+) | Free | 15% discount |
| Enterprise (50+) | Free | 25% discount |
| Enterprise (100+) | Free | 35% discount |
| Academic / Non-Profit | Free | 50% discount |

---

## Frequently Asked Questions

**Is the CLI tool ever going to have paid features?**
No. The `aumos-certify` CLI is open source and will remain free forever. Fees apply
only to the optional verified certification service, which involves human review.

**Can I display the self-assessed badge on a commercial product?**
Yes. The Apache-2.0 license permits commercial use. The badge must display the
"Self-Assessed" label — do not modify the badge SVG to remove or alter that label.

**What happens if my verified certification expires?**
Your badge reverts to the self-assessed tier. You can continue to display the
self-assessed badge as long as your self-assessment remains current. To restore
verified status, pay the renewal fee and submit an updated assessment report.

**When will verified certification be available?**
Verified certification is planned but has no confirmed launch date. Join the waitlist
at [aumos.ai/certified-waitlist](https://aumos.ai/certified-waitlist) to be notified.

---

*Copyright (c) 2026 MuVeraAI Corporation. Prices are in USD and subject to change.
Current pricing will always be listed at [aumos.ai/certified](https://aumos.ai/certified).*
