#!/usr/bin/env python3
"""Validate .trip.js files against basic TripData rules.

This is a lightweight, stdlib-only validator intended for local checks and CI.
It extracts the JS object passed to `window.__TRIPS__.push(...)`, parses it
as JSON, and performs a few sanity checks:
 - required top-level fields present
 - days are 1-indexed and consistent
 - stop IDs match d{day}-s{idx}
 - cost totals equal the sum of category items for budget/mid/high

Usage: python3 scripts/validate_trips.py [path...]
Each path may be a directory (searched recursively for *.trip.js) or a single
*.trip.js file. If no path is provided, validates files under `viewer/`.
"""
import json
import os
import re
import sys
from glob import glob
from typing import Tuple

# Valid Day.category values, per the TripData schema.
DAY_CATEGORIES = ('travel', 'history', 'nature', 'driving', 'mixed', 'departure')


def extract_json_object_from_js(text: str) -> str:
    # Find the first occurrence of window.__TRIPS__.push( and capture the
    # balanced {...} that follows. We implement a simple brace matcher.
    m = re.search(r"window\.__TRIPS__\.push\s*\(", text)
    if not m:
        raise ValueError("no window.__TRIPS__.push(...) call found")
    start = m.end()
    # find the first '{' after start
    brace_pos = text.find('{', start)
    if brace_pos == -1:
        raise ValueError('no object literal found after push(')
    i = brace_pos
    depth = 0
    in_str = False
    esc = False
    while i < len(text):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == in_str:
                in_str = False
        else:
            if ch == '"' or ch == "'":
                in_str = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    # include this closing brace
                    return text[brace_pos:i+1]
        i += 1
    raise ValueError('could not find matching closing brace for object')


def parse_trip_js(path: str) -> dict:
    txt = open(path, 'r', encoding='utf-8').read()
    obj_text = extract_json_object_from_js(txt)
    # Some JS files may use single quotes; normalize by ensuring it's valid JSON.
    # The sample files use double-quoted JSON, so a direct parse should work.
    return json.loads(obj_text)


def _fmt_num(n):
    """Render a tier as an int when it's whole (300 not 300.0), else as-is."""
    return int(n) if isinstance(n, float) and n.is_integer() else n


