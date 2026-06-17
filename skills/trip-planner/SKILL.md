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

### Cost Estimation

Build a cost estimate with three tiers (budget, mid, high) covering:

- Flights (if applicable)
- Ground transportation (rental car, gas, taxi/rideshare)
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
