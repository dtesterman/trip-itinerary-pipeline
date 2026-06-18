#!/bin/bash
set -e

# Regenerates trips.js loader from *.trip.js files in the target directory.
# The newest trip file (specified as $2) is placed first in the loading order.
#
# Usage:
#   bash scripts/regenerate-loader.sh <output-dir> [newest-trip-file]
#
# Example:
#   bash scripts/regenerate-loader.sh ./my-trips galena-2026.trip.js
#
# Note: the output dir must NOT be the public viewer/ template — the guard below
# rejects any dir named "viewer". Run scripts/setup-workspace.sh once and use
# my-trips/ instead. (If no *.trip.js files are present in the target dir, the
# existing trips.js there is removed — see below.)
#
# Output: <output-dir>/trips.js

OUTPUT_DIR="${1:?Usage: regenerate-loader.sh <output-dir> [newest-trip-file]}"
NEWEST="${2:-}"

if [ ! -d "$OUTPUT_DIR" ]; then
  echo "Error: Directory not found: $OUTPUT_DIR"
  exit 1
fi

# Guard: never regenerate the loader inside the public viewer/ template. This sits
# before the rm -f path below, so it can never delete the committed viewer/trips.js.
if [ "$(basename "$OUTPUT_DIR")" = "viewer" ]; then
  echo "Error: viewer/ is the public, read-only template — do not regenerate its loader." >&2
  echo "  Run 'bash scripts/setup-workspace.sh' once, then use my-trips/ as the output dir." >&2
  exit 1
fi

TRIPS_JS="$OUTPUT_DIR/trips.js"

# Find all *.trip.js files
TRIP_FILES=()
for f in "$OUTPUT_DIR"/*.trip.js; do
  [ -f "$f" ] && TRIP_FILES+=("$(basename "$f")")
done

if [ ${#TRIP_FILES[@]} -eq 0 ]; then
  echo "No *.trip.js files found in $OUTPUT_DIR"
  rm -f "$TRIPS_JS"
  exit 0
fi

# Build the loader: newest first, then all others in existing order
{
  echo "// trips.js — auto-generated loader, do not edit"
  echo "// Loads all trip data files. First entry is the most recent trip."
  echo "window.__TRIPS__ = window.__TRIPS__ || [];"

  # Newest first (if specified and exists)
  if [ -n "$NEWEST" ] && [ -f "$OUTPUT_DIR/$NEWEST" ]; then
    echo "document.write('<script src=\"$NEWEST\"><\\/script>');"
  fi

  # All others (skip the newest since it's already first)
  for f in "${TRIP_FILES[@]}"; do
    if [ "$f" != "$NEWEST" ]; then
      echo "document.write('<script src=\"$f\"><\\/script>');"
    fi
  done
} > "$TRIPS_JS"

echo "Loader written: $TRIPS_JS (${#TRIP_FILES[@]} trip files)"
cat "$TRIPS_JS"
