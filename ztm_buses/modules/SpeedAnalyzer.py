from __future__ import annotations
from typing import Set, List
import pandas as pd

from .Bus import Bus
from .RoutesManager import RoutesManager
from .BusStopsManager import BusStopsManager


class SpeedAnalyzer:
    def __init__(self, buses: Set[Bus]) -> SpeedAnalyzer:
        self.__buses = buses

    def __speed_compute(self) -> List[float]:
        speeds: List = []
        for bus in self.__buses:
            val = bus.speed_compute()
            if val:
                speeds += val
        return speeds

    def get_speed_statistics(self):
        speeds: List[float] = self.__speed_compute()
        speeds_df_data = [(speed, coord.lon, coord.lat, vehicle_num, line_num)
                          for speed, coord, vehicle_num, line_num in speeds]
        speeds_df = pd.DataFrame(speeds_df_data, columns=[
                                 'speed', 'lon', 'lat', 'vehicle_number', 'line_number'])

        return speeds_df
