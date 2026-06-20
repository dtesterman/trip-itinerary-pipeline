# Trip Itinerary Pipeline — Project Instructions

This project turns vacation plans into an interactive, self-contained trip
viewer. Work follows a two-stage authoring pipeline backed by a shared schema,
plus a prebuilt viewer that renders the result.

> **Public vs. private:** `viewer/` is the immutable public template (read-only
> reference; it ships the sample trips). **Your trips live in `my-trips/`**, a
> gitignored workspace populated by `scripts/setup-workspace.sh`. Never write trips
> into `viewer/`, and never commit private trips back into this template repo.

## The Pipeline

```
trip-planner          trip-exporter              my-trips/trip-viewer.html
 (research + plan)  →  (serialize + register)  →  (render; public template
                                                   lives in viewer/)
                   trip-data.json
                   SLUG-YEAR.trip.js   ──→  trips.js loads each .trip.js
                   trips.js (regenerated)   window.__TRIPS__ populated
                                            prebuilt React app reads & renders
```

### Stage 1 — Plan the trip (`trip-planner` skill)

Research destinations, organize a day-by-day itinerary, estimate costs across
budget/mid/high tiers, and validate the plan against the TripData schema before
handoff.

**Trigger when:** the user wants to plan or research a trip, asks "what should we
do in [place]", or hasn't yet produced a completed plan.

### Stage 2 — Export the trip (`trip-exporter` skill)

Convert a completed plan into `trip-data.json`, wrap it as a self-registering
`SLUG-YEAR.trip.js` (`window.__TRIPS__.push(...)`), and regenerate `trips.js`
so the viewer picks up the new trip automatically. Optionally embed a single
trip into a standalone HTML file for sharing.

**Trigger when:** a plan is ready and the user says "export", "add to my trips",
or when `trip-planner` finishes and offers to hand off.

**Default output:** `.trip.js` + regenerated `trips.js` (dynamic loading).
Standalone HTML is only produced on explicit request.

## The Viewer

`viewer/trip-viewer.html` is a **prebuilt, single-file** React/Vite app
(with Leaflet maps and a print stylesheet). It loads trips dynamically via
`<script src="trips.js">`, which in turn loads each `*.trip.js`. Adding a trip
**never** requires rebuilding the viewer.

> Note: the React source used to build the viewer is **not included** in this
> repo. You can author and view trips with the prebuilt `trip-viewer.html`
> as-is; rebuilding the viewer itself would require that source.

## Authoring trips (where output goes)

Before writing any trip output, ensure the private workspace exists: if
`my-trips/trip-viewer.html` is absent, run `bash scripts/setup-workspace.sh`. Author
all trip files (`SLUG-YEAR.trip.js`, `trips.js`, `trip-data.json`) into `my-trips/`
— never into the public `viewer/` template. The export scripts reject `viewer/` as
an output dir.

## Validating trips (do this after every export or edit)

You cannot open a browser, so **validation is your definition of done** — a clean
validator run is the strongest proof a trip is well-formed and will render. After
writing or editing any `.trip.js`, run the validator and only report success if it
exits `0`:

```bash
python3 scripts/validate_trips.py my-trips      # check the trips you just wrote
python3 scripts/validate_trips.py .             # check everything (what CI runs)
```

A path may be a directory (searched recursively) or a single `.trip.js` file.
The validator checks: required top-level fields; 1-indexed, contiguous
`dayNumber`s; stop IDs in `d{day}-s{stopIndex}` form; and that
`costEstimate.totals` equals the sum of all line items. Exit codes: `0` = all
valid, `1` = no trip files found at the given path, `2` = validation errors (the
errors are printed — fix them and re-run until clean).

After exporting, also confirm `trips.js` registers the new file (a
`document.write('<script src="SLUG-YEAR.trip.js">')` line) so the viewer will load
it. Regenerate the loader with `skills/trip-exporter/scripts/regenerate-loader.sh`
rather than hand-editing it.

> **The samples vs. CI:** CI (`.github/workflows/validate-trips.yml`) validates
> every committed `.trip.js` across the repo. Trips you author in `my-trips/` are
> gitignored and never reach CI, so validating them locally is the only check they
> get — don't skip it.

## Shared Schema (the interface contract)

`skills/shared/references/trip-data-schema.md` defines the TripData types,
required fields, valid enum values, and example JSON. It is the contract both
skills depend on: `trip-planner` validates plans against it, `trip-exporter`
generates JSON to it. Keep both skills in sync when the schema changes.

Conventions: **days are 1-indexed** (`dayNumber` starts at 1; Day 1 = arrival).
Stop IDs follow `d{dayNumber}-s{stopIndex}`. Day categories must be one of:
`travel`, `history`, `nature`, `driving`, `mixed`, `departure`. Cost estimates
carry three tiers, and `totals` must equal the sum of all line items.

## File Layout

```
trip-itinerary-pipeline/
├── README.md
├── AGENTS.md                       ← this file
├── CLAUDE.md                       ← same instructions for Claude Code
├── CONTRIBUTING.md                 ← human contributor workflow
├── .github/workflows/
│   └── validate-trips.yml          ← CI: validates every committed *.trip.js
├── scripts/
│   ├── setup-workspace.sh          ← bootstraps my-trips/ from the template
│   ├── validate_trips.py           ← trip validator (run after every export/edit)
│   └── validate_trips.ps1          ← Windows wrapper for validate_trips.py
├── skills/
│   ├── trip-planner/SKILL.md
│   ├── trip-exporter/
│   │   ├── SKILL.md
│   │   ├── scripts/                ← create-trip-file, regenerate-loader, inject-trip-data, validate-trip
│   │   └── assets/bundle-shell.html
│   └── shared/
│       ├── SKILL.md
│       └── references/trip-data-schema.md
├── viewer/                         ← PUBLIC TEMPLATE (read-only reference + samples)
│   ├── trip-viewer.html            ← prebuilt app shell, loads trips.js
│   ├── trips.js                    ← loader for the sample trips
│   └── *.trip.js                   ← two sample trips (committed)
└── my-trips/                       ← YOUR private workspace (gitignored)
    └── (populated by scripts/setup-workspace.sh; your trips land here)
```

## Quick Reference

| I want to...                     | Use                                          |
|----------------------------------|----------------------------------------------|
| Set up my private workspace      | `bash scripts/setup-workspace.sh` (once)     |
| Plan a new trip                  | `trip-planner`                               |
| Export a finished plan           | `trip-exporter` (writes into `my-trips/`)    |
| Make a standalone HTML to share  | `trip-exporter` (ask for standalone)         |
| Change data in an existing trip  | Edit the `my-trips/*.trip.js` file directly  |
| Verify a trip is valid (done?)   | `python3 scripts/validate_trips.py my-trips` (exit 0 = OK) |
| Check everything (as CI does)    | `python3 scripts/validate_trips.py .`        |
| Let a human view my trips        | Tell them to open `my-trips/trip-viewer.html` in a browser |
| Let a human view the samples     | Tell them to open `viewer/trip-viewer.html` in a browser |

The `viewer/` folder ships with two **sample trips** as a read-only schema demo.
Don't replace them in place — author your own in the gitignored `my-trips/`
workspace via the pipeline above.
