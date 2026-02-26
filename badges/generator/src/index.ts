// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 MuVeraAI Corporation

/**
 * @aumos/badge-generator — SVG badge generator for the AumOS Certified badge program.
 *
 * All generated badges carry the label "Self-Assessed" to reflect that results
 * come from the implementer's own conformance run, not a third-party audit.
 *
 * @example
 * ```ts
 * import { generateBadge, getBadgeDisplayName, getBadgeColor } from "@aumos/badge-generator";
 *
 * const svg = generateBadge("gold");
 * fs.writeFileSync("aumos-certified-gold.svg", svg);
 * ```
 */

export {
  generateBadge,
  getBadgeDisplayName,
  getBadgeColor,
  CertificationLevelSchema,
} from "./badge.js";

export type { CertificationLevel, BadgeOptions } from "./badge.js";
