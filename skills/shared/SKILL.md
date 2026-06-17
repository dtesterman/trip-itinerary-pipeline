---
name: shared
description: >
  Shared reference files used by trip-planner and trip-exporter
  skills. Contains the TripData schema (trip-data-schema.md) which serves as the
  interface contract between all trip planning stages. This is not a standalone
  skill — do not trigger it directly. It exists solely so sibling skills can
  reference its files via $SKILL_DIR/../shared/references/.
---

# Shared References

This directory holds reference files shared across multiple trip planning skills.
It is not a standalone skill and should never be triggered directly.

## Contents

- `references/trip-data-schema.md` — Complete TripData TypeScript type definitions,
  field-by-field tables, and example JSON. This is the interface contract that
  trip-planner uses to validate plans and trip-exporter uses to generate JSON.
