---
name: trip-planner
description: >
  Guides the user through researching and planning a vacation trip from scratch.
  Covers destination research, attraction discovery, day-by-day itinerary
  organization, route optimization, cost estimation across budget/mid/high tiers,
  and lodging selection — producing a validated plan ready for export.

  Use this skill whenever the conversation involves planning a new trip, choosing
  a destination, researching what to do somewhere, organizing a vacation itinerary,
  or asking "what should we do in [place]?" Trigger on: "plan a trip to",
  "I want to visit", "help me plan a vacation", "research [destination]",
  "organize a trip", "what should we do in", "how many days in", "plan our
  next vacation", or any conversation where a trip destination is being explored
  but no completed plan exists yet. Also trigger when the user provides a
  destination and dates and wants help filling in the details.
---

# Trip Planner

Guide the user through two phases — RESEARCH and PLAN — to produce a complete,
validated vacation plan. The plan must capture every field the TripData schema
requires so that the trip-exporter skill can convert it directly to JSON without
further research.

## Before You Start

1. **Check auto-memory** for persistent travel preferences: lodging constraints
   (e.g., timeshare eligibility), dietary restrictions, activity preferences
   (e.g., scenic drives vs. museums), family heritage context, and any
   destination-specific notes from prior trips.

2. **Read the schema** at `$SKILL_DIR/../shared/references/trip-data-schema.md`
   to understand what fields the final plan must include. Every stop needs a name,
   time estimate, emoji, description, approximate coordinates, pricing, and status.
   Every day needs a category. Cost estimates need three tiers.

---

## Phase 1 — RESEARCH

Gather the raw material the plan will be built from. Work with the user to
establish constraints, then research within those bounds.

### Establish Constraints

- Destination(s) and travel dates
- Traveler count and who's traveling (couple, family, solo)
- Budget range expectations
- Travel style preferences (relaxed vs. packed, driving vs. walking, etc.)
- Lodging preferences and constraints (timeshare availability, B&B vs. hotel)
- Any must-see stops or activities
- Any must-avoid activities or foods
- **Home location** — always ask. It's used to *estimate* door-to-airport travel time
  for both legs (home → home airport, and arrival airport → home on the return). Be
  explicit about what the estimate can and can't do: it's a **rough distance-based
  estimate, not live or time-of-day traffic routing**. Invite the traveler to **supply a
  known door-to-airport travel time instead** — a supplied time always takes precedence.
- **Home-airport mode** — will they **park at the home airport or use rideshare** to get
  there? Drives the home-side logistics stops and their cost.
- **Destination ground-transport mode** — **rental car, Turo, or rideshare (Uber/Lyft)**?
  A separate decision from the home-airport mode. Drives the destination pickup/return
  stops and the buffers folded into destination arrival and departure times.

### Research Destinations

For each destination area, investigate:

- **Attractions:** museums, historic sites, parks, scenic viewpoints, tours
- **Restaurants:** breakfast, lunch, dinner options matching dietary preferences
- **Scenic routes:** drives, walks, overlooks
- **Lodging options:** verify eligibility (e.g., Club Wyndham timeshare vs.
  Wyndham-branded hotel — these are different things)
- **Operating hours and seasonal availability:** closed days, seasonal closures,
  reservation requirements
- **Event calendars:** festivals, markets, special exhibits during travel dates
- **Timing constraints:** "museum closed Mondays", "reservations open 90 days out"

### Capture Approximate Coordinates

Look up lat/lng for each potential stop during research. These don't need to be
precise — trip-exporter will refine them — but having approximate values during
planning enables route optimization and driving time estimates.

---

## Phase 2 — PLAN

Organize the researched material into a structured day-by-day itinerary.

### Day-by-Day Organization

For each day, define:

- **Day number** (1-indexed: Day 1 = arrival day)
- **Title** (e.g., "Old Town & Museums")
- **Subtitle** (e.g., "Friday, Oct 16")
- **Category** — one of: `travel`, `history`, `nature`, `driving`, `mixed`, `departure`
- **Stops** — ordered list with timing, descriptions, pricing
- **Daily tip** — practical advice for that day
- **Driving time and miles** (if applicable)

### Stop Details

For each stop, capture:

- Name and location
- Approximate time of arrival
- Contextual emoji (airport, hotel, restaurant, museum, park, etc.)
- 1-3 sentence description
- Pricing with type (confirmed, estimated, free, optional)
- Coordinates (approximate lat/lng)
- Google Maps search URL
- Operating hours (if relevant)
- Reservation requirements (if any)
- Lodging info (if this is where they're staying)

### Route Optimization

- Minimize backtracking — order stops geographically within each day
- Account for driving time between stops
- Place longer stops (museums, parks) when energy is highest
- Put restaurants at natural meal times
- Balance activity density — don't pack 10 stops into one day and 2 into the next

### Airport & Travel-Day Routing

A trip doesn't begin at the destination airport — it begins at the traveler's front
door. Model the full chain to and from home as ordinary **stops** (existing fields: name,
`placeholderEmoji`, `time`, `pricing`), back-calculated from the flight times so nothing
is missed. These are normal stops — keep ids 1-indexed and contiguous (`d{day}-s{stop}`).

**Pre-flight buffer.** Arrive at the airport **2 hours before a domestic flight, 3 hours
before an international flight**. Determine domestic vs. international from the
origin/destination airports (international if the trip crosses a national border).

**Door-to-airport time.** Estimate it from the traveler's home location (rough,
distance-based — say so), or use a traveler-supplied time when given. Whichever value you
use, **state it in the plan** (e.g., "assuming ~40 min to DFW") so it stays visible and
the traveler can override it.

