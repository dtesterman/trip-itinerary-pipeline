# Contributing

Thanks for your interest in contributing to the Trip Itinerary Pipeline. This
document explains the expected workflow for adding trips, running local
validation, and opening clean pull requests so CI can verify your changes.

## Quick checklist

- Do not edit files in `viewer/` — those are the public, read-only samples.
- Add trip files into your `my-trips/` workspace (the repo is gitignored there).
- Run the validator and confirm it passes before opening a PR.
- Regenerate the loader only inside `my-trips/` (not `viewer/`).

## Bootstrap (one-time)

If you haven't already, create your private workspace:

```bash
bash scripts/setup-workspace.sh
```

This copies the viewer shell into `my-trips/` so your trips live there and are
kept private.

## Adding a trip (manual)

1. Create a `*.trip.js` file that contains a single `window.__TRIPS__.push({...})`
   call with your `TripData` object (see `skills/shared/references/trip-data-schema.md`).
2. Place the file in `my-trips/`.
3. Regenerate the loader in `my-trips/`:

```bash
bash skills/trip-exporter/scripts/regenerate-loader.sh my-trips your-trip-file.trip.js
```

4. Validate locally (see Validation section below) and open a PR against `main`.

## Adding a trip using the exporter skill

If you use the `trip-exporter` scripts or the skill to write trips, ensure the
export target is `my-trips/` and not `viewer/`. The exporter scripts include a
guard to prevent accidental writes into `viewer/`.

## Validation (required before PR)

CI automatically runs `scripts/validate_trips.py` on pushes and PRs to `main`,
scanning the whole repo so every committed `.trip.js` is validated. Private trips
in `my-trips/` are gitignored and never reach CI, so validate them locally before
sharing. Run the validator before opening a PR — pass a directory (searched
recursively) or a single `.trip.js` file:

```bash
python3 scripts/validate_trips.py .          # everything (matches CI)
python3 scripts/validate_trips.py my-trips   # just your private workspace
```

If you are editing raw JSON trip data instead of `.trip.js` wrapper files, you can
also use the existing validator in `skills/trip-exporter/scripts/validate-trip.sh`:

```bash
bash skills/trip-exporter/scripts/validate-trip.sh path/to/trip-data.json
```

On Windows (PowerShell):

```powershell
.\scripts\validate_trips.ps1
```

The validator checks a subset of important rules including:

- top-level required fields (`name`, `dates`, `travelers`, `airports`, `days`, `costEstimate`)
- `dayNumber` sequencing (days must be 1-indexed and contiguous)
- stop `id` format `d{day}-s{stopIndex}`
- cost totals arithmetic (sum of item costs must match `costEstimate.totals`)

If the validator reports errors, fix them locally and re-run until the report is clean.

## PR checklist

- [ ] Validator passes locally (`scripts/validate_trips.py .`).
- [ ] `viewer/` samples were not edited.
- [ ] Loader regenerated only under `my-trips/` if you added trip files.
- [ ] PR description includes: what changed, why, and which files were added.

## Troubleshooting

- Cost totals mismatch: recalc `totals` by summing each category's `items[].cost` numbers.
- Missing `dayNumber` or wrong sequence: ensure day objects are ordered and numbered starting at 1.
- Windows users: prefer running the validator under WSL/Git-Bash if you hit environment issues; the PowerShell wrapper (`scripts/validate_trips.ps1`) locates `python` or `py` on PATH.

## Style and etiquette

- Keep commits focused and small. One trip per PR is ideal for reviewability.
- Use clear commit messages and a descriptive PR title.

## Contact

If you're unsure about schema fields or need help adding a trip, open an issue
or mention the maintainers listed in the repository metadata.
