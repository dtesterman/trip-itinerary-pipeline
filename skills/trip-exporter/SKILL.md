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
- **Every stop needs `coords`** (lat/lng) for maps and route links. Look up precise
  coordinates for each location. Stops without coords won't appear on the map.
- **`placeholderEmoji`** is required — pick contextually relevant emoji
  (see schema reference for common emoji table)
- **`mapUrl`** should be a Google Maps search URL for the location
- **Cost estimates** need all three tiers: `budget`, `mid`, `high`
- **Day categories** must be one of: `travel`, `history`, `nature`, `driving`,
  `mixed`, `departure`
- **Stop status** should be `planned` for new trips

Validate the JSON:
```bash
node -e "const d = JSON.parse(require('fs').readFileSync('trip-data.json','utf8')); \
  console.log('Valid:', d.name, '-', d.days.length, 'days,', \
  d.days.reduce((s,d)=>s+d.stops.length,0), 'stops')"
```

### Step 2 — Create .trip.js file (default output)

Use the script bundled with this skill to wrap the JSON in a self-registering
format that pushes onto `window.__TRIPS__`:

```bash
SKILL_DIR="<path-to-this-skill>"
bash "$SKILL_DIR/scripts/create-trip-file.sh" trip-data.json SLUG-YEAR OUTPUT_DIR
```

Where `SLUG-YEAR` is a short identifier like `lakes-loop-2027` or `coast-weekender-2027`.
Output: `OUTPUT_DIR/SLUG-YEAR.trip.js`

### Step 3 — Regenerate trips.js loader

Update the loader so trip-viewer.html discovers the new trip automatically:

```bash
bash "$SKILL_DIR/scripts/regenerate-loader.sh" OUTPUT_DIR SLUG-YEAR.trip.js
```

The new trip file is placed first in the loader (most recent trip).
Output: `OUTPUT_DIR/trips.js`

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

### Step 5 — Deliver to workspace

Copy outputs to the user's Vacation Planning folder:

```
Vacation Planning/
  SLUG-YEAR.trip.js      <- new trip data file
  trips.js               <- regenerated loader (references all .trip.js files)
  trip-data.json         <- raw JSON (for future edits or re-export)
```

Confirm to the user that opening trip-viewer.html will now show the new trip
automatically — no rebuild required.

---

## Output Checklist

Before delivering, verify:

- [ ] JSON parses without errors
- [ ] Every stop has a unique `id` in `d{day}-s{stop}` format
- [ ] Every stop has `coords` (lat/lng)
- [ ] Every stop has required fields: time, name, mapUrl, placeholderEmoji,
      description, pricing, status
- [ ] Cost estimate has all three tiers with a `totals` object
- [ ] Cost totals sum correctly (category line items = category total = grand total)
- [ ] Day categories use valid values
- [ ] Day count and stop count match the plan
- [ ] `.trip.js` file loads without JavaScript errors
- [ ] `trips.js` references all existing `.trip.js` files plus the new one

---

## Schema Reference

See `$SKILL_DIR/../shared/references/trip-data-schema.md` for the complete
TypeScript type definitions, field descriptions, and example data.