Build the chain in four phases (omit stops that don't apply to the chosen modes):

**Phase 1 — Outbound, home side** (leading stops of Day 1, the `travel` day):
- 🏠 **Depart home** — `time` = flight departure − buffer − door-to-airport time.
- 🅿️ **Park at {home airport}** *or* 🚕 **Rideshare to {home airport}** — carry the
  parking/rideshare cost on the stop's `pricing` (home-airport mode).
- ✈️ **Arrive {home airport}** — `time` = flight departure − buffer (2h / 3h).

**Phase 2 — Destination arrival, mode-aware** (after the destination ✈️ arrival stop).
Apply the pickup buffer for the chosen mode, which pushes back the first real stop:
- Rental car → 🚗 **Pick up rental car** — counter/queue buffer, default **~45 min**.
- Turo → 🚙 **Pick up Turo** — at a major airport this is a multi-step **remote-lot
  shuttle** process: locate/wait for the shuttle → ride to the lot → **~10-min
  check-in/inspection** → drive off. Default **~45–60 min** (shuttle + locate time
  dominates; the check-in itself is only ~10 min).
- Rideshare → 🚕 **Rideshare to {first stop / lodging}** — pickup-zone wait, default
  **~15 min**.

**Phase 3 — Destination departure, mode-aware** (trailing stops of the `departure` day).
Work backward from the flight: arrive at the airport by departure − buffer (2h / 3h),
then add the mode's return process and the travel time **from the last itinerary entry**:
- 🚗 **Drive to {airport}** — `time` = last entry + travel-to-airport time. *Skip when
  rideshare-only* — the rideshare itself is the trip to the airport.
- Rental → 🚗 **Return rental car** — add a **30-min** drop-off buffer before the airport
  deadline. · Turo → 🚙 **Return Turo** — reverse of arrival: drive to the remote lot →
  **~10-min check-out** → **shuttle back to the terminal**, default **~45–60 min** total,
  *before* the pre-flight buffer. · Rideshare → 🚕 **Rideshare to {airport}** — pickup wait.
- ✈️ **Arrive {airport}** — `time` = flight departure − buffer (2h / 3h).

**Phase 4 — Return, home side:**
- 🏠 **Arrive home** — `time` = flight arrival + airport-to-home travel time.

All buffer values above are **defaults — state them and let the traveler adjust.**

### Cost Estimation

Build a cost estimate with three tiers (budget, mid, high) covering:

- Flights (if applicable)
- Ground transportation (rental car/Turo, gas, taxi/rideshare, **home-airport parking or
  rideshare**) — reflect the `pricing` from the Phase 1–3 logistics stops here as line
  items so the totals stay complete
- Lodging (per night, noting timeshare savings if applicable)
- Attractions (per person, confirmed vs. estimated pricing)
- Dining (breakfast, lunch, dinner by day count)
- Miscellaneous (parking, tips, souvenirs, incidentals)

Each category should have line items with per-person or per-unit costs.
Totals must sum correctly across all categories.

### Alignment Note

Write an alignment note explaining the optimal arrival day and why. Reference
timing constraints: "Arrive Thursday so Day 1 = Friday and museums are open
weekdays. Japanese Gardens closed Mon-Tue. Railway Museum weekends only."

---

## Validation Checkpoint

Before declaring the plan complete, verify:

- [ ] Every stop has: name, time, emoji, description, pricing, approximate coords
- [ ] Every day has: title, subtitle, category, tip
- [ ] Travel day (Day 1) leads with the home-side outbound stops (depart home →
      park/rideshare → arrive home airport) and the destination pickup stop, with times
      back-calculated from the flight and the pre-flight buffer (2h domestic / 3h intl)
- [ ] Departure day ends with the destination return chain (drive to airport / return
      car or Turo / rideshare → arrive airport → arrive home), times computed from the
      last itinerary entry, the mode's return buffer, and the pre-flight buffer
- [ ] Day categories use valid values (travel, history, nature, driving, mixed, departure)
- [ ] Cost estimates have all three tiers (budget, mid, high)
- [ ] Cost totals sum correctly
- [ ] Stop count and day count feel right for the trip length
- [ ] Route order makes geographic sense (no unnecessary backtracking)
- [ ] User preferences from auto-memory are reflected (scenic drives, dining, etc.)

Present the completed plan to the user for review. Offer to adjust days,
add/remove stops, or tweak costs.

---

## Handoff to Export

When the user approves the plan, offer to hand off to the trip-exporter skill:

> "Your plan is ready. Want me to export it to your trip collection? This will
> generate the trip data file and add it to your trip viewer."

This triggers the trip-exporter skill, which converts the plan to trip-data.json
and produces the `.trip.js` file for dynamic loading into trip-viewer.html.

---

## Schema Reference

The complete TripData schema is at `$SKILL_DIR/../shared/references/trip-data-schema.md`.
Consult it when you need field-level detail on types, required vs. optional fields,
or valid enum values.
