from __future__ import annotations
import json
from typing import Set
import pandas as pd


from .modules.Bus import Bus
from .modules.SpeedAnalyzer import SpeedAnalyzer
from .modules.BusStopsManager import BusStopsManager
from .modules.RoutesManager import RoutesManager
from .modules.PunctualityAnalyzer import PunctualityAnalyzer
from .modules.TimetableManager import TimeTableMangager
from .modules.time_changer import time_changer


class BusStatistician:
  def __init__(self, bus_coordinates_file : str, timetable_file: str, routes_file : str, bus_stops_file : str):
    routes = RoutesManager(routes_file)
    bus_stops = BusStopsManager(bus_stops_file)
    timetable = TimeTableMangager(timetable_file)
    buses = self.__set_buses(bus_coordinates_file, timetable, routes)
    self.__speed_analyzer = SpeedAnalyzer(buses)
    self.__punctuality_analyzer = PunctualityAnalyzer(buses, bus_stops, routes)
    
    
  def __set_buses(self, buses_file : str, timetable : TimeTableMangager, routes : RoutesManager) -> Set[Bus]:
    with open(buses_file,'r', encoding='utf8') as file:
      temp_dict = json.load(file)
    
    buses : Set[Bus] = set()
    #register buses
    for bus_num in temp_dict["0"].keys():
      buses.add(Bus(bus_num)) 

    for all_buses in temp_dict.values():
      for bus in buses:
        params = all_buses.get(bus.get_vehicle_number())
        if params is not None: bus.update(params["Lines"], params["Brigade"],
                                          params["Lon"], params["Lat"],
                                          time_changer(params["Time"]))

    
    filtered_buses = []
    for bus in buses: 
      try:
        bus.set_timetable(timetable)
        filtered_buses.append(bus)
      except RuntimeError: pass

    filtered_buses = filter(lambda  x : x.number_of_states() > 1, filtered_buses)  
    buses = set(filtered_buses)
    
    for bus in buses: bus.determine_route(routes)
    return buses
  
 
  def get_speed_statistics(self) -> pd.DataFrame:
    df = self.__speed_analyzer.get_speed_statistics()
    return df
  
  
  
  def get_punctuality_statistics(self) -> pd.DataFrame:
    df = self.__punctuality_analyzer.compute_punctuality()
    return df
  