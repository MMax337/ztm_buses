from __future__ import annotations
from typing import Dict, List
import json

from .time_changer import time_changer


class TimeTableMangager:
    def __init__(self, timetable_file: str) -> TimeTableMangager:
        with open(timetable_file, 'r', encoding='utf8') as file:
            self.__timetable: Dict[str, Dict[str, Dict[str,
                                                       List[Dict[str, str]]]]] = json.load(file)
        for brigade_busstom_time in self.__timetable.values():
            for busstop_time in brigade_busstom_time.values():
                for list_of_timetable in busstop_time.values():
                    for time_dict in list_of_timetable:
                        time_dict["Time"] = time_changer(time_dict["Time"])

    def get_schedule(self, line: str, brigade: str) -> Dict[str, List[Dict[str, str]]]:
        return self.__timetable[line][brigade]
