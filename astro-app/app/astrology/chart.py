"""Natal chart calculation with the Swiss Ephemeris (pyswisseph).

Licensing note: the Swiss Ephemeris is dual-licensed (AGPL or a paid
professional license from Astrodienst). Check the license before
running a closed-source commercial service.
"""
from datetime import datetime, timezone

import swisseph as swe

from app.config import get_settings

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS,
    "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
    "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO,
    "North Node": swe.TRUE_NODE,
}

# name: (angle, orb for natal chart)
ASPECTS = {
    "conjunction": (0, 8), "opposition": (180, 8), "trine": (120, 7),
    "square": (90, 7), "sextile": (60, 5),
}

_settings = get_settings()
if _settings.se_ephe_path:
    swe.set_ephe_path(_settings.se_ephe_path)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED
else:
    FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED  # built-in, no data files needed


def julian_day(dt_utc: datetime) -> float:
    dt = dt_utc.astimezone(timezone.utc)
    hour = dt.hour + dt.minute / 60 + dt.second / 3600
    return swe.julday(dt.year, dt.month, dt.day, hour, swe.GREG_CAL)


def sign_of(lon: float) -> dict:
    lon %= 360
    idx = int(lon // 30)
    deg_in_sign = lon - idx * 30
    d = int(deg_in_sign)
    m = int(round((deg_in_sign - d) * 60))
    if m == 60:
        d, m = d + 1, 0
    return {"sign": SIGNS[idx], "degree": round(deg_in_sign, 4), "formatted": f"{d}°{m:02d}' {SIGNS[idx]}"}


def planet_positions(jd: float) -> dict:
    out = {}
    for name, pid in PLANETS.items():
        xx, _ = swe.calc_ut(jd, pid, FLAGS)
        lon, speed = xx[0] % 360, xx[3]
        out[name] = {"longitude": round(lon, 4), "speed": round(speed, 4),
                     "retrograde": speed < 0, **sign_of(lon)}
    return out


def house_of(lon: float, cusps: list[float]) -> int:
    for i in range(12):
        start, end = cusps[i], cusps[(i + 1) % 12]
        span = (end - start) % 360
        if (lon - start) % 360 < span:
            return i + 1
    return 12


def angle_between(a: float, b: float) -> float:
    diff = abs(a - b) % 360
    return 360 - diff if diff > 180 else diff


def find_aspects(pos_a: dict, pos_b: dict | None = None, orb_scale: float = 1.0) -> list[dict]:
    """Aspects within one chart (pos_b None) or between two charts (transits)."""
    results = []
    names_a = list(pos_a)
    same = pos_b is None
    pos_b = pos_a if same else pos_b
    for i, a in enumerate(names_a):
        for b in (names_a[i + 1:] if same else list(pos_b)):
            sep = angle_between(pos_a[a]["longitude"], pos_b[b]["longitude"])
            for asp, (ang, orb) in ASPECTS.items():
                delta = abs(sep - ang)
                if delta <= orb * orb_scale:
                    results.append({"a": a, "b": b, "aspect": asp, "orb": round(delta, 2)})
    return sorted(results, key=lambda x: x["orb"])


def natal_chart(dt_utc: datetime, lat: float, lon: float, time_known: bool = True) -> dict:
    jd = julian_day(dt_utc)
    planets = planet_positions(jd)
    chart = {"planets": planets, "time_known": time_known, "house_system": None,
             "houses": None, "angles": None}

    if time_known:
        hsys = b"P"  # Placidus
        try:
            cusps, ascmc = swe.houses_ex(jd, lat, lon, hsys)
        except swe.Error:
            hsys = b"W"  # Placidus fails near the poles; fall back to Whole Sign
            cusps, ascmc = swe.houses_ex(jd, lat, lon, hsys)
        cusps = list(cusps)[-12:]
        chart["house_system"] = "Placidus" if hsys == b"P" else "Whole Sign"
        chart["houses"] = [{"house": i + 1, "longitude": round(c, 4), **sign_of(c)}
                           for i, c in enumerate(cusps)]
        chart["angles"] = {"Ascendant": {"longitude": round(ascmc[0], 4), **sign_of(ascmc[0])},
                           "Midheaven": {"longitude": round(ascmc[1], 4), **sign_of(ascmc[1])}}
        for p in planets.values():
            p["house"] = house_of(p["longitude"], cusps)

    chart["aspects"] = find_aspects(planets)
    elements = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    for name in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        idx = SIGNS.index(planets[name]["sign"])
        elements[["Fire", "Earth", "Air", "Water"][idx % 4]] += 1
    chart["elements"] = elements
    chart["summary"] = {
        "sun": planets["Sun"]["sign"],
        "moon": planets["Moon"]["sign"],
        "rising": chart["angles"]["Ascendant"]["sign"] if chart["angles"] else None,
    }
    return chart
