// SPDX-License-Identifier: Apache-2.0
// Copyright (c) 2026 MuVeraAI Corporation

import { z } from "zod";

/**
 * Recognised certification levels in the AumOS Certified badge program.
 * All criteria for each level are publicly documented in docs/certification-levels.md.
 */
export const CertificationLevelSchema = z.enum([
  "bronze",
  "silver",
  "gold",
  "platinum",
]);

export type CertificationLevel = z.infer<typeof CertificationLevelSchema>;

/**
 * Visual properties for each certification level.
 * Colors match the definitions in python/src/aumos_certify/levels.py.
 */
const LEVEL_CONFIG: Record<
  CertificationLevel,
  { color: string; label: string }
> = {
  bronze: { color: "#CD7F32", label: "Bronze" },
  silver: { color: "#C0C0C0", label: "Silver" },
  gold: { color: "#FFD700", label: "Gold" },
  platinum: { color: "#E5E4E2", label: "Platinum" },
};

/**
 * Options for badge generation.
 */
export interface BadgeOptions {
  /** Width of the badge in pixels. Default: 220. */
  readonly width?: number;
  /** Height of the badge in pixels. Default: 64. */
  readonly height?: number;
}

const BadgeOptionsSchema = z.object({
  width: z.number().int().positive().optional().default(220),
  height: z.number().int().positive().optional().default(64),
});

/**
 * Generate an SVG badge for the given certification level.
 *
 * The badge always carries the label "Self-Assessed" — it reflects the
 * implementer's own test results, not an official third-party audit.
 *
 * @param level   The certification level to render.
 * @param options Optional width/height overrides.
 * @returns       An SVG string ready to write to a .svg file or embed in HTML.
 *
 * @example
 * ```ts
 * import { generateBadge } from "@aumos/badge-generator";
 *
 * const svg = generateBadge("gold");
 * fs.writeFileSync("aumos-certified-gold.svg", svg);
 * ```
 */
export function generateBadge(
  level: CertificationLevel,
  options: BadgeOptions = {},
): string {
  const validated = CertificationLevelSchema.parse(level);
  const { width, height } = BadgeOptionsSchema.parse(options);

  const config = LEVEL_CONFIG[validated];
  const displayName = `AumOS Self-Assessed ${config.label}`;
  const leftWidth = Math.round(width * 0.5);
  const rightX = leftWidth;
  const rightWidth = width - leftWidth;
  const leftCenterX = Math.round(leftWidth / 2);
  const rightCenterX = rightX + Math.round(rightWidth / 2);
  const topTextY = Math.round(height * 0.34);
  const bottomTextY = Math.round(height * 0.59);

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" role="img" aria-label="${displayName}">
  <title>${displayName}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="${width}" height="${height}" rx="8" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="${leftWidth}" height="${height}" fill="#555"/>
    <rect x="${rightX}" width="${rightWidth}" height="${height}" fill="${config.color}"/>
    <rect width="${width}" height="${height}" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="12">
    <text x="${leftCenterX}" y="${topTextY - 1}" fill="#010101" fill-opacity=".3">AumOS</text>
    <text x="${leftCenterX}" y="${topTextY - 2}">AumOS</text>
    <text x="${leftCenterX}" y="${bottomTextY}" fill="#010101" fill-opacity=".3">Self-Assessed</text>
    <text x="${leftCenterX}" y="${bottomTextY - 1}">Self-Assessed</text>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="15" font-weight="bold">
    <text x="${rightCenterX}" y="${bottomTextY}" fill="#010101" fill-opacity=".3">${config.label}</text>
    <text x="${rightCenterX}" y="${bottomTextY - 1}">${config.label}</text>
  </g>
</svg>`;
}

/**
 * Return the display name for a certification level badge.
 *
 * @param level  The certification level.
 * @returns      The full display name, e.g. "AumOS Self-Assessed Gold".
 */
export function getBadgeDisplayName(level: CertificationLevel): string {
  const validated = CertificationLevelSchema.parse(level);
  const config = LEVEL_CONFIG[validated];
  return `AumOS Self-Assessed ${config.label}`;
}

/**
 * Return the badge color hex string for a certification level.
 *
 * @param level  The certification level.
 * @returns      Hex color string, e.g. "#FFD700".
 */
export function getBadgeColor(level: CertificationLevel): string {
  const validated = CertificationLevelSchema.parse(level);
  return LEVEL_CONFIG[validated].color;
}
