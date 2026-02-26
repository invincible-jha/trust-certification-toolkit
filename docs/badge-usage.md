# Displaying AumOS Certified Badges

After running a passing self-assessment, add a badge to your project README to signal
your conformance level to users and contributors.

## Generate your badge SVG

Use the CLI to generate a badge SVG at the level you achieved:

```bash
aumos-certify badge --level silver --output ./badges/aumos-certified-silver.svg
```

Or use the pre-built static assets from this repository:

```
badges/assets/aumos-certified-bronze.svg
badges/assets/aumos-certified-silver.svg
badges/assets/aumos-certified-gold.svg
badges/assets/aumos-certified-platinum.svg
```

## Add the badge to your README

Copy the generated SVG into your repository (for example, into a `badges/` or `docs/`
directory), then reference it in your README using a Markdown image tag:

```markdown
![AumOS Self-Assessed | Silver](./badges/aumos-certified-silver.svg)
```

To make the badge clickable and link to the certification criteria:

```markdown
[![AumOS Self-Assessed | Silver](./badges/aumos-certified-silver.svg)](https://github.com/aumos-ai/trust-certification-toolkit/blob/main/docs/certification-levels.md)
```

## Using the TypeScript badge generator

If you generate badges programmatically (for example, in a documentation build script),
install the `@aumos/badge-generator` package:

```bash
npm install @aumos/badge-generator
```

Then generate SVG strings in code:

```typescript
import { generateBadge } from "@aumos/badge-generator";
import fs from "node:fs";

const svg = generateBadge("silver");
fs.writeFileSync("aumos-certified-silver.svg", svg);
```

The generator validates the level argument at runtime using Zod and returns a complete
SVG string ready to write to a file or embed directly in HTML.

## Badge specifications

| Level | Color | Left label | Right label |
|-------|-------|------------|-------------|
| Bronze | `#CD7F32` | AumOS Self-Assessed | Bronze |
| Silver | `#C0C0C0` | AumOS Self-Assessed | Silver |
| Gold | `#FFD700` | AumOS Self-Assessed | Gold |
| Platinum | `#E5E4E2` | AumOS Self-Assessed | Platinum |

Badges are 220 x 20 px by default (shields.io-style). The width and height can be
overridden via the `BadgeOptions` parameter when using the TypeScript generator.

## Honest labelling

All badges produced by this toolkit include "Self-Assessed" in the label. This is
intentional — it accurately represents that the result comes from your own conformance
run, not a third-party audit.

Do not alter the badge label to remove or replace "Self-Assessed" when distributing the
badge. See `docs/submission.md` for information on officially audited certification
(a future commercial offering).
