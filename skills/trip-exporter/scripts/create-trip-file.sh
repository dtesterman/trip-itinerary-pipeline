#!/bin/bash
set -e

# Converts a trip-data.json into a self-registering *.trip.js file
# that pushes onto window.__TRIPS__.
#
# Usage:
#   bash scripts/create-trip-file.sh <trip-data.json> <slug> <output-dir>
#
# Example:
#   bash scripts/create-trip-file.sh galena-trip.json galena-2026 my-trips
#
# Tip: run scripts/validate-trip.sh on the JSON first — this script only wraps it.
#
# Note: <output-dir> is REQUIRED — there is intentionally no default, so the
# script never writes into the current directory implicitly. Use an explicit
# private workspace, normally my-trips/. The output dir must NOT resolve to the
# public viewer/ template (it ships the samples and is read-only); the guard below
# rejects viewer/ under any spelling (viewer, viewer/, viewer/., ./viewer, or an
# equivalent absolute path) by comparing resolved absolute physical paths.
#
# Output: <output-dir>/<slug>.trip.js

TRIP_JSON="${1:?Usage: create-trip-file.sh <trip-data.json> <slug> <output-dir>}"
SLUG="${2:?Usage: create-trip-file.sh <trip-data.json> <slug> <output-dir>}"
OUTPUT_DIR="${3:?Usage: create-trip-file.sh <trip-data.json> <slug> <output-dir> (required — use a private workspace such as my-trips)}"

if [ ! -f "$TRIP_JSON" ]; then
  echo "Error: Trip data file not found: $TRIP_JSON"
  exit 1
fi

# Guard: never author trips into the public viewer/ template — or any path under
# it. Compare resolved absolute physical paths so no spelling of "viewer"
# (viewer/, viewer/., ./viewer, viewer/sub, absolute paths, symlinks) can slip
# past a name-only check. This runs BEFORE mkdir -p so a rejected viewer/<sub> is
# never created on disk.
#
# Resolving the FINAL path component matters: if OUTPUT_DIR already exists, resolve
# it directly (cd into it; pwd -P dereferences a symlink and "." to the physical
# target) — otherwise a symlink named e.g. "out" -> viewer/ would write through into
# the template. Only for a not-yet-existing OUTPUT_DIR do we resolve via the parent
# plus the literal basename (there is no symlink final component to follow then).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
VIEWER_DIR="$(cd "$SCRIPT_DIR/../../../viewer" 2>/dev/null && pwd -P || true)"
if [ -e "$OUTPUT_DIR" ]; then
  OUTPUT_DIR_ABS="$(cd "$OUTPUT_DIR" && pwd -P)"
else
  OUT_PARENT="$(cd "$(dirname "$OUTPUT_DIR")" 2>/dev/null && pwd -P || true)"
  if [ -z "$OUT_PARENT" ]; then
    echo "Error: parent directory of '$OUTPUT_DIR' does not exist." >&2
    exit 1
  fi
  OUTPUT_DIR_ABS="$OUT_PARENT/$(basename "$OUTPUT_DIR")"
fi
if [ -n "$VIEWER_DIR" ] && { [ "$OUTPUT_DIR_ABS" = "$VIEWER_DIR" ] || [ "${OUTPUT_DIR_ABS#"$VIEWER_DIR"/}" != "$OUTPUT_DIR_ABS" ]; }; then
  echo "Error: viewer/ is the public, read-only template — do not write trips there or under it." >&2
  echo "  Run 'bash scripts/setup-workspace.sh' once, then use my-trips/ as the output dir." >&2
  exit 1
fi

# Create the destination now that the guard has accepted it.
mkdir -p "$OUTPUT_DIR"

OUTPUT_FILE="$OUTPUT_DIR/${SLUG}.trip.js"

node -e "
const fs = require('fs');
const json = fs.readFileSync(process.argv[1], 'utf8');
// Validate it's valid JSON
JSON.parse(json);
const content = 'window.__TRIPS__ = window.__TRIPS__ || [];\nwindow.__TRIPS__.push(' + json.trim() + ');\n';
fs.writeFileSync(process.argv[2], content);
" "$TRIP_JSON" "$OUTPUT_FILE"

FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
echo "Trip file created: $OUTPUT_FILE ($FILE_SIZE)"
