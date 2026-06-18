#!/bin/bash
set -e

# Validates a trip-data.json against the TripData schema contract
# (skills/shared/references/trip-data-schema.md).
#
# Checks (ERRORS - exit 1):
#   - required top-level fields and types
#   - each day: required fields + valid category enum
#   - each stop: required fields, id format d{day}-s{stop}, unique ids,
#     valid pricing.type and status enums
#   - costEstimate: required structure + valid line-item priceType
#   - cost totals equal the sum of all line items for every tier
#
# Checks (WARNINGS - do not fail):
#   - stop missing coords (per the schema, coords are strongly recommended,
#     not required; such stops simply do not render as map pins)
#   - stop id day prefix not matching the day it belongs to
#
# Usage:
#   bash scripts/validate-trip.sh <trip-data.json>

TRIP_JSON="${1:?Usage: validate-trip.sh <trip-data.json>}"

if [ ! -f "$TRIP_JSON" ]; then
  echo "Error: Trip data file not found: $TRIP_JSON"
  exit 1
fi

node -e '
const fs = require("fs");
const path = process.argv[1];

let d;
try {
  d = JSON.parse(fs.readFileSync(path, "utf8"));
} catch (e) {
  console.error("FAIL: not valid JSON - " + e.message);
  process.exit(1);
}

const errors = [];
const warnings = [];
const E = (m) => errors.push(m);
const W = (m) => warnings.push(m);

const DAY_CATEGORIES = ["travel","history","nature","driving","mixed","departure"];
const PRICE_TYPES   = ["confirmed","free","estimated","optional"];
const STOP_STATUS   = ["planned","visited","skipped"];
const LINE_PRICE    = ["confirmed","estimated"];

const isStr = (v) => typeof v === "string" && v.length > 0;
const isNum = (v) => typeof v === "number" && !Number.isNaN(v);

// ---- top level ----
if (!isStr(d.name)) E("top-level: name missing or not a string");
if (!d.dates || !isStr(d.dates.start) || !isStr(d.dates.end))
  E("top-level: dates.start / dates.end missing");
if (!isNum(d.travelers)) E("top-level: travelers missing or not a number");
if (!d.airports || !isStr(d.airports.flyIn) || !isStr(d.airports.flyOut))
  E("top-level: airports.flyIn / airports.flyOut missing");
if (!Array.isArray(d.days) || d.days.length === 0)
  E("top-level: days must be a non-empty array");
if (!d.costEstimate) E("top-level: costEstimate missing");

// ---- days + stops ----
const ids = new Set();
(d.days || []).forEach((day, di) => {
  const dn = "day[" + di + "]";
  if (!isNum(day.dayNumber)) E(dn + ": dayNumber missing or not a number");
  if (!isStr(day.title))     E(dn + ": title missing");
  if (!isStr(day.subtitle))  E(dn + ": subtitle missing");
  if (!isStr(day.tip))       E(dn + ": tip missing");
  if (!DAY_CATEGORIES.includes(day.category))
    E(dn + ": invalid category \"" + day.category + "\" (must be " + DAY_CATEGORIES.join("|") + ")");
  if (!Array.isArray(day.stops) || day.stops.length === 0) {
    E(dn + ": stops must be a non-empty array");
    return;
  }
  day.stops.forEach((s, si) => {
    const sn = dn + ".stop[" + si + "] (" + (s.id || "no-id") + ")";
    if (!isStr(s.id) || !/^d\d+-s\d+$/.test(s.id)) {
      E(sn + ": id missing or not in d{day}-s{stop} format");
    } else {
      if (ids.has(s.id)) E(sn + ": duplicate id " + s.id);
      ids.add(s.id);
      const m = s.id.match(/^d(\d+)-s\d+$/);
      if (m && isNum(day.dayNumber) && Number(m[1]) !== day.dayNumber)
        W(sn + ": id day prefix d" + m[1] + " != dayNumber " + day.dayNumber);
    }
    if (!isStr(s.time))             E(sn + ": time missing");
    if (!isStr(s.name))             E(sn + ": name missing");
    if (!isStr(s.mapUrl))           E(sn + ": mapUrl missing");
    if (!isStr(s.placeholderEmoji)) E(sn + ": placeholderEmoji missing");
    if (!isStr(s.description))      E(sn + ": description missing");
    if (!s.pricing || !isStr(s.pricing.amount))
      E(sn + ": pricing.amount missing");
    if (!s.pricing || !PRICE_TYPES.includes(s.pricing.type))
      E(sn + ": invalid pricing.type \"" + (s.pricing && s.pricing.type) + "\" (must be " + PRICE_TYPES.join("|") + ")");
    if (!STOP_STATUS.includes(s.status))
      E(sn + ": invalid status \"" + s.status + "\" (must be " + STOP_STATUS.join("|") + ")");
    if (!s.coords || !isNum(s.coords.lat) || !isNum(s.coords.lng))
      W(sn + ": no coords - will not render as a map pin");
  });
});

// ---- cost estimate ----
const ce = d.costEstimate;
if (ce) {
  if (!Array.isArray(ce.categories) || ce.categories.length === 0)
    E("costEstimate: categories must be a non-empty array");
  if (!ce.totals || !["budget","mid","high"].every(k => isNum(ce.totals[k])))
    E("costEstimate: totals must have numeric budget/mid/high");
  if (!Array.isArray(ce.tips)) E("costEstimate: tips must be an array");

  const sums = { budget: 0, mid: 0, high: 0 };
  (ce.categories || []).forEach((c, ci) => {
    const cn = "costEstimate.category[" + ci + "]";
    if (!isStr(c.emoji)) E(cn + ": emoji missing");
    if (!isStr(c.name))  E(cn + ": name missing");
    if (!Array.isArray(c.items) || c.items.length === 0)
      E(cn + " (" + c.name + "): items must be a non-empty array");
    (c.items || []).forEach((it, ii) => {
      const inm = "costEstimate." + c.name + ".item[" + ii + "]";
      if (!isStr(it.item)) E(inm + ": item missing");
      if (typeof it.detail !== "string") E(inm + ": detail missing");
      if (!LINE_PRICE.includes(it.priceType))
        E(inm + ": invalid priceType \"" + it.priceType + "\" (must be " + LINE_PRICE.join("|") + ")");
      if (!it.cost || !["budget","mid","high"].every(k => isNum(it.cost[k])))
        E(inm + ": cost must have numeric budget/mid/high");
      else ["budget","mid","high"].forEach(k => sums[k] += it.cost[k]);
    });
  });

  if (ce.totals) {
    ["budget","mid","high"].forEach(k => {
      if (isNum(ce.totals[k]) && sums[k] !== ce.totals[k])
        E("costEstimate: " + k + " total " + ce.totals[k] + " != sum of line items " + sums[k]);
    });
  }
}

// ---- report ----
warnings.forEach(w => console.log("WARN: " + w));
if (errors.length) {
  errors.forEach(e => console.error("FAIL: " + e));
  console.error("\nINVALID - " + errors.length + " error(s), " + warnings.length + " warning(s).");
  process.exit(1);
}
const stops = (d.days || []).reduce((s, x) => s + (x.stops ? x.stops.length : 0), 0);
console.log("\nVALID: " + d.name + " - " + d.days.length + " days, " + stops + " stops, totals " + JSON.stringify(d.costEstimate.totals) + " (" + warnings.length + " warning(s)).");
' "$TRIP_JSON"
