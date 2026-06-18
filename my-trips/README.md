# Your private trip workspace

This folder is where **your own trips** live. It is **gitignored** — everything
here except this `README.md` and `.gitkeep` is ignored and will never be committed
back into the template repo.

## Setup (once)

From the repo root:

```bash
bash scripts/setup-workspace.sh
```

This copies the prebuilt viewer shell (`viewer/trip-viewer.html`) into this folder.
The viewer loads `trips.js` and each `*.trip.js` by same-folder relative path, so
your trips must live next to their own copy of the viewer shell — which is exactly
what this workspace provides.

## Authoring trips

Export trips here (use `my-trips` as the output dir), or author `*.trip.js` files by
hand. A typical workspace ends up with:

```
my-trips/
  trip-viewer.html       <- your copy of the shell (from setup)
  SLUG-YEAR.trip.js      <- your trip data file(s)
  trips.js               <- regenerated loader
  trip-data.json         <- raw JSON source (for future edits / re-export)
```

Then open `my-trips/trip-viewer.html` to view your trips.

> Never write trips into the public `viewer/` folder — that's the read-only
> template and its sample trips. The export scripts will reject `viewer/` as an
> output dir.
