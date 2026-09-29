"""Birthplace -> coordinates -> historical time zone -> UTC moment of birth."""
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

from app.config import get_settings

_tf = TimezoneFinder()


@dataclass
class Place:
    display_name: str
    latitude: float
    longitude: float
    timezone: str


class PlaceNotFound(Exception):
    pass


def geocode(place: str) -> Place:
    geolocator = Nominatim(user_agent=get_settings().geocoder_user_agent, timeout=10)
    loc = geolocator.geocode(place, language="en")
    if not loc:
        raise PlaceNotFound(f"Could not find '{place}'. Try adding the region or country.")
    tz = _tf.timezone_at(lat=loc.latitude, lng=loc.longitude)
    if not tz:
        raise PlaceNotFound(f"Could not determine the time zone for '{place}'.")
    return Place(loc.address, loc.latitude, loc.longitude, tz)


def local_to_utc(d: date, t: time, tz_name: str) -> datetime:
    """Convert a local birth date/time to UTC using the IANA database.

    The IANA database contains historical offsets and daylight-saving rules,
    so a 1975 birth uses the 1975 rules for that location, not today's.
    """
    local = datetime.combine(d, t).replace(tzinfo=ZoneInfo(tz_name))
    return local.astimezone(timezone.utc)
