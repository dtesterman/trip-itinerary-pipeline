# Trip Itinerary Pipeline — Project Instructions

This project turns vacation plans into an interactive, self-contained trip
viewer. Work follows a two-stage authoring pipeline backed by a shared schema,
plus a prebuilt viewer that renders the result.

## The Pipeline

```
trip-planner          trip-exporter              viewer/trip-viewer.html
 (research + plan)  →  (serialize + register)  →  (render)
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
├── CLAUDE.md                       ← this file
├── skills/
│   ├── trip-planner/SKILL.md
│   ├── trip-exporter/
│   │   ├── SKILL.md
│   │   ├── scripts/                ← create-trip-file, regenerate-loader, inject-trip-data
│   │   └── assets/bundle-shell.html
│   └── shared/
│       ├── SKILL.md
│       └── references/trip-data-schema.md
└── viewer/
    ├── trip-viewer.html            ← prebuilt app shell, loads trips.js
    ├── trips.js                    ← generated loader (lists all .trip.js)
    └── *.trip.js                   ← trip data files (sample trips included)
```

## Quick Reference

| I want to...                     | Use                                   |
|----------------------------------|---------------------------------------|
| Plan a new trip                  | `trip-planner`                        |
| Export a finished plan           | `trip-exporter`                       |
| Make a standalone HTML to share  | `trip-exporter` (ask for standalone)  |
| Change data in an existing trip  | Edit the `.trip.js` file directly     |
| View the trips                   | Open `viewer/trip-viewer.html`        |

The `viewer/` folder ships with two **sample trips** to demonstrate the schema
and the viewer. Replace them with your own via the pipeline above.
