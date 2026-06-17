# Trip Itinerary Pipeline

A small, self-contained system for turning a vacation plan into an **interactive,
offline-friendly trip viewer**. It's built as a set of [Claude](https://claude.com)
**skills** plus a prebuilt web viewer, structured like a build pipeline with a
shared schema acting as the interface contract between stages.

```
trip-planner  ──►  trip-exporter  ──►  viewer/trip-viewer.html
 (research+plan)    (serialize)         (render)
        \              |                   ▲
         \   skills/shared/references/trip-data-schema.md  (the contract)
          \__________ /
```

- **`trip-planner`** (skill) — research + planning. Produces a complete plan and
  validates it against the schema before handoff. The "produce a valid object" stage.
- **`trip-exporter`** (skill) — serializes the plan to `trip-data.json`, wraps it
  as a self-registering `SLUG-YEAR.trip.js` (`window.__TRIPS__.push(...)`), and
  regenerates `trips.js`. Ships with shell scripts and the prebuilt
  `bundle-shell.html` asset (used for the optional standalone-HTML output).
- **`shared`** — not a runnable skill; it only hosts `trip-data-schema.md`, the
  TripData contract both skills reference via `$SKILL_DIR/../shared/references/`.
- **`viewer/trip-viewer.html`** — the prebuilt single-file React/Vite app that
  renders the trips. Loads trip data dynamically; never needs rebuilding to add a trip.

## What's in here

```
skills/
  trip-planner/SKILL.md
  trip-exporter/SKILL.md  + scripts/  + assets/bundle-shell.html
  shared/SKILL.md         + references/trip-data-schema.md
viewer/
  trip-viewer.html        prebuilt app shell (loads trips.js)
  trips.js                generated loader
  *.trip.js               trip data (two sample trips included)
CLAUDE.md                 project instructions for the AI pipeline
```

## Quick start (just view the samples)

No build step. Open `viewer/trip-viewer.html` in a browser — it loads the two
sample trips via `trips.js`. Because it uses `document.write`-based script
loading, opening straight from the filesystem works in most browsers; if your
browser blocks local scripts, serve the folder instead:

```bash
cd viewer
python3 -m http.server 8000   # then open http://localhost:8000/trip-viewer.html
```

## Using the skills

These are Claude skills (compatible with Claude Code / Cowork). Install by making
the `skills/` directories available to your Claude environment as skills (e.g.,
place them in your skills directory, or load them as a plugin). Then:

1. **Plan** — ask Claude to plan a trip; the `trip-planner` skill guides research
   and produces a schema-valid plan.
2. **Export** — ask Claude to export it; the `trip-exporter` skill writes the
   `.trip.js` file and regenerates `trips.js` into your `viewer/` folder.
3. **View** — open `viewer/trip-viewer.html`.

You don't strictly need Claude — the data format is plain JSON wrapped in a tiny
JS shim, so you can also author `*.trip.js` files by hand against the schema.

### Adding a trip by hand (no AI)

A `*.trip.js` file is just your trip object pushed onto a global array:

```js
window.__TRIPS__ = window.__TRIPS__ || [];
window.__TRIPS__.push({ /* a TripData object — see the schema */ });
```

Then regenerate the loader (lists every `*.trip.js`, newest first):

```bash
bash skills/trip-exporter/scripts/regenerate-loader.sh viewer my-trip-2027.trip.js
```

To produce a single shareable file with one trip embedded:

```bash
bash skills/trip-exporter/scripts/inject-trip-data.sh my-trip.json itinerary.html
```

## The data contract

Everything flows through `skills/shared/references/trip-data-schema.md`. Key rules:

- **Days are 1-indexed** — `dayNumber` starts at **1** (Day 1 = arrival).
- Stop IDs follow `d{dayNumber}-s{stopIndex}`.
- Day `category` ∈ `travel | history | nature | driving | mixed | departure`.
- Stop `pricing.type` ∈ `confirmed | free | estimated | optional`.
- `costEstimate` has three tiers (`budget`, `mid`, `high`); **`totals` must equal
  the sum of all line items** (regenerate totals programmatically when editing).
- Stops without `coords` (drives, meals) simply don't render as map pins.

## Notes & limitations

- **The viewer's React source is not included.** The prebuilt
  `viewer/trip-viewer.html` and `skills/trip-exporter/assets/bundle-shell.html`
  are committed and fully functional for authoring and viewing trips, but the
  upstream React/Vite source used to build them isn't part of this repo — so you
  can't recompile the viewer from here. (A `viewer-builder` skill that does the
  recompile exists in the original project but was intentionally omitted, since
  it requires that source.)
- The sample trips under `viewer/` are illustrative dummy data — replace them
  with your own.
- The viewer is a single self-contained HTML file (React, Leaflet, print styles
  inlined); it works offline once loaded.

## Credits

Built as a Claude skills pipeline. The skill format (`SKILL.md` + scripts/assets)
follows Claude's skills convention.
