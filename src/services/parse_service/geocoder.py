from typing import Optional, Protocol, Tuple
import re


class Geocoder(Protocol):
    def parse_latlon(self, val: Optional[str]
                     ) -> Optional[Tuple[float, float]]: ...


class DefaultGeocoder(Geocoder):
    def parse_latlon(self, val: Optional[str]) -> Optional[Tuple[float, float]]:
        if val is None:
            return None
        s = val.strip().upper().replace("°", "").replace("'", "").replace(
            '"', "").replace(",", " ").replace("  ", " ")
        s = (
            s.replace("С", "N")
             .replace("Ю", "S")
             .replace("В", "E")
             .replace("З", "W")
        )

        m_lat = re.search(r'([NS])', s)
        m_lon = re.search(r'([EW])', s)
        if not m_lat or not m_lon:
            return None
        lat_dir = m_lat.group(1)
        lon_dir = m_lon.group(1)
        lat_part = s[:m_lat.start()].strip()
        lon_part = s[m_lat.end():m_lon.start()].strip()
        if not lat_part:
            return None
        if not lon_part:
            return None

        lat_dec = self._parse_part(lat_part)
        lon_dec = self._parse_part(lon_part)
        if lat_dec is None or lon_dec is None:
            return None
        if lat_dir == 'S':
            lat_dec = -lat_dec
        if lon_dir == 'W':
            lon_dec = -lon_dec
        return lat_dec, lon_dec

    def _parse_part(self, part: str) -> Optional[float]:
        part = part.replace(" ", "")
        m = re.match(r'^(\d+)(\d{2}(?:\.\d+)?)$', part)
        if not m:
            return None
        deg_str, min_str = m.group(1), m.group(2)
        deg = int(deg_str)
        minutes = float(min_str)
        return deg + minutes / 60.0
