from __future__ import annotations
from datetime import datetime as dt
from datetime import timedelta
from timeit import default_timer as timer
from math import ceil
from collections import defaultdict
from typing import Dict, List, Tuple, DefaultDict

from .Coordinates import Coordinates
from .BusStopsManager import BusStopsManager
from .RoutesManager import RoutesManager
from .TimetableManager import TimeTableMangager


class Bus:
    def __init__(self, vehicle_num: str):
        self.__vehicle = vehicle_num
        self.__lines: List[str] = []
        self.__brigades: List[str] = []
        self.__timetable: Dict[str, Dict[str, List[Dict[str, str]]]] = {}
        self.__route_path: Dict[str, Tuple[str, List[dt]]] = {}
        self.__state: List[Tuple[dt, Coordinates]] = []
        self.__route = None
        self.__passed_station: str = None
        self.__current_state: int = 0

    @property
    def vehicle(self):
        return self.__vehicle
    
    # the following 3 methods are mainly for unit testing purposes
    def get_all_states(self):
        return tuple(self.__state)
    
    def get_all_lines(self):
        return tuple(self.__lines)
    
    def get_all_brigades(self):
        return tuple(self.__brigades)

    def __hash__(self) -> int:
        return hash(self.__vehicle)

    def __eq__(self, other):
        return self.__vehicle == other.__vehicle

    def update(self, line: str, brigade: str, longtitude: float, latitude: float, time: dt):
        # I do not add the same time
        if not self.__state or self.__state[-1][0] != time:
            coor = Coordinates(longtitude, latitude)
            
            ok_brigade = (brigade != " " and brigade != "")
            try:
                true_brigade = brigade if ok_brigade else self.__brigades[-1]
            except IndexError: return
            self.__brigades.append(true_brigade)
            self.__state.append((time, coor))
            self.__lines.append(line)
            

    def set_timetable(self, timetable_manager: TimeTableMangager) -> None:
        for line, brigade in zip(self.__lines, self.__brigades):
            key = line + "," + brigade
            # I connect line and brigade to get the unique key
            if line not in self.__timetable:
                try:
                    self.__timetable[key] = timetable_manager.get_schedule(
                        line, brigade)
                except KeyError:
                    raise RuntimeError("No suitable timetable found")

    def __get_current_timetable(self):
        return self.__timetable[self.line + "," + self.brigade]

    def get_vehicle_number(self) -> str:
        return self.__vehicle

    def number_of_states(self):
        return len(self.__state)

    def __str__(self) -> str:
        return str(self.__state)

    def __get_next_state(self):
        """sometimes in the data we have 2 different times but the same coordinates
        when a bus is stationery
         this function returns the first state that had change in its position."""
        current_coordinates = self.__state[self.__current_state][1]
        for i in range(self.__current_state + 1, len(self.__state)):
            next_state_coor = self.__state[i][1]
            if next_state_coor - current_coordinates != 0:
                return self.__state[i]
        return self.__state[self.__current_state]

    @property
    def line(self) -> str:
        return self.__lines[self.__current_state]

    @property
    def brigade(self) -> str:
        return self.__brigades[self.__current_state]

    def speed_compute(self) -> list[Tuple[int, Coordinates, str, str]]:
        result = []
        for past, future in zip(self.__state, self.__state[1:]):
            time: float = (future[0] - past[0]).total_seconds()

            if time != 0:
                # 3.6 is conversion m/s to km/h
                speed = ceil(3.6 * (future[1]-past[1])/time)
                result.append((speed, past[1], self.__vehicle, self.line))
        return result

    def determine_route(self, routes: RoutesManager) -> None:
        some_list = []
        def time_difference(entry): return abs(
            (entry['Time'] - self.__state[self.__current_state][0]).total_seconds())
        for time_entry in self.__get_current_timetable().values():
            some_list.append(min(time_entry, key=time_difference))

        if not some_list:
            return
        min_time = min(some_list, key=time_difference)
        self.__route = min_time["Route"]
        path = routes.get_route(self.line, self.__route)

        for num, busstop in path.items():
            times = self.__get_current_timetable().get(busstop)
            if times is None:
                times = []
            self.__route_path[num] = (busstop, [x['Time'] for x in times])

    def __determine_passed_stop(self, busstops: BusStopsManager) -> None:
        if not self.__route_path or self.__current_state >= len(self.__state) - 1:
            return
        temp_list = []
        for index, busstop_with_time in self.__route_path.items():
            busstop = busstop_with_time[0]
            try:
                distance = self.__state[self.__current_state][1] - \
                    busstops.get_coordinates(busstop)
            except KeyError:
                # Sometimes there's a problem with busstops that are suspended
                # but it is still present in the routes.
                continue
            temp_list.append((index, distance))

        # Sorting is O(N log N) but here the data is restricted to max 20-30 values so doing
        # O(N) will take more
        two_min_values = sorted(temp_list, key=lambda x: x[1])[0:2]

        # Make the first busstop the former one
        if int(two_min_values[0][0]) > int(two_min_values[1][0]):
            two_min_values.reverse()

        future_distances = [(index, busstops.get_coordinates(
                            self.__route_path[index][0]) - self.__get_next_state()[1])
                            for index, _ in two_min_values]

        """
    Four cases:
    1. Distance to the former one increased, the latter one decreased -> bus heads to the latter one
    2. Distance to the former one decreased, the latter one increased -> bus heads to the latter one
    3. Two distances decreased -> bus goes to the former bus stop
    4. Two distance increased bus passed the later bus stop
        """
        def helper(index):
            return future_distances[index][1] - two_min_values[index][1]

        if helper(0) > 0:
            if helper(1) < 0: self.__passed_station = two_min_values[0][0]
            else: self.__passed_station = two_min_values[1][0]
        else: self.__passed_station = str(int(two_min_values[0][0]) - 1)

    def punctuality_compute(self, busstops: BusStopsManager,
                            routes: RoutesManager) -> DefaultDict[str, List[Dict[str, str]]]:
        self.__determine_passed_stop(busstops)
        meters_to_stop = 10
        offset_in_meters = 5
        delay: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        if self.__passed_station is None:
            return delay
        passed_stop = int(self.__passed_station)+1

        prev_line = self.line
        prev_brigade = self.brigade
        check_for_route = False

        while self.__current_state < len(self.__state) - 1:
            if passed_stop >= len(self.__route_path) or check_for_route \
                    or prev_line != self.line \
                    or prev_brigade != self.brigade:
                check_for_route = False
                self.__current_state += 1
                self.determine_route(routes)
                prev_line = self.line
                prev_brigade = self.brigade
                passed_stop = int(self.__passed_station)+1
                continue

            present_time, present_coord = self.__state[self.__current_state]
            busstop, arrival_times = self.__route_path[f"{passed_stop}"]
            if not arrival_times:
                self.__current_state += 1
                self.__determine_passed_stop(busstops)
                passed_stop = int(self.__passed_station)+1
                continue

            try:
                # sometimes there is a mismatch between the busstops for the day
                # When a busstop is suspended but a route still has it. It is pretty rare though
                busstop_coord = busstops.get_coordinates(busstop)
            except KeyError:
                continue
            present_distance = present_coord - busstop_coord
            if present_distance < meters_to_stop:  # We consider that the bus arrived at the bus stop
                passed_stop += 1
                self.__current_state += 1
                time_diff = [(present_time - arrival_time).total_seconds()
                             for arrival_time in arrival_times]
                min_time_diff = min(time_diff, key=lambda x: abs(x))
                delay[busstop].append({"Line": self.line, "Arrived": present_time,
                                      "Expected": arrival_times[time_diff.index(min_time_diff)]})
                continue

            future_time, future_coord = self.__state[self.__current_state+1]
            if future_coord == present_coord:
                self.__current_state += 1
                continue
            future_distance = future_coord - busstop_coord

            if future_distance < meters_to_stop or future_distance - offset_in_meters < present_distance:
                self.__current_state += 1
                continue

            check_for_further_distance = False
            for j in range(self.__current_state + 2, min(self.__current_state + 10, len(self.__state))):
                far_future_coor = self.__state[j][1]
                if far_future_coor - busstop_coord < present_distance - offset_in_meters:
                    self.__current_state = j
                    check_for_further_distance = True
                    break
            if check_for_further_distance:
                continue

            if (future_time - present_time).total_seconds() > 60:  # Too big gap in time
                self.__current_state += 1
                self.__determine_passed_stop(busstops)
                passed_stop = int(self.__passed_station)+1
                continue

            # Case: present_distance > future_distance means that we gone past the stop
            # and we are more than 10 m from it
            # We do some rough approximations that includes speed
            # Calculate the speed between these two points, find the time required to get to the stop
            # add to the present_time and compare with the expected time
            if future_distance < 500:
                self.__current_state += 1
                passed_stop += 1
                time_diff = (future_time - present_time).total_seconds()
                # in m/s:
                speed1 = ceil((future_coord - present_coord) / time_diff) + 1
                speed2 = ceil((future_distance - present_distance) / time_diff) + 1  
                
                # speed2 better represent a situation where a bus passed the
                # latter bus stop but it may give unrealistic result,
                # hence I impose a treshhold
                speed = speed1 if speed2 > 50 else speed2

                time_to_stop = timedelta(seconds=int((present_distance / speed)))
                time_of_arrival = present_time + time_to_stop

                time_diff = [(time_of_arrival - arrival_time).total_seconds()
                             for arrival_time in arrival_times]
                min_time_diff = min(time_diff, key=lambda x: abs(x))
                delay[busstop].append({"Line": self.line, "Arrived": time_of_arrival,
                                      "Expected": arrival_times[time_diff.index(min_time_diff)]})
            else:
                check_for_route = True

        return delay
