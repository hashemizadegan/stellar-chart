from datetime import date, datetime, time, timezone

from app.astrology.chart import angle_between, house_of, natal_chart, sign_of
from app.astrology.geo import local_to_utc
from app.astrology.transits import transits_for


def test_sign_of():
    assert sign_of(0)["sign"] == "Aries"
    assert sign_of(45.5)["formatted"] == "15°30' Taurus"
    assert sign_of(359.9)["sign"] == "Pisces"


def test_angle_between_wraps():
    assert angle_between(350, 10) == 20
    assert angle_between(10, 190) == 180


def test_historical_dst():
    # New York, July 1975 was on daylight time (UTC-4)
    utc = local_to_utc(date(1975, 7, 4), time(12, 0), "America/New_York")
    assert utc == datetime(1975, 7, 4, 16, 0, tzinfo=timezone.utc)


def test_known_chart_sun_sign():
    # Sun enters Aries around March 20; April 10 must be Aries, the Sun near 20° Aries.
    dt = datetime(2000, 4, 10, 12, 0, tzinfo=timezone.utc)
    chart = natal_chart(dt, 51.5074, -0.1278)
    assert chart["planets"]["Sun"]["sign"] == "Aries"
    assert 19 < chart["planets"]["Sun"]["degree"] < 22
    assert len(chart["houses"]) == 12
    assert chart["summary"]["rising"] is not None
    for p in chart["planets"].values():
        assert 1 <= p["house"] <= 12


def test_unknown_time_has_no_houses():
    dt = datetime(1990, 1, 1, 12, 0, tzinfo=timezone.utc)
    chart = natal_chart(dt, 35.0844, -106.6504, time_known=False)
    assert chart["houses"] is None and chart["summary"]["rising"] is None


def test_polar_latitude_falls_back():
    dt = datetime(1990, 6, 21, 12, 0, tzinfo=timezone.utc)
    chart = natal_chart(dt, 78.2, 15.6)  # Svalbard
    assert chart["house_system"] in ("Placidus", "Whole Sign")


def test_house_of():
    cusps = [i * 30.0 for i in range(12)]
    assert house_of(5, cusps) == 1 and house_of(359, cusps) == 12


def test_transits():
    natal = natal_chart(datetime(1990, 1, 1, 12, tzinfo=timezone.utc), 40.7, -74.0)
    t = transits_for(natal, datetime(2026, 9, 29, 12, tzinfo=timezone.utc))
    assert t["date"] == "2026-09-29" and "Sun" in t["sky"]
