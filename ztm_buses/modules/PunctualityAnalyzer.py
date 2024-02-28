from __future__ import annotations
from typing import Set
import pandas as pd

from .Bus import Bus
from .BusStopsManager import BusStopsManager
from .RoutesManager import RoutesManager


class PunctualityAnalyzer:
    def __init__(self, buses: Set[Bus], bus_stops_manager: BusStopsManager,
                 routes_manager: RoutesManager) -> PunctualityAnalyzer:
        self.__buses = buses
        self.__bus_stops_manager = bus_stops_manager
        self.__routes_manager = routes_manager

    def compute_punctuality(self):
        counter = 0
        result = []
        bus_stop_name = self.__bus_stops_manager.get_bus_stop_name
        for bus in self.__buses:
            delay = bus.punctuality_compute(
                self.__bus_stops_manager, self.__routes_manager)
            counter += 1
            if counter % 100 == 0:
                print(f"{counter}/{len(self.__buses)} done")
            if delay:
                for busstop, list_of_info in delay.items():
                    coordinates = self.__bus_stops_manager.get_coordinates(
                        busstop)
                    for info in list_of_info:
                        result.append((bus.vehicle, info["Line"], busstop,
                                       bus_stop_name(busstop), coordinates.lon,
                                       coordinates.lat, info["Arrived"], info["Expected"]))

        df = pd.DataFrame(result, columns=['Bus_num', 'Line', 'Busstop_id',
                                           'Busstop_name', 'Lon', 'Lat',
                                           'Arrived', 'Expected'])
        df['Delay [min]'] = round((df['Arrived'] - df['Expected'])
                                  / pd.Timedelta(minutes=1), 2)

        return df
