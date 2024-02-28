from __future__ import annotations
from typing import KeysView
import json

from .Coordinates import Coordinates


class BusStopsManager:
    def __init__(self, filename: str) -> BusStopsManager:
        self.__bus_stops = {}
        self.__bus_stop_names = {}
        with open(filename, 'r', encoding='utf8') as file:
            busstop_coordinates = json.load(file)

        for busstop, val in busstop_coordinates.items():
            # busstop is string of the form "XXXX,XX"
            coord = val["Lon,Lat"]
            name = val["stop_name"]
            bus_complex_id = busstop.split(',')[0]
            self.__bus_stops[busstop] = Coordinates(
                float(coord[0]), float(coord[1]))
            if bus_complex_id not in self.__bus_stop_names:
                self.__bus_stop_names[bus_complex_id] = name

    def get_coordinates(self, busstop: str):
        return self.__bus_stops[busstop]

    def get_bus_nums(self) -> KeysView[str]:
        return self.__bus_stops["0"].keys()

    def get_bus_stop_name(self, busstop: str) -> str:
        # busstop is string of the form "XXXX,XX"
        bus_complex_id, bus_stop_no = busstop.split(',')
        return self.__bus_stop_names[bus_complex_id] + " " + bus_stop_no
