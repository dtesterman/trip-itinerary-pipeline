# Contributing

Thanks for your interest in the Trip Itinerary Pipeline. There are **two
distinct workflows**, and they don't mix:

1. **Authoring your own trips** — a **private, local** activity. Your trips live
   in `my-trips/`, which is **gitignored by design**. They never get committed,
   never go into a PR, and never reach CI. You validate and view them locally.
   This is most people's use of the project. See
   [*Authoring trips (private & local)*](#authoring-trips-private--local).
2. **Contributing to the project itself** — changes to the **tooling, template,
   skills, validator, or docs**. This is what pull requests are for. See
   [*Contributing changes to the repo (pull requests)*](#contributing-changes-to-the-repo-pull-requests).

> **Why your trips can't be PR'd:** `.gitignore` excludes `my-trips/*` (except the
> scaffolding `.gitkeep`/`README.md`). A `*.trip.js` placed there is intentionally
> not tracked by git, so it would be absent from any PR and CI could not see it.
> This is deliberate — `viewer/` is a public, read-only template and private trips
> are never committed back into it. Keep and share your trips locally instead.

## Quick checklist

- Do not edit files in `viewer/` — those are the public, read-only samples.
- Author your trips in `my-trips/` (gitignored) — validate and view them locally;
  do **not** open a PR for them.
- Open a PR only for changes to tooling/template/skills/validator/docs.
- Regenerate the loader only inside `my-trips/` (not `viewer/`).

## Bootstrap (one-time)

If you haven't already, create your private workspace:

```bash
bash scripts/setup-workspace.sh
```

This copies the viewer shell into `my-trips/` so your trips live there and are
kept private.

## Authoring trips (private & local)

This stays entirely on your machine — no commit, no PR. Your trips are yours.

### Manual

1. Create a `*.trip.js` file that contains a single `window.__TRIPS__.push({...})`
   call with your `TripData` object (see `skills/shared/references/trip-data-schema.md`).
2. Place the file in `my-trips/` (run `bash scripts/setup-workspace.sh` first if
   that folder isn't set up yet).
3. Regenerate the loader in `my-trips/`:

```bash
bash skills/trip-exporter/scripts/regenerate-loader.sh my-trips your-trip-file.trip.js
```

4. Validate locally (see below) and view by opening `my-trips/trip-viewer.html`
   in a browser. Done — there's nothing to commit.

### Using the exporter skill

If you use the `trip-exporter` scripts or the skill to write trips, ensure the
export target is `my-trips/` and not `viewer/`. The exporter scripts include a
guard to prevent accidental writes into `viewer/`.

### Validating your trips locally

Run the validator against your workspace — pass a directory (searched
recursively) or a single `.trip.js` file:

```bash
python3 scripts/validate_trips.py my-trips         # your private workspace
python3 scripts/validate_trips.py my-trips/your-file.trip.js   # a single trip
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
- each day has a non-empty `stops` array (the viewer crashes on a stopless day)
- stop `id` format `d{day}-s{stopIndex}`
- `costEstimate` structure (non-empty `categories`, numeric `totals` for all three tiers)
- cost totals arithmetic (sum of item costs must match `costEstimate.totals`)

If the validator reports errors, fix them locally and re-run until the report is clean.

## Contributing changes to the repo (pull requests)

Pull requests are for changes to the **project itself** — the validator, the
export scripts, the skills, the docs, CI, or the `viewer/` template (sample trips
and shell). They are **not** for your personal trips, which stay private and local
(see above). If your "contribution" is only a new `*.trip.js` under `my-trips/`,
there is nothing to PR — keep it locally.

CI runs `scripts/validate_trips.py .` on pushes and PRs to `main`, scanning the
whole repo so every committed `.trip.js` (i.e. the `viewer/` samples) stays valid.
If your change touches those samples or the validator, run the full scan locally
first.

### PR checklist

- [ ] Full validation passes locally (`python3 scripts/validate_trips.py .`).
- [ ] `viewer/` samples weren't changed unintentionally (and if changed on
      purpose, they still validate).
- [ ] No private trips or `my-trips/` contents were committed.
- [ ] PR description includes: what changed, why, and which files were touched.

## Troubleshooting

- Cost totals mismatch: recalc `totals` by summing each category's `items[].cost` numbers.
- Missing `dayNumber` or wrong sequence: ensure day objects are ordered and numbered starting at 1.
- Windows users: prefer running the validator under WSL/Git-Bash if you hit environment issues; the PowerShell wrapper (`scripts/validate_trips.ps1`) locates `python` or `py` on PATH.

## Style and etiquette

- Keep commits focused and small — one logical change per PR is ideal for
  reviewability.
- Use clear commit messages and a descriptive PR title.

## Contact

If you're unsure about schema fields or need help authoring a trip, open an issue
or mention the maintainers listed in the repository metadata. (Remember: trips
themselves stay in your local `my-trips/` — issues are for questions, not for
submitting trip files.)