def _coerce_tier(value):
    """Return value as a number, or None if it isn't a real numeric tier.

    Bools are rejected (JSON true/false are ints in Python but never valid
    dollar amounts) and so are strings — the schema requires numbers.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value


def numeric_sum_category(categories) -> Tuple[Tuple[float, float, float], list]:
    """Sum every line item's three cost tiers, collecting structural errors.

    Returns ((budget, mid, high), errors). Each item's `cost` must carry three
    numeric tiers; a missing/non-numeric tier is reported and treated as 0 so
    the arithmetic can still be reported alongside the structural error.
    """
    b = m = h = 0.0
    errs = []
    for ci, cat in enumerate(categories):
        if not isinstance(cat, dict):
            errs.append(f"costEstimate.categories[{ci}] is not an object")
            continue
        items = cat.get('items')
        if not isinstance(items, list) or len(items) == 0:
            errs.append(f"costEstimate.categories[{ci}] has missing or empty 'items'")
            continue
        for ii, item in enumerate(items):
            cost = item.get('cost') if isinstance(item, dict) else None
            if not isinstance(cost, dict):
                errs.append(f"categories[{ci}].items[{ii}] missing 'cost' object")
                continue
            for tier, acc_name in (('budget', 'b'), ('mid', 'm'), ('high', 'h')):
                num = _coerce_tier(cost.get(tier))
                if num is None:
                    errs.append(f"categories[{ci}].items[{ii}].cost.{tier} is missing or not a number")
                    num = 0
                if acc_name == 'b':
                    b += num
                elif acc_name == 'm':
                    m += num
                else:
                    h += num
    return (b, m, h), errs


def validate_trip(data: dict, path: str) -> Tuple[bool, list]:
    errs = []
    # Top-level required fields
    for f in ('name', 'dates', 'travelers', 'airports', 'days', 'costEstimate'):
        if f not in data:
            errs.append(f"missing top-level field: {f}")

    # dates — must be an object carrying both required date strings.
    dates = data.get('dates')
    if not isinstance(dates, dict):
        if 'dates' in data:  # presence already reported above if absent
            errs.append("dates must be an object with 'start' and 'end'")
    else:
        for d in ('start', 'end'):
            if d not in dates:
                errs.append(f"dates.{d} missing")

    # airports — must be an object carrying both required IATA codes. (Required
    # by the schema but previously only checked for top-level presence, so an
    # `airports: {}` slipped through with no flyIn/flyOut.)
    airports = data.get('airports')
    if not isinstance(airports, dict):
        if 'airports' in data:
            errs.append("airports must be an object with 'flyIn' and 'flyOut'")
    else:
        for a in ('flyIn', 'flyOut'):
            if a not in airports:
                errs.append(f"airports.{a} missing")

    # days
    days = data.get('days') or []
    if not isinstance(days, list) or len(days) == 0:
        errs.append('days must be a non-empty array')
    else:
        for idx, day in enumerate(days, start=1):
            dn = day.get('dayNumber')
            if dn != idx:
                errs.append(f"day #{idx} has dayNumber={dn} (expected {idx})")
            # Required Day fields beyond dayNumber/stops (previously unchecked).
            for df in ('title', 'subtitle', 'category', 'tip'):
                if df not in day:
                    errs.append(f"day #{idx} missing field: {df}")
            # category, when present, must be one of the schema's enum values.
            cat = day.get('category')
            if cat is not None and cat not in DAY_CATEGORIES:
                errs.append(
                    f"day #{idx} has invalid category {cat!r} "
                    f"(must be one of: {', '.join(DAY_CATEGORIES)})"
                )
            # `stops` is required and must be a non-empty array. The viewer
            # dereferences day.stops.length and maps over day.stops while
            # rendering, so a missing/empty stops list passes silently here but
            # crashes (missing) or renders a blank day (empty) in the viewer.
            stops = day.get('stops')
            if not isinstance(stops, list) or len(stops) == 0:
                errs.append(f"day #{idx} has missing or empty 'stops' (must be a non-empty array)")
                stops = []
            for sidx, stop in enumerate(stops, start=1):
                sid = stop.get('id')
                expected = f"d{idx}-s{sidx}"
                if sid != expected:
                    errs.append(f"stop id mismatch in {path}: expected {expected}, got {sid}")
                # required stop fields
                for sf in ('time', 'name', 'mapUrl', 'placeholderEmoji', 'description', 'pricing', 'status'):
                    if sf not in stop:
                        errs.append(f"stop {sid} missing field: {sf}")

    # cost estimate — require the structure before comparing totals, so a
    # `costEstimate: {}` (or one missing categories/totals) can't pass as 0 == 0.
    ce = data.get('costEstimate')
    if not isinstance(ce, dict):
        errs.append("costEstimate missing or not an object")
    else:
        cats = ce.get('categories')
        totals = ce.get('totals')

        cats_ok = isinstance(cats, list) and len(cats) > 0
        if not cats_ok:
            errs.append("costEstimate.categories missing or empty (must be a non-empty array)")

        # Declared totals: all three tiers must be present and numeric.
        declared = None
        if not isinstance(totals, dict):
            errs.append("costEstimate.totals missing or not an object")
        else:
            tier_vals = {}
            for tier in ('budget', 'mid', 'high'):
                num = _coerce_tier(totals.get(tier))
                if num is None:
                    errs.append(f"costEstimate.totals.{tier} is missing or not a number")
                else:
                    tier_vals[tier] = num
            if len(tier_vals) == 3:
                declared = (tier_vals['budget'], tier_vals['mid'], tier_vals['high'])

        # Only compare arithmetic once both sides are structurally sound; a
        # mismatch report is meaningless if the inputs were never valid.
        if cats_ok and declared is not None:
            (calc_b, calc_m, calc_h), sum_errs = numeric_sum_category(cats)
            errs.extend(sum_errs)
            if not sum_errs and (calc_b, calc_m, calc_h) != declared:
                calc = tuple(_fmt_num(x) for x in (calc_b, calc_m, calc_h))
                decl = tuple(_fmt_num(x) for x in declared)
                errs.append(
                    f"cost totals mismatch: calculated (budget,mid,high)="
                    f"({calc[0]},{calc[1]},{calc[2]}) vs totals=({decl[0]},{decl[1]},{decl[2]})"
                )

    return (len(errs) == 0), errs


def discover_trip_files(path: str) -> list:
    """Return *.trip.js files for a path.

    A path may be a single *.trip.js file (returned as-is) or a directory,
    which is searched recursively. Unknown paths return an empty list.
    """
    if os.path.isfile(path):
        return [path] if path.endswith('.trip.js') else []
    if os.path.isdir(path):
        return sorted(glob(os.path.join(path, '**', '*.trip.js'), recursive=True))
    return []


def main(argv=None):
    argv = argv or sys.argv[1:]
    paths = argv or ['viewer']
    files = []
    for p in paths:
        if not os.path.exists(p):
            print(f"Warning: path not found: {p}")
            continue
        found = discover_trip_files(p)
        if not found:
            print(f"Warning: no *.trip.js files under: {p}")
        files.extend(found)

    # Deduplicate while preserving order (overlapping paths are possible).
    seen = set()
    files = [f for f in files if not (f in seen or seen.add(f))]

    if not files:
        print('No *.trip.js files found in target paths')
        return 1

    overall_ok = True
    for p in files:
        print(f'Validating {p}...')
        try:
            trip = parse_trip_js(p)
        except Exception as e:
            print(f'  ERROR parsing {p}: {e}')
            overall_ok = False
            continue
        ok, errs = validate_trip(trip, p)
        if ok:
            print('  OK')
        else:
            overall_ok = False
            for e in errs:
                print('  -', e)

    return 0 if overall_ok else 2


if __name__ == '__main__':
    rc = main()
    sys.exit(rc)
