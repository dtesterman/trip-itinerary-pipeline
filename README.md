# Trip Itinerary Pipeline

A small, self-contained system for turning a vacation plan into an **interactive,
offline-friendly trip viewer**. It's built as a set of [Claude](https://claude.com)
**skills** plus a prebuilt web viewer, structured like a build pipeline with a
shared schema acting as the interface contract between stages.

```
trip-planner  ──►  trip-exporter  ──►  my-trips/trip-viewer.html
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

> **Public vs. private:** `viewer/` is the immutable public template and ships two
> sample trips — treat it as read-only reference. **Your trips live in `my-trips/`**,
> a gitignored workspace you populate with `scripts/setup-workspace.sh`. Never commit
> your trips back into this template repo.

## What's in here

```
skills/
  trip-planner/SKILL.md
  trip-exporter/SKILL.md  + scripts/  + assets/bundle-shell.html
  shared/SKILL.md         + references/trip-data-schema.md
viewer/                   PUBLIC TEMPLATE (committed, read-only)
  trip-viewer.html        prebuilt app shell (loads trips.js)
  trips.js                loader for the samples
  *.trip.js               two sample trips
my-trips/                 YOUR private workspace (gitignored)
  (run scripts/setup-workspace.sh to populate it with the viewer shell)
scripts/
  setup-workspace.sh      bootstraps my-trips/ from the template
CLAUDE.md / AGENTS.md     project instructions for AI agents
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

**Ready to make your own?** Run `bash scripts/setup-workspace.sh`, then see
[*Using the skills*](#using-the-skills). Your trips go in `my-trips/`, not `viewer/`.

The export scripts require an explicit output directory and will reject
`viewer/` or any path under it, so use `my-trips/` as the export target.

## Using the skills

These are Claude skills (compatible with Claude Code / Cowork). Install by making
the `skills/` directories available to your Claude environment as skills (e.g.,
place them in your skills directory, or load them as a plugin). Then:

0. **Set up your workspace (once)** — run `bash scripts/setup-workspace.sh`. This
   copies the viewer shell into your gitignored `my-trips/` folder, where your trips
   will live.
1. **Plan** — ask Claude to plan a trip; the `trip-planner` skill guides research
   and produces a schema-valid plan.
2. **Export** — ask Claude to export it; the `trip-exporter` skill writes the
   `.trip.js` file and regenerates `trips.js` into your private `my-trips/` workspace
   (it runs setup automatically if you skipped step 0).
3. **View** — open `my-trips/trip-viewer.html` (or `viewer/trip-viewer.html` to see
   the samples).

You don't strictly need Claude — the data format is plain JSON wrapped in a tiny
JS shim, so you can also author `*.trip.js` files by hand against the schema.

### Adding a trip by hand (no AI)

A `*.trip.js` file is just your trip object pushed onto a global array:

```js
window.__TRIPS__ = window.__TRIPS__ || [];
window.__TRIPS__.push({ /* a TripData object — see the schema */ });
```

Place that file in your `my-trips/` workspace (run `bash scripts/setup-workspace.sh`
first if you haven't), then regenerate the loader (lists every `*.trip.js`, newest
first):

```bash
bash skills/trip-exporter/scripts/regenerate-loader.sh my-trips my-trip-2027.trip.js
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
- The sample trips under `viewer/` are a read-only schema demo — don't edit them in
  place. Create your own in the gitignored `my-trips/` workspace via the pipeline (or
  by hand).
- The viewer is a single self-contained HTML file (React, Leaflet, print styles
  inlined); it works offline once loaded.

## CI and local validation

- **GitHub Actions:** A workflow at `.github/workflows/validate-trips.yml` runs
  `scripts/validate_trips.py` on push and pull requests to `main`. It scans the
  whole repo, so **every committed `.trip.js`** is validated — the public samples
  in `viewer/` plus any trip committed elsewhere. (Private trips in `my-trips/`
  are gitignored and never reach CI, so they aren't checked there; validate them
  locally before sharing.)
- **Raw JSON validation:** For plain `trip-data.json` artifacts, the repo also
  includes `skills/trip-exporter/scripts/validate-trip.sh`, which validates the
  raw JSON contract.
- **Run locally (Python):** pass any directory (searched recursively) or a single
  `.trip.js` file. To check your own trips, point it at `my-trips/`:

```bash
python3 scripts/validate_trips.py .          # everything (what CI runs)
python3 scripts/validate_trips.py my-trips   # just your private workspace
```

- **Run locally (PowerShell on Windows):**

```powershell
.\scripts\validate_trips.ps1
```


## Credits

Built as a Claude skills pipeline. The skill format (`SKILL.md` + scripts/assets)
follows Claude's skills convention.
