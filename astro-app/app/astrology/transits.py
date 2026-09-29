"""Daily transits: today's sky compared with the natal chart."""
from datetime import datetime, timezone

from app.astrology.chart import find_aspects, julian_day, planet_positions

# Tighter orbs for transits so the reading focuses on what is exact now.
TRANSIT_ORB_SCALE = 0.35


def transits_for(natal: dict, when: datetime | None = None) -> dict:
    when = when or datetime.now(timezone.utc)
    today = planet_positions(julian_day(when))
    natal_points = dict(natal["planets"])
    if natal.get("angles"):
        natal_points.update(natal["angles"])
    aspects = find_aspects(today, natal_points, orb_scale=TRANSIT_ORB_SCALE)
    # The Moon moves ~13°/day; its aspects are brief moods, keep only the closest.
    moon = [a for a in aspects if a["a"] == "Moon"][:2]
    others = [a for a in aspects if a["a"] != "Moon"][:8]
    return {
        "date": when.date().isoformat(),
        "sky": {k: {"formatted": v["formatted"], "retrograde": v["retrograde"]} for k, v in today.items()},
        "transits": others + moon,
    }
