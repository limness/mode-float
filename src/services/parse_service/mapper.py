import re
from math import atan2, cos, radians, sin, sqrt
from typing import Any, Optional, Protocol

import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

from src.database.models import UavFlightModel

from .geocoder import Geocoder


def ensure_aware(x, tz="Europe/Moscow"):
    tz = ZoneInfo(tz) if isinstance(tz, str) else tz
    if x is None:
        return None
    if isinstance(x, pd.Timestamp):
        x = x if x.tzinfo else x.tz_localize(tz)
        return x.to_pydatetime()
    if isinstance(x, datetime):
        return x if x.tzinfo else x.replace(tzinfo=tz)
    x = pd.to_datetime(x)
    x = x if x.tzinfo else x.tz_localize(tz)
    return x.to_pydatetime()


class Mapper(Protocol):
    def map_row(self, row: pd.Series) -> UavFlightModel: ...


class DefaultMapper(Mapper):
    def __init__(self, geocoder: Geocoder):
        self.geocoder = geocoder

    def map_row(self, row: pd.Series) -> UavFlightModel:
        city = row.get('Центр ЕС ОрВД', '')
        raw_shr = row.get('SHR', '')
        raw_dep = row.get('DEP', '')
        raw_arr = row.get('ARR', '')

        sid = self._extract(raw_dep, r'-SID\s+(\d+)') or ''
        uav_type = self._extract(raw_shr, r'TYP/([A-Z0-9]+)') or 'UNKNOWN'

        route_lines = re.findall(r'^-M.*$', raw_shr, flags=re.MULTILINE)
        route_points = []
        for line in route_lines:
            coords = re.findall(r'\d{4,6}[NSСЮ]\d{5,7}[EWВЗ]', line)
            for c in coords:
                pt = self.geocoder.parse_latlon(c)
                if pt:
                    route_points.append(pt)

        takeoff_coords = self.geocoder.parse_latlon(
            self._extract(raw_dep, r'-ADEPZ\b[\s\S]*?(\d{4,6}[NSСЮ]\d{5,7}[EWВЗ])')
        )
        landing_coords = self.geocoder.parse_latlon(
            self._extract(raw_arr, r'-ADARRZ\b[\s\S]*?(\d{4,6}[NSСЮ]\d{5,7}[EWВЗ])')
        )

        dof = self._extract(raw_dep, r'-ADD\s+(\d{6})')
        dep_time = ensure_aware(self._make_timestamp(dof, self._extract(raw_dep, r'-ATD\s+(\d{4})')))
        arr_time = ensure_aware(self._make_timestamp(dof, self._extract(raw_arr, r'-ATA\s+(\d{4})')))

        date = None
        if dep_time is not None:
            date = dep_time
        elif arr_time is not None:
            date = arr_time

        duration = None
        if dep_time is not None and arr_time is not None:
            duration = (arr_time - dep_time).seconds / 60

        takeoff_lat, takeoff_lon = None, None
        landing_lat, landing_lon = None, None
        latitude, longitude = None, None
        if landing_coords is not None:
            landing_lat, landing_lon = landing_coords
            latitude, longitude = landing_lat, landing_lon
        if takeoff_coords is not None:
            takeoff_lat, takeoff_lon = takeoff_coords
            latitude, longitude = takeoff_coords

        distance_km = None
        if landing_coords is not None and takeoff_coords is not None:
            distance_km = self._haversine(takeoff_lat, takeoff_lon, landing_lat, landing_lon)
        average_speed_kmh = None
        if distance_km is not None and duration > 0:
            average_speed_kmh = distance_km / duration * 60

        return UavFlightModel(
            flight_id=sid,
            uav_type=uav_type,
            takeoff_lat=takeoff_lat,
            takeoff_lon=takeoff_lon,
            landing_lat=landing_lat,
            landing_lon=landing_lon,
            latitude=latitude,
            longitude=longitude,
            takeoff_datetime=dep_time,
            landing_datetime=arr_time,
            date=date,
            duration_minutes=duration,
            city=city,
            distance_km=distance_km,
            average_speed_kmh=average_speed_kmh,
        )

    def _extract(self, text: Any, pattern: str) -> str | None:
        text = str(text) if text is not None else ''
        m = re.search(pattern, text)
        return m.group(1) if m else None

    def _make_timestamp(self, yymmdd: str | None, hhmm: str | None) -> Optional[pd.Timestamp]:
        if yymmdd and hhmm:
            return pd.to_datetime(yymmdd + hhmm, format='%y%m%d%H%M', errors='coerce')
        return None

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371.0

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance
