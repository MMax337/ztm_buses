from __future__ import annotations
import requests
import json
import time
from timeit import default_timer as timer
import concurrent.futures
from typing import Dict, List, Tuple, Optional, DefaultDict
from concurrent.futures import as_completed
from datetime import datetime
from collections import defaultdict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ZTMFetcher:
    def __init__(self, apikeys: List[str]) -> ZTMFetcher:
        self.__apikeys = apikeys
        self.__session = requests.Session()
        self.__session.mount(
            "https://", HTTPAdapter(max_retries=Retry(total=10, backoff_factor=0.5)))
        self.__number_of_requests: int = 0

        self.__bustram_endpoint = "https://api.um.warszawa.pl/api/action/busestrams_get/"
        self.__schedule_endpoint = "https://api.um.warszawa.pl/api/action/dbtimetable_get"
        self.__db_endpoint = "https://api.um.warszawa.pl/api/action/dbstore_get/"
        self.__routes_end_point = "https://api.um.warszawa.pl/api/action/public_transport_routes/?"

    def __send_request(self, endpoint: str, params_without_apikey: Dict[str, str]):
        time.sleep(0.01)
        self.__number_of_requests += 1
        apikey = self.__apikeys[(self.__number_of_requests//100) % len(self.__apikeys)]
        params_without_apikey['apikey'] = apikey
        response = self.__session.get(endpoint, params=params_without_apikey)
        return response

    def __log(self, error_msg: str):
        print(f"Wrong response: {error_msg}")

    def fetch_bus_location(self) -> Dict[str, Dict[str, str]]:
        params = {'resource_id': '%20f2e5503e%02927d-4ad3-9500-4ab9e55deb59', 'type': '1'}
        bus_data: Dict[str, Dict[str, str]] = {}
        while True:
            """ Sample respone
            {
              "result": [
                  {"Lines": "219", "Lon": 21.1128748, "VehicleNumber": "1000", 
                   "Time": "2024-02-04 21:19:45", "Lat": 52.213404,"Brigade": "3"
                  },
                  { ... },
                        ],
              },
            """
            response = self.__send_request(self.__bustram_endpoint, params)
            if not response:
                continue
            response_json = response.json()
            if not response_json['result']:
                raise RuntimeError('No Buses')
            try:
                for bus in response_json['result']:
                    date = bus['Time'].split(' ')[0]
                    if date == datetime.now().strftime('%Y-%m-%d'):
                        bus_data[bus['VehicleNumber']] = {
                            "Lines": bus["Lines"], "Lon": bus["Lon"], "Lat": bus["Lat"], 
                            "Time": bus["Time"], "Brigade": bus["Brigade"]}
                return bus_data
            except TypeError:
                self.__log(response_json)

    def fetch_bus_location_period(self, period_second: int, 
                                  output_filename: Optional[str] = None) -> None:
        bus_data: Dict[int, Dict[str, Dict[str, str]]] = {}
        i = 0
        times = period_second // 10
        start_time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        for _ in range(times):
            bus_data[i] = self.fetch_bus_location()
            print(f"Collection {i} done")
            i += 1
            time.sleep(10)

        output = output_filename if output_filename is not None else \
            f"bus_coordinates_{start_time}_duration_{int(period_second)}s.json"

        with open(output, "w", encoding='utf-8') as fp:
            json.dump(bus_data, fp, ensure_ascii=False)

    def __fetch_busstop_coordinates_helper(self) -> Dict[str, Tuple[float, float]]:
        params = {'id': '1c08a38c-ae09-46d2-8926-4f9d25cb0630'}
        busstop_coord: Dict[str, Tuple[float, float]] = {}
        while True:
            """ Sample response:
            {
              "result": [
                          {
                            "values": [
                                        {"value": "1001", "key": "zespol"},
                                        {"value": "01", "key": "slupek"},
                                        {"value": "Kijowska","key": "nazwa_zespolu"},
                                        {"value": "2201","key": "id_ulicy"},
                                        {"value": "52.248455","key": "szer_geo"},
                                        {"value": "21.044827","key": "dlug_geo"},
                                        {"value": "al.Zieleniecka","key": "kierunek"},
                                        {"value": "2023-09-23 00:00:00.0","key": "obowiazuje_od"}
                                      ]
                          },
                        ]
            }
            """
            response = self.__send_request(self.__db_endpoint, params)
            if not response:
                continue
            response_json = response.json()
            if not response_json['result']:
                raise ValueError(f"Empty result, fetch_busstop_coordinates")
            try:
                for bus_stop_dict in response_json['result']:
                    complex_id = bus_stop_dict['values'][0]['value']
                    bus_stop_id = bus_stop_dict['values'][1]['value']
                    bus_stop_name = bus_stop_dict['values'][2]['value']
                    latitude = bus_stop_dict['values'][4]['value']
                    longtitude = bus_stop_dict['values'][5]['value']
                    direction = bus_stop_dict['values'][6]['value']

                    key = complex_id + ',' + bus_stop_id
                    busstop_coord[key] = {
                        "Lon,Lat": (float(longtitude), float(latitude)),
                        "stop_name": bus_stop_name
                    }

                break
            except TypeError:
                self.__log(response_json)

        return busstop_coord

    def fetch_busstop_coordinates(self, output_filename: Optional[str] = None):
        busstop_data = self.__fetch_busstop_coordinates_helper()
        output = output_filename if output_filename is not None else \
            f"busstop_coordinates_{datetime.now().strftime('%Y-%m-%d')}.json"

        with open(output, "w", encoding='utf-8') as fp:
            json.dump(busstop_data, fp, ensure_ascii=False)

    def fetch_lines_for_busstop(self, bus_stop_complex_id: str, bus_stop_id: str):
        params = {'id': '88cd555f-6f31-43ca-9de4-66c479ad5942',
                  'busstopId': bus_stop_complex_id,
                  'busstopNr': bus_stop_id,
                 }
        lines_for_stop = []
        while True:
            """Sample response
              {'result': 
                      [
                        {'values': [{'value': '138', 'key': 'linia'}]}, 
                        {'values': [{'value': '143', 'key': 'linia'}]}, 
                        {'values': [{'value': '523', 'key': 'linia'}]}, 
                        {'values': [{'value': '525', 'key': 'linia'}]}, 
                        {'values': [{'value': 'N25', 'key': 'linia'}]}
                      ]
              }
            """
            response = self.__send_request(self.__schedule_endpoint, params)
            if not response:
                continue
            response_json = response.json()

            if not response_json['result']:
                return []
            try:
                for line_dict in response_json['result']:
                    lines_for_stop.append(line_dict['values'][0]['value'])
                return lines_for_stop
            except TypeError:
                self.__log(response_json)

    def fetch_routes(self, output_filename: Optional[str] = None):
        result_dict = defaultdict(lambda: defaultdict(dict))
        while True:
            """ Sample response:
                  {
                    "result": {
                      "1": {
                          "TD-1NAR": 
                            {
                              "1": {"odleglosc": 0, "ulica_id": "1501", "nr_zespolu": "R-01",
                                    "typ": "6", "nr_przystanku": "00"},
                              "2": {...}
                            },
                  },
            """
            response = self.__send_request(self.__routes_end_point, dict())
            if not response:
                continue
            response_json = response.json()
            if not response_json['result']:
                raise ValueError(f"Empty result")
            try:
                for line, routes in response_json['result'].items():
                    for route, info_dict in routes.items():
                        for nr_porzadkowy, info in info_dict.items():
                            result_dict[line][route][int(
                                nr_porzadkowy)] = info["nr_zespolu"]+','+info["nr_przystanku"]
                break
            except TypeError:
                self.__log(response_json)

        output = output_filename if output_filename is not None else \
            f"routes_{datetime.now().strftime('%Y-%m-%d')}.json"

        with open(output, "w", encoding='utf-8') as fp:
            json.dump(result_dict, fp, ensure_ascii=False)

    def __fetch_schedule_for_busstop_line(self, timetable: DefaultDict[str, DefaultDict[str, List]],
                                          bus_stop_complex_id: str, bus_stop_id: str,
                                          line_num: str) -> None:
        params = {'id': 'e923fa0e-d96c-43f9-ae6e-60518c9f3238',
                  'busstopId': bus_stop_complex_id,
                  'busstopNr': bus_stop_id,
                  'line': line_num,
                 }
        while True:
            """Sample response:
              {'result': 
                      [
                        { 'values': 
                                    [
                                      {'value': 'null', 'key': 'symbol_2'}, 
                                      {'value': 'null', 'key': 'symbol_1'},
                                      {'value': '1', 'key': 'brygada'},
                                      {'value': 'Utrata', 'key': 'kierunek'},
                                      {'value': 'TP-UTS', 'key': 'trasa'},
                                      {'value': '05:06:00', 'key': 'czas'}
                                    ]
                        }, 
                        { 'values': [...]},
                      ]
              }
              """
            response = self.__send_request(self.__schedule_endpoint, params)
            if not response:
                continue
            response_json = response.json()
            if not response_json['result']:
                return

            try:
                for bus_dict in response_json['result']:
                    brigade = bus_dict['values'][2]['value']
                    route = bus_dict['values'][4]['value']
                    time = bus_dict['values'][5]['value']
                    time = datetime.now().strftime('%Y-%m-%d') + " " + time
                    timetable[line_num][brigade][','.join((bus_stop_complex_id, bus_stop_id))].append({
                        "Time": time, "Route": route})
                return
            except TypeError:
                self.__log(response_json)

    def __fetch_schedule_for_busstop(self, timetable: DefaultDict[str, DefaultDict[str, List]],
                                     bus_stop_complex_id: str, bus_stop_id: str) -> None:
        all_lines = self.fetch_lines_for_busstop(
            bus_stop_complex_id, bus_stop_id)
        if len(all_lines) >= 10:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.__fetch_schedule_for_busstop_line,
                                           timetable, bus_stop_complex_id, bus_stop_id, line)
                           for line in all_lines]
                for future in as_completed(futures): future.result()
        else:
            for line in all_lines:
                self.__fetch_schedule_for_busstop_line(
                    timetable, bus_stop_complex_id, bus_stop_id, line)

    def read_the_whole_schedule(self, output_filename: Optional[str] = None):
        start = timer()
        timetable = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        busstop_data = self.__fetch_busstop_coordinates_helper()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.__fetch_schedule_for_busstop, timetable, *val.split(','))
                       for val in busstop_data.keys()]

            for future in as_completed(futures):
                future.result()

        output = output_filename if output_filename is not None else \
            f"timetable_{datetime.now().strftime('%Y-%m-%d')}.json"

        with open(output, "w", encoding='utf-8') as fp:
            # encode dict into JSON
            json.dump(timetable, fp, ensure_ascii=False)

        print("Time passed: ", timer() - start, " seconds")


