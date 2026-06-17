window.__TRIPS__ = window.__TRIPS__ || [];
window.__TRIPS__.push({
  "name": "Sample Trip · Northern Lakes Loop",
  "dates": {
    "start": "2027-09-09",
    "end": "2027-09-12"
  },
  "travelers": 2,
  "airports": {
    "flyIn": "MSP",
    "flyOut": "MSP"
  },
  "alignmentNote": "Sample data for demonstrating the viewer. Arrive Thursday so the scenic byway and the state-park day fall on quieter weekdays. Replace this trip with your own using the trip-planner / trip-exporter skills.",
  "days": [
    {
      "dayNumber": 1,
      "title": "Arrival & Lakeshore First Look",
      "subtitle": "Thursday, Sep 9",
      "category": "travel",
      "drivingTime": "2h 15m",
      "drivingMiles": "120 mi",
      "stops": [
        {
          "id": "d1-s1",
          "time": "11:00 AM",
          "name": "Arrive at the airport (MSP)",
          "mapUrl": "https://maps.google.com/maps/search/Minneapolis+Saint+Paul+Airport",
          "placeholderEmoji": "✈️",
          "description": "Land and collect bags. Rental counters are in the main terminal ramp.",
          "pricing": {
            "amount": "$0",
            "type": "free"
          },
          "coords": {
            "lat": 44.8848,
            "lng": -93.2223
          },
          "status": "planned"
        },
        {
          "id": "d1-s2",
          "time": "11:45 AM",
          "name": "Pick up rental car",
          "mapUrl": "https://maps.google.com/maps/search/MSP+Rental+Car+Center",
          "placeholderEmoji": "🚗",
          "description": "Midsize sedan. Follow signs to the rental ramp from baggage claim.",
          "pricing": {
            "amount": "$55/day",
            "type": "estimated"
          },
          "coords": {
            "lat": 44.881,
            "lng": -93.21
          },
          "status": "planned"
        },
        {
          "id": "d1-s3",
          "time": "12:30 PM",
          "name": "Drive north along the lake road",
          "mapUrl": "https://maps.google.com/maps/dir/MSP/Lakeside+Town",
          "placeholderEmoji": "🚗",
          "description": "Easy two-hour drive with water views for the last stretch.",
          "pricing": {
            "amount": "$0",
            "type": "free"
          },
          "status": "planned"
        },
        {
          "id": "d1-s4",
          "time": "3:00 PM",
          "name": "Check in at the Lakeside Lodge",
          "mapUrl": "https://maps.google.com/maps/search/Lakeside+Lodge",
          "placeholderEmoji": "🏨",
          "description": "Base for the trip. Lake-view rooms; breakfast included.",
          "pricing": {
            "amount": "$160/night",
            "type": "estimated"
          },
          "lodging": {
            "type": "primary",
            "name": "Lakeside Lodge"
          },
          "coords": {
            "lat": 46.7867,
            "lng": -92.1005
          },
          "status": "planned"
        },
        {
          "id": "d1-s5",
          "time": "6:30 PM",
          "name": "Dinner on the waterfront",
          "mapUrl": "https://maps.google.com/maps/search/waterfront+restaurant",
          "placeholderEmoji": "🍽️",
          "description": "Casual lakefront spot with a varied menu.",
          "pricing": {
            "amount": "$30–$45/pp",
            "type": "estimated"
          },
          "coords": {
            "lat": 46.787,
            "lng": -92.099
          },
          "status": "planned"
        }
      ],
      "tip": "💡 Pick up the car early — the lake road is more scenic in afternoon light."
    },
    {
      "dayNumber": 2,
      "title": "State Park & Scenic Byway",
      "subtitle": "Friday, Sep 10",
      "category": "nature",
      "drivingTime": "1h 30m",
      "drivingMiles": "75 mi",
      "stops": [
        {
          "id": "d2-s1",
          "time": "9:00 AM",
          "name": "Breakfast at the lodge",
          "mapUrl": "https://maps.google.com/maps/search/Lakeside+Lodge",
          "placeholderEmoji": "🍽️",
          "description": "Included with the stay.",
          "pricing": {
            "amount": "$0 (included)",
            "type": "free"
          },
          "status": "planned"
        },
        {
          "id": "d2-s2",
          "time": "10:00 AM",
          "name": "State Park visitor center & overlook",
          "mapUrl": "https://maps.google.com/maps/search/state+park+overlook",
          "placeholderEmoji": "🌳",
          "description": "Short paved trail to a bluff overlook. Per-vehicle entry.",
          "hours": "8 AM – 8 PM",
          "pricing": {
            "amount": "$7/vehicle",
            "type": "confirmed"
          },
          "coords": {
            "lat": 47.24,
            "lng": -91.47
          },
          "status": "planned"
        },
        {
          "id": "d2-s3",
          "time": "12:30 PM",
          "name": "Lunch in a harbor town",
          "mapUrl": "https://maps.google.com/maps/search/harbor+town+lunch",
          "placeholderEmoji": "🍽️",
          "description": "Several cafés around the marina.",
          "pricing": {
            "amount": "$18–$28/pp",
            "type": "estimated"
          },
          "status": "planned"
        },
        {
          "id": "d2-s4",
          "time": "2:00 PM",
          "name": "Scenic byway drive",
          "mapUrl": "https://maps.google.com/maps/search/scenic+byway",
          "placeholderEmoji": "🗺️",
          "description": "Quiet ridgeline route with frequent pull-offs.",
          "pricing": {
            "amount": "$0",
            "type": "free"
          },
          "status": "planned"
        },
        {
          "id": "d2-s5",
          "time": "6:30 PM",
          "name": "Dinner near the lodge",
          "mapUrl": "https://maps.google.com/maps/search/dinner+near+Lakeside+Lodge",
          "placeholderEmoji": "🍽️",
          "description": "Relaxed evening close to base.",
          "pricing": {
            "amount": "$30–$45/pp",
            "type": "estimated"
          },
          "status": "planned"
        }
      ],
      "tip": "💡 Buy the park pass at the visitor center — it covers all the overlooks on the byway."
    },
    {
      "dayNumber": 3,
      "title": "Town History & Local Museum",
      "subtitle": "Saturday, Sep 11",
      "category": "mixed",
      "drivingTime": "40 min",
      "drivingMiles": "22 mi",
      "stops": [
        {
          "id": "d3-s1",
          "time": "9:30 AM",
          "name": "Local history museum",
          "mapUrl": "https://maps.google.com/maps/search/local+history+museum",
          "placeholderEmoji": "🏛️",
          "description": "Small, well-curated collection on the area's maritime past.",
          "hours": "10 AM – 4 PM",
          "pricing": {
            "amount": "$10/pp",
            "type": "confirmed"
          },
          "coords": {
            "lat": 46.79,
            "lng": -92.085
          },
          "status": "planned"
        },
        {
          "id": "d3-s2",
          "time": "11:30 AM",
          "name": "Historic downtown walk",
          "mapUrl": "https://maps.google.com/maps/search/historic+downtown",
          "placeholderEmoji": "🗺️",
          "description": "Self-guided loop of restored storefronts and a lift bridge.",
          "pricing": {
            "amount": "$0",
            "type": "free"
          },
          "coords": {
            "lat": 46.7895,
            "lng": -92.093
          },
          "status": "planned"
        },
        {
          "id": "d3-s3",
          "time": "1:00 PM",
          "name": "Lunch downtown",
          "mapUrl": "https://maps.google.com/maps/search/downtown+lunch",
          "placeholderEmoji": "🍽️",
          "description": "Varied menus along the main street.",
          "pricing": {
            "amount": "$18–$28/pp",
            "type": "estimated"
          },
          "status": "planned"
        },
        {
          "id": "d3-s4",
          "time": "2:30 PM",
          "name": "Optional harbor boat tour",
          "mapUrl": "https://maps.google.com/maps/search/harbor+boat+tour",
          "placeholderEmoji": "⛵",
          "description": "90-minute narrated cruise. Optional, weather permitting.",
          "reservation": "Recommended",
          "pricing": {
            "amount": "$25–$35/pp",
            "type": "optional"
          },
          "coords": {
            "lat": 46.782,
            "lng": -92.096
          },
          "status": "planned"
        },
        {
          "id": "d3-s5",
          "time": "6:30 PM",
          "name": "Farewell dinner",
          "mapUrl": "https://maps.google.com/maps/search/dinner+downtown",
          "placeholderEmoji": "🍽️",
          "description": "A nicer sit-down dinner for the last evening.",
          "pricing": {
            "amount": "$35–$55/pp",
            "type": "estimated"
          },
          "status": "planned"
        }
      ],
      "tip": "💡 The boat tour is optional and weather-dependent — keep it flexible."
    },
    {
      "dayNumber": 4,
      "title": "Departure",
      "subtitle": "Sunday, Sep 12",
      "category": "departure",
      "drivingTime": "2h 15m",
      "drivingMiles": "120 mi",
      "stops": [
        {
          "id": "d4-s1",
          "time": "8:30 AM",
          "name": "Breakfast & check out",
          "mapUrl": "https://maps.google.com/maps/search/Lakeside+Lodge",
          "placeholderEmoji": "🍽️",
          "description": "Final included breakfast, then check out.",
          "pricing": {
            "amount": "$0 (included)",
            "type": "free"
          },
          "status": "planned"
        },
        {
          "id": "d4-s2",
          "time": "9:30 AM",
          "name": "Drive back to the airport",
          "mapUrl": "https://maps.google.com/maps/dir/Lakeside+Town/MSP",
          "placeholderEmoji": "🚗",
          "description": "Allow extra time to return the car.",
          "pricing": {
            "amount": "$0",
            "type": "free"
          },
          "status": "planned"
        },
        {
          "id": "d4-s3",
          "time": "12:30 PM",
          "name": "Depart (MSP)",
          "mapUrl": "https://maps.google.com/maps/search/Minneapolis+Saint+Paul+Airport",
          "placeholderEmoji": "✈️",
          "description": "Flight home.",
          "pricing": {
            "amount": "$0 (in flights)",
            "type": "free"
          },
          "coords": {
            "lat": 44.8848,
            "lng": -93.2223
          },
          "status": "planned"
        }
      ],
      "tip": "💡 Return the rental with a full tank — the nearest station to the airport runs pricey."
    }
  ],
  "costEstimate": {
    "categories": [
      {
        "emoji": "✈️",
        "name": "Flights",
        "items": [
          {
            "item": "Round-trip airfare (2 people)",
            "detail": "Sample estimate",
            "cost": {
              "budget": 360,
              "mid": 480,
              "high": 620
            },
            "priceType": "estimated"
          }
        ]
      },
      {
        "emoji": "🚗",
        "name": "Car Rental",
        "items": [
          {
            "item": "4-day rental (midsize)",
            "detail": "Sample estimate, incl. taxes/fees",
            "cost": {
              "budget": 240,
              "mid": 300,
              "high": 380
            },
            "priceType": "estimated"
          },
          {
            "item": "Gas (~340 miles)",
            "detail": "~12 gal",
            "cost": {
              "budget": 42,
              "mid": 48,
              "high": 55
            },
            "priceType": "estimated"
          }
        ]
      },
      {
        "emoji": "🏨",
        "name": "Lodging",
        "items": [
          {
            "item": "Lakeside Lodge (3 nights)",
            "detail": "Lake-view room, breakfast included",
            "cost": {
              "budget": 420,
              "mid": 480,
              "high": 540
            },
            "priceType": "estimated"
          }
        ]
      },
      {
        "emoji": "🎟️",
        "name": "Attractions",
        "items": [
          {
            "item": "State Park entry",
            "detail": "$7/vehicle",
            "cost": {
              "budget": 7,
              "mid": 7,
              "high": 7
            },
            "priceType": "confirmed"
          },
          {
            "item": "Local history museum",
            "detail": "$10/pp × 2",
            "cost": {
              "budget": 20,
              "mid": 20,
              "high": 20
            },
            "priceType": "confirmed"
          },
          {
            "item": "Harbor boat tour (optional)",
            "detail": "$25–$35/pp × 2",
            "cost": {
              "budget": 0,
              "mid": 60,
              "high": 70
            },
            "priceType": "estimated"
          }
        ]
      },
      {
        "emoji": "🍽️",
        "name": "Dining",
        "items": [
          {
            "item": "Breakfasts (2 paid; others included)",
            "detail": "Lodge breakfast included 3 mornings",
            "cost": {
              "budget": 30,
              "mid": 45,
              "high": 60
            },
            "priceType": "estimated"
          },
          {
            "item": "Lunches (3 days × 2)",
            "detail": "Casual cafés",
            "cost": {
              "budget": 110,
              "mid": 150,
              "high": 190
            },
            "priceType": "estimated"
          },
          {
            "item": "Dinners (4 nights × 2)",
            "detail": "Casual to one nicer dinner",
            "cost": {
              "budget": 260,
              "mid": 360,
              "high": 480
            },
            "priceType": "estimated"
          }
        ]
      },
      {
        "emoji": "💳",
        "name": "Miscellaneous",
        "items": [
          {
            "item": "Parking, tips, souvenirs",
            "detail": "Full-trip estimate",
            "cost": {
              "budget": 50,
              "mid": 90,
              "high": 140
            },
            "priceType": "estimated"
          }
        ]
      }
    ],
    "tips": [
      "This is sample data — replace it with your own trips via the trip-planner and trip-exporter skills.",
      "Costs are shown as budget / mid / high so you can plan to a comfort level.",
      "Stops without coordinates (drives, meals) simply won't appear as map pins."
    ],
    "totals": {
      "budget": 1539,
      "mid": 2040,
      "high": 2562
    }
  }
});
