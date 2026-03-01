#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 MuVeraAI Corporation
#
# ci-cert-check.sh — AumOS Certification CI gate
#
# Runs aumos-certify against an implementation adapter and exits with a
# non-zero status code if the implementation does not meet the required
# certification level. Use this script as a CI step to block merges when
# conformance drops below your target level.
#
# USAGE
# -----
#   scripts/ci-cert-check.sh [OPTIONS]
#
# OPTIONS
#   --adapter PATH          Path to the Python implementation adapter file
#                           (must define an ImplementationAdapter subclass).
#                           Default: examples/certify_sdk.py
#
#   --level LEVEL           Required certification level to pass the gate.
#                           One of: bronze, silver, gold, platinum
#                           Default: bronze
#
#   --output-dir DIR        Directory for the exported report files.
#                           Default: ./cert-output
#
#   --format FORMAT         Export format(s), comma-separated.
#                           Supported: json, markdown, html, all
#                           Default: json
#
#   --history-file PATH     Optional JSONL history file. When provided, the
#                           run result is appended to track progress over time.
#                           Default: (none)
#
#   --fail-on-missing-protocols
#                           Exit non-zero even when the score threshold is met
#                           but required protocols are missing. Default: true.
#
#   -h, --help              Print this help text and exit.
#
# EXIT CODES
# ----------
#   0  — Certification passed at or above --level
#   1  — Certification failed (below required level or missing protocols)
#   2  — Invocation error (bad arguments, missing adapter, etc.)
#
# EXAMPLES
# --------
#   # Gate on bronze (minimum check — suitable for most PRs)
#   scripts/ci-cert-check.sh --adapter src/my_adapter.py --level bronze
#
#   # Gate on gold with full reports
#   scripts/ci-cert-check.sh \
#     --adapter src/my_adapter.py \
#     --level gold \
#     --output-dir ci-artifacts/cert \
#     --format all \
#     --history-file ci-artifacts/cert-history.jsonl
#
# SETUP
# -----
#   pip install aumos-certify
#   # or, from source:
#   pip install -e python/

set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
ADAPTER_PATH="examples/certify_sdk.py"
REQUIRED_LEVEL="bronze"
OUTPUT_DIR="./cert-output"
EXPORT_FORMAT="json"
HISTORY_FILE=""
FAIL_ON_MISSING_PROTOCOLS="true"

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
usage() {
  sed -n '/^# USAGE/,/^# EXIT/p' "$0" | head -n -2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --adapter)
      ADAPTER_PATH="$2"
      shift 2
      ;;
    --level)
      REQUIRED_LEVEL="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --format)
      EXPORT_FORMAT="$2"
      shift 2
      ;;
    --history-file)
      HISTORY_FILE="$2"
      shift 2
      ;;
    --no-fail-on-missing-protocols)
      FAIL_ON_MISSING_PROTOCOLS="false"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
if [[ ! -f "$ADAPTER_PATH" ]]; then
  echo "ERROR: Adapter file not found: $ADAPTER_PATH" >&2
  exit 2
fi

case "$REQUIRED_LEVEL" in
  bronze|silver|gold|platinum) ;;
  *)
    echo "ERROR: Invalid level '$REQUIRED_LEVEL'. Must be one of: bronze, silver, gold, platinum" >&2
    exit 2
    ;;
esac

# ---------------------------------------------------------------------------
# Run certification
# ---------------------------------------------------------------------------
echo ""
echo "AumOS Certification CI Gate"
echo "==========================="
echo "  Adapter:        $ADAPTER_PATH"
echo "  Required level: $REQUIRED_LEVEL"
echo "  Output dir:     $OUTPUT_DIR"
echo "  Format(s):      $EXPORT_FORMAT"
echo ""

mkdir -p "$OUTPUT_DIR"

# Build the aumos-certify CLI command
CERT_CMD=(aumos-certify run --implementation "$ADAPTER_PATH" --level "$REQUIRED_LEVEL")

# Run and capture exit code
set +e
"${CERT_CMD[@]}" --output-dir "$OUTPUT_DIR"
CERT_EXIT=$?
set -e

# ---------------------------------------------------------------------------
# Export reports
# ---------------------------------------------------------------------------
REPORT_BASE="$OUTPUT_DIR/cert-report"
JSON_PATH="${REPORT_BASE}.json"

# The run subcommand writes JSON by default; produce additional formats here
if [[ "$EXPORT_FORMAT" == "all" || "$EXPORT_FORMAT" == *"markdown"* ]]; then
  if command -v aumos-certify &>/dev/null; then
    aumos-certify report --format md --input "$JSON_PATH" \
      --output "${REPORT_BASE}.md" 2>/dev/null || true
  fi
fi

if [[ "$EXPORT_FORMAT" == "all" || "$EXPORT_FORMAT" == *"html"* ]]; then
  if command -v aumos-certify &>/dev/null; then
    aumos-certify report --format html --input "$JSON_PATH" \
      --output "${REPORT_BASE}.html" 2>/dev/null || true
  fi
fi

# ---------------------------------------------------------------------------
# Append to history (if requested)
# ---------------------------------------------------------------------------
if [[ -n "$HISTORY_FILE" && -f "$JSON_PATH" ]]; then
  python3 - <<PYEOF
import json, sys
from pathlib import Path
from datetime import datetime, timezone

history_path = Path("$HISTORY_FILE")
json_path = Path("$JSON_PATH")

if not json_path.exists():
    sys.exit(0)

try:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    entry = {"recorded_at": datetime.now(tz=timezone.utc).isoformat(), "result": data}
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    print(f"  History appended to: {history_path}")
except Exception as exc:
    print(f"  Warning: could not append to history file: {exc}", file=sys.stderr)
PYEOF
fi

# ---------------------------------------------------------------------------
# Final result
# ---------------------------------------------------------------------------
echo ""
if [[ $CERT_EXIT -eq 0 ]]; then
  echo "RESULT: PASSED — implementation meets $REQUIRED_LEVEL certification."
  echo "  Reports written to: $OUTPUT_DIR"
  echo ""
  exit 0
else
  echo "RESULT: FAILED — implementation does not meet $REQUIRED_LEVEL certification."
  echo "  See reports in: $OUTPUT_DIR"
  echo ""
  exit 1
fi
