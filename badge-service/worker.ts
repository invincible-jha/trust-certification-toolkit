// SPDX-License-Identifier: BSL-1.1
// Copyright (c) 2026 MuVeraAI Corporation
/**
 * AumOS Badge Service — Cloudflare Worker
 *
 * Serves dynamically-generated SVG governance score badges at two routes:
 *   GET /score/:score   — numeric score badge  (e.g., /score/82)
 *   GET /cert/:level    — certification level badge (e.g., /cert/Gold)
 *
 * Deploy:
 *   wrangler deploy
 */

export default {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;

    // Route: /score/:score
    const scoreMatch = path.match(/^\/score\/(\d+)$/);
    if (scoreMatch) {
      const score = parseInt(scoreMatch[1], 10);
      const clampedScore = Math.min(100, Math.max(0, score));
      const level = scoreToLevel(clampedScore);
      const color = levelToColor(level);
      const svg = generateBadgeSvg("governance", `${clampedScore}/100 ${level}`, color);

      return new Response(svg, {
        headers: {
          "Content-Type": "image/svg+xml",
          "Cache-Control": "public, max-age=300",
        },
      });
    }

    // Route: /cert/:level
    const certMatch = path.match(/^\/cert\/(\w+)$/);
    if (certMatch) {
      const level = certMatch[1];
      const color = levelToColor(level);
      const svg = generateBadgeSvg("AumOS Certified", level, color);

      return new Response(svg, {
        headers: {
          "Content-Type": "image/svg+xml",
          "Cache-Control": "public, max-age=3600",
        },
      });
    }

    return new Response(
      "AumOS Badge Service. Use /score/:score or /cert/:level",
      { status: 200 },
    );
  },
};

function scoreToLevel(score: number): string {
  if (score >= 90) return "Platinum";
  if (score >= 75) return "Gold";
  if (score >= 50) return "Silver";
  if (score >= 25) return "Bronze";
  return "Unrated";
}

function levelToColor(level: string): string {
  const colors: Record<string, string> = {
    Platinum: "#e5e4e2",
    Gold: "#ffd700",
    Silver: "#c0c0c0",
    Bronze: "#cd7f32",
    Unrated: "#9e9e9e",
  };
  return colors[level] ?? "#9e9e9e";
}

function generateBadgeSvg(label: string, value: string, color: string): string {
  const labelWidth = label.length * 7 + 12;
  const valueWidth = value.length * 7 + 12;
  const totalWidth = labelWidth + valueWidth;

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${totalWidth}" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <mask id="a"><rect width="${totalWidth}" height="20" rx="3" fill="#fff"/></mask>
  <g mask="url(#a)">
    <rect width="${labelWidth}" height="20" fill="#555"/>
    <rect x="${labelWidth}" width="${valueWidth}" height="20" fill="${color}"/>
    <rect width="${totalWidth}" height="20" fill="url(#b)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="${labelWidth / 2}" y="15" fill="#010101" fill-opacity=".3">${label}</text>
    <text x="${labelWidth / 2}" y="14">${label}</text>
    <text x="${labelWidth + valueWidth / 2}" y="15" fill="#010101" fill-opacity=".3">${value}</text>
    <text x="${labelWidth + valueWidth / 2}" y="14">${value}</text>
  </g>
</svg>`;
}
