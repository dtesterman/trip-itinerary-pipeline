#!/bin/bash
set -e

# Bootstraps your PRIVATE trip workspace from the public viewer template.
# Copies the prebuilt viewer shell into my-trips/ so your authored trips can be
# co-located with it (the viewer loads trips.js + *.trip.js from its own folder).
# Safe to re-run: never overwrites an existing copy.
#
# Usage:
#   bash scripts/setup-workspace.sh

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE="$REPO_DIR/my-trips"
TEMPLATE="$REPO_DIR/viewer/trip-viewer.html"

if [ ! -f "$TEMPLATE" ]; then
  echo "Error: viewer template not found: $TEMPLATE" >&2
  exit 1
fi

mkdir -p "$WORKSPACE"
if [ -f "$WORKSPACE/trip-viewer.html" ]; then
  echo "Workspace already set up: $WORKSPACE/trip-viewer.html exists. Nothing to do."
else
  cp "$TEMPLATE" "$WORKSPACE/trip-viewer.html"
  echo "Copied viewer shell -> $WORKSPACE/trip-viewer.html"
fi
echo "Your private workspace is ready: $WORKSPACE"
echo "Author trips here; open $WORKSPACE/trip-viewer.html to view them."
