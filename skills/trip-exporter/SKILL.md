---
name: trip-exporter
description: >
  Converts a completed vacation plan into trip data files for the interactive
  trip viewer. Generates trip-data.json conforming to the TripData schema, then
  produces a .trip.js file and updates trips.js so trip-viewer.html automatically
  loads the new trip without rebuilding. Optionally creates a standalone HTML
  file with embedded data for sharing.

  Use this skill whenever the user has a completed trip plan and wants to create
  the viewer files. Trigger on: "export the trip", "create the itinerary",
  "generate the trip data", "add to my trips", "add to my collection",
  "package the trip", "make it shareable", "I'm done planning, export it",
  "create the trip files", or any reference to converting a plan into viewable
  format. Also trigger when trip-planner hands off a completed plan, or when
  the user says "here's the plan, make it interactive". For standalone HTML,
  trigger on: "make a standalone file", "single file I can email",
  "self-contained HTML".
---

# Trip Exporter

Convert a completed vacation plan into machine-readable trip data and deliver it
as files that trip-viewer.html loads automatically.

## Prerequisites

1. **A completed vacation plan** — either from the trip-planner skill, in
   conversation context, or uploaded as a document. The plan must include:
   trip name, dates, traveler count, airports, day-by-day itinerary with stops,
   and cost estimates.

2. **This skill's bundled assets and scripts** — located relative to SKILL.md:
   - `assets/bundle-shell.html` — pre-built app shell (~594 KB)
   - `scripts/create-trip-file.sh` — wraps JSON in `window.__TRIPS__.push()`
   - `scripts/regenerate-loader.sh` — regenerates trips.js from all .trip.js files
   - `scripts/inject-trip-data.sh` — embeds JSON into standalone HTML (optional path)

---

## Workflow

### Step 1 — Generate trip-data.json

Convert the vacation plan into JSON conforming to the TripData schema
(see `$SKILL_DIR/../shared/references/trip-data-schema.md` for complete type
definitions and field-by-field guidance).

Key rules:

- **Every stop needs an `id`** in format `d{dayNumber}-s{stopIndex}` (e.g., `d1-s1`)
- **`coords` (lat/lng) are strongly recommended** for maps and route links. Look up
  approximate coordinates for each place. They are *optional*: a stop without coords
  is still valid — it simply won't render as a map pin (fine for meals, drives, or
  transit-only entries).
- **`placeholderEmoji`** is required — pick contextually relevant emoji
  (see schema reference for common emoji table)
- **`mapUrl`** should be a Google Maps search URL for the location
- **Cost estimates** need all three tiers: `budget`, `mid`, `high`
- **Day categories** must be one of: `travel`, `history`, `nature`, `driving`,
  `mixed`, `departure`
- **Stop status** should be `planned` for new trips
- **Travel-day logistics stops** (depart home, airport parking/rideshare, rental/Turo
  pickup & return, arrive home) are ordinary stops — preserve them as-is using the same
  `id`/emoji conventions (see the "Travel-day logistics stops" note in the schema
  reference); their parking/rideshare/rental costs belong in the "Ground transportation"
  cost category

Validate the JSON against the schema contract **before** wrapping it. This checks
required fields, valid enum values (`category`, `pricing.type`, `status`,
line-item `priceType`), `id` format and uniqueness, and that cost `totals` equal
the sum of all line items. Missing `coords` are reported as warnings, not errors:

```bash
SKILL_DIR="<path-to-this-skill>"
bash "$SKILL_DIR/scripts/validate-trip.sh" trip-data.json
```

Fix every `FAIL:` line before continuing; review any `WARN:` lines and confirm
they're intentional. Do not proceed to Step 2 until validation passes.

### Step 2 — Create .trip.js file (default output)

Use the script bundled with this skill to wrap the JSON in a self-registering
format that pushes onto `window.__TRIPS__`:

```bash
SKILL_DIR="<path-to-this-skill>"
bash "$SKILL_DIR/scripts/create-trip-file.sh" trip-data.json SLUG-YEAR my-trips
```

Where `SLUG-YEAR` is a short identifier like `lakes-loop-2027` or `coast-weekender-2027`.
The output dir (`my-trips`) is **required** — `create-trip-file.sh` has no default and
will not write to the current directory implicitly. Always pass your private
workspace (`my-trips`); never `viewer` (the script rejects `viewer/`, and any path
under it, under every spelling).
Output: `my-trips/SLUG-YEAR.trip.js`

### Step 3 — Regenerate trips.js loader

Update the loader so trip-viewer.html discovers the new trip automatically:

```bash
bash "$SKILL_DIR/scripts/regenerate-loader.sh" my-trips SLUG-YEAR.trip.js
```

The new trip file is placed first in the loader (most recent trip). Pass the same
private workspace (`my-trips`) here; `viewer/` and any subdirectory under it are
rejected under every spelling.
Output: `my-trips/trips.js`

### Step 4 — Create standalone HTML (only on explicit request)

If the user explicitly asks for a standalone/self-contained file they can share
via email or view offline:

```bash
bash "$SKILL_DIR/scripts/inject-trip-data.sh" trip-data.json itinerary-SLUG.html
```

This embeds the JSON directly into bundle-shell.html, producing a single file
that needs no other files to work. The script automatically finds
`assets/bundle-shell.html` relative to itself.

Only run this step when the user asks for it. The primary delivery path is
Steps 2-3 (dynamic loading via trips.js).

### Step 5 — Deliver to your private trip workspace

**Before writing outputs, ensure the workspace exists:** if
`my-trips/trip-viewer.html` is absent, run `bash scripts/setup-workspace.sh` from
the repo root. It copies the prebuilt viewer shell from the public `viewer/`
template into `my-trips/`, so your trips sit next to their own copy of the viewer
(the loader resolves `trips.js` and each `*.trip.js` by same-folder relative path).

Write the outputs into **`my-trips/`** — your private, gitignored workspace. Use
`my-trips/` as the `OUTPUT_DIR` in Steps 2–3 so the files land directly on the
loader's path:

```
my-trips/
  trip-viewer.html       <- your copy of the shell (from setup-workspace.sh)
  SLUG-YEAR.trip.js      <- new trip data file
  trips.js               <- regenerated loader (references all .trip.js files)
  trip-data.json         <- raw JSON (for future edits or re-export)
```

`viewer/` is the **read-only public template** (it ships the sample trips) — never
write trips into it. The export scripts reject `viewer/` as an output dir.

Confirm to the user that opening `my-trips/trip-viewer.html` will now show the new
trip automatically — no rebuild required.

---

## Output Checklist

Before delivering, verify:

- [ ] `validate-trip.sh` passes with no `FAIL:` lines — this covers JSON validity,
      required fields, valid enums, unique `d{day}-s{stop}` ids, and cost
      `totals` = sum of all line items
- [ ] Reviewed any `WARN:` lines (e.g. stops without `coords`) and confirmed they're
      intentional — coords are optional and only affect map pins
- [ ] Day count and stop count match the plan
- [ ] Output written to your `my-trips/` workspace (`SLUG-YEAR.trip.js`, `trips.js`,
      `trip-data.json`) — not into the public `viewer/` template
- [ ] `.trip.js` file loads without JavaScript errors
- [ ] `trips.js` references all existing `.trip.js` files plus the new one

---

## Schema Reference

See `$SKILL_DIR/../shared/references/trip-data-schema.md` for the complete
TypeScript type definitions, field descriptions, and example data.
