from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any, List
import pandas as pd
from datetime import timedelta


@dataclass
class Flight:
    flight_id: str
    uav_type: str
    takeoff_coords: Optional[Tuple[float, float]]
    landing_coords: Optional[Tuple[float, float]]
    dep_datetime: Optional[pd.Timestamp]
    arr_datetime: Optional[pd.Timestamp]
    duration: Optional[timedelta]
    city: str
    route_points: Optional[List[Tuple[float, float]]]
    is_weekend: Optional[bool]
    is_holiday: Optional[bool]
    raw: Dict[str, Any]
