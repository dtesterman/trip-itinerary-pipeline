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


def numeric_sum_category(categories, key: str) -> Tuple[int, int, int]:
    b = m = h = 0
    for cat in categories:
        for item in cat.get('items', []):
            cost = item.get('cost') or {}
            b += int(cost.get('budget') or 0)
            m += int(cost.get('mid') or 0)
            h += int(cost.get('high') or 0)
    return b, m, h


def validate_trip(data: dict, path: str) -> Tuple[bool, list]:
    errs = []
    # Top-level required fields
    for f in ('name', 'dates', 'travelers', 'airports', 'days', 'costEstimate'):
        if f not in data:
            errs.append(f"missing top-level field: {f}")

    # dates
    dates = data.get('dates') or {}
    for d in ('start', 'end'):
        if d not in dates:
            errs.append(f"dates.{d} missing")

    # days
    days = data.get('days') or []
    if not isinstance(days, list) or len(days) == 0:
        errs.append('days must be a non-empty array')
    else:
        for idx, day in enumerate(days, start=1):
            dn = day.get('dayNumber')
            if dn != idx:
                errs.append(f"day #{idx} has dayNumber={dn} (expected {idx})")
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

    # cost totals
    ce = data.get('costEstimate') or {}
    cats = ce.get('categories') or []
    totals = ce.get('totals') or {}
    calc_b, calc_m, calc_h = numeric_sum_category(cats, 'cost')
    tb = int(totals.get('budget') or 0)
    tm = int(totals.get('mid') or 0)
    th = int(totals.get('high') or 0)
    if (calc_b, calc_m, calc_h) != (tb, tm, th):
        errs.append(f"cost totals mismatch: calculated (budget,mid,high)=({calc_b},{calc_m},{calc_h}) vs totals=({tb},{tm},{th})")

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
