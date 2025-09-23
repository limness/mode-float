from typing import Optional, Protocol, Tuple, Any, List
import pandas as pd
import holidays
import re

from flight import Flight
from geocoder import Geocoder


class Mapper(Protocol):
    def map_row(self, row: pd.Series) -> Flight: ...


class DefaultMapper(Mapper):
    def __init__(self, geocoder: Geocoder):
        self.geocoder = geocoder
        self.holidays = holidays.RU()

    def map_row(self, row: pd.Series) -> Flight:
        city = row.get("Центр ЕС ОрВД", "")
        raw_shr = row.get("SHR", "")
        raw_dep = row.get("DEP", "")
        raw_arr = row.get("ARR", "")

        sid = self._extract(raw_dep, r"-SID\s+(\d+)") or ""
        uav_type = self._extract(raw_shr, r"TYP/([A-Z0-9]+)") or "UNKNOWN"

        route_lines = re.findall(r"^-M.*$", raw_shr, flags=re.MULTILINE)
        route_points = []
        for line in route_lines:
            coords = re.findall(r"\d{4,6}[NSСЮ]\d{5,7}[EWВЗ]", line)
            for c in coords:
                pt = self.geocoder.parse_latlon(c)
                if pt:
                    route_points.append(pt)

        takeoff_coords = self.geocoder.parse_latlon(
            self._extract(
                raw_dep, r"-ADEPZ\b[\s\S]*?(\d{4,6}[NSСЮ]\d{5,7}[EWВЗ])")
        )
        landing_coords = self.geocoder.parse_latlon(
            self._extract(
                raw_arr, r"-ADARRZ\b[\s\S]*?(\d{4,6}[NSСЮ]\d{5,7}[EWВЗ])")
        )

        dof = self._extract(raw_dep, r"-ADD\s+(\d{6})")
        dep_time = self._make_timestamp(
            dof, self._extract(raw_dep, r"-ATD\s+(\d{4})"))
        arr_time = self._make_timestamp(
            dof, self._extract(raw_arr, r"-ATA\s+(\d{4})"))

        duration = None
        if dep_time is not None and arr_time is not None:
            duration = arr_time - dep_time

        is_weekend = dep_time and dep_time.weekday() >= 5
        is_holiday = dep_time and dep_time.date() in self.holidays

        return Flight(
            flight_id=sid,
            uav_type=uav_type,
            takeoff_coords=takeoff_coords,
            landing_coords=landing_coords,
            dep_datetime=dep_time,
            arr_datetime=arr_time,
            duration=duration,
            route_points=route_points or None,
            city=city,
            is_weekend=is_weekend,
            is_holiday=is_holiday,
            raw=row.to_dict()
        )

    def _extract(self, text: Any, pattern: str) -> Optional[str]:
        text = str(text) if text is not None else ""
        m = re.search(pattern, text)
        return m.group(1) if m else None

    def _make_timestamp(self, yymmdd: Optional[str], hhmm: Optional[str]) -> Optional[pd.Timestamp]:
        if yymmdd and hhmm:
            return pd.to_datetime(yymmdd + hhmm, format="%y%m%d%H%M", errors="coerce")
        return None
