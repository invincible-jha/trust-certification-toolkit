#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
#
# fire-line-audit.sh — Scan all source files for forbidden identifiers.
# Exits with code 1 if any forbidden identifier is found.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

FORBIDDEN=(
  "progressLevel"
  "promoteLevel"
  "computeTrustScore"
  "behavioralScore"
  "adaptiveBudget"
  "optimizeBudget"
  "predictSpending"
  "detectAnomaly"
  "generateCounterfactual"
  "PersonalWorldModel"
  "MissionAlignment"
  "SocialTrust"
  "CognitiveLoop"
  "AttentionFilter"
  "GOVERNANCE_PIPELINE"
)

SCAN_DIRS=(
  "${REPO_ROOT}/python/src"
  "${REPO_ROOT}/badges/generator/src"
  "${REPO_ROOT}/examples"
)

FOUND=0

for dir in "${SCAN_DIRS[@]}"; do
  if [[ ! -d "${dir}" ]]; then
    continue
  fi

  for identifier in "${FORBIDDEN[@]}"; do
    matches=$(grep -rn --include="*.py" --include="*.ts" \
      "${identifier}" "${dir}" 2>/dev/null || true)

    if [[ -n "${matches}" ]]; then
      echo "FIRE LINE VIOLATION: forbidden identifier '${identifier}' found:"
      echo "${matches}"
      FOUND=1
    fi
  done
done

if [[ "${FOUND}" -eq 1 ]]; then
  echo ""
  echo "Fire line audit FAILED. Remove all forbidden identifiers before committing."
  exit 1
fi

echo "Fire line audit passed — no forbidden identifiers found."
exit 0
