import unittest
from unittest.mock import MagicMock, patch, mock_open
from datetime import datetime
from collections import defaultdict

from ztm_buses.ZTMFetcher import ZTMFetcher


class ZTMFetcherTest(unittest.TestCase):

    @patch('ztm_buses.ZTMFetcher.requests.get')
    def test_send_request(self, mock_get):
        endpoint = "https://some_endpoint/"
        params = {"first": "whatever1", "second": "whatever2"}
        return_val = {"result": "response"}
        mock_session = MagicMock()
        mock_get.return_value = return_val
        mock_session.get = mock_get

        ZTM = ZTMFetcher(["random_api_key1"])
        ZTM._ZTMFetcher__session = mock_session

        response = ZTM._ZTMFetcher__send_request(endpoint, params)
        self.assertEqual(response, return_val)
        mock_get.assert_called_once_with(endpoint, params=params)

    @patch('ztm_buses.ZTMFetcher.requests.get')
    def setUp(self, mock_get):
        self.ZTM = ZTMFetcher(["random_api_key1", "random_api_key2"])
        self.mock_get = mock_get
        mock_session = MagicMock()
        mock_session.get = self.mock_get
        self.ZTM._ZTMFetcher__session = mock_session

    def test_fetch_bus_location(self):
        mock_response = MagicMock(status_code=200)
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        mock_response.json.return_value = {
            "result": [
                {"Lines": "219", "Lon": 21.1128748, "VehicleNumber": "1000",
                 "Time": time, "Lat": 52.213404, "Brigade": "3"
                },
                {"Lines": "Mock_line", "Lon": "Mock_lon", "VehicleNumber": "Mock",
                 "Time": "Mock_time", "Lat": "Mock_lat", "Brigade": "Mock_brig"
                }
            ]
        }

        self.mock_get.return_value = mock_response
        correct_dict = {
            "1000": {"Lines": "219", "Lon": 21.1128748, "Lat": 52.213404,
                     "Time": time, "Brigade": "3"},
        }
        self.assertEqual(self.ZTM.fetch_bus_location(), correct_dict)

    def test_fetch_bus_location(self):

        mock_response = MagicMock(status_code=200)
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        mock_response.json.return_value = {
            "result": [
                {"Lines": "219", "Lon": 21.1128748, "VehicleNumber": "1000",
                 "Time": time, "Lat": 52.213404, "Brigade": "3"
                },
                {"Lines": "Mock_line", "Lon": "Mock_lon", "VehicleNumber": "Mock",
                 "Time": "Mock_time", "Lat": "Mock_lat", "Brigade": "Mock_brig"
                }
            ]
        }

        self.mock_get.return_value = mock_response
        correct_dict = {
            "1000": {"Lines": "219", "Lon": 21.1128748, "Lat": 52.213404,
                     "Time": time, "Brigade": "3"},
        }
        self.assertEqual(self.ZTM.fetch_bus_location(), correct_dict)

    @patch('ztm_buses.ZTMFetcher.json')
    @patch('ztm_buses.ZTMFetcher.time.sleep', return_value=None)
    @patch('ztm_buses.ZTMFetcher.ZTMFetcher.fetch_bus_location')
    def test_fetch_bus_location_period(self, mock_response, patched_time_sleep, json_mock):
        return_val = {"whatever1": "whatever2"}
        mock_response.return_value = return_val

        filename = "filename"
        open_mock = mock_open()
        time = 25
        with patch('ztm_buses.ZTMFetcher.open', open_mock, create=True):
            self.ZTM.fetch_bus_location_period(time, filename)

        self.assertEqual(time//10, patched_time_sleep.call_count)

        open_mock.assert_called_once_with(filename, 'w', encoding='utf-8')

        correct_output = {0: return_val, 1: return_val}

        json_mock.dump.assert_called_once_with(
            correct_output, open_mock(), ensure_ascii=False)

    def test__fetch_busstop_coordinates_helper(self):
        mock_response = MagicMock(status_code=200)

        mock_response.json.return_value = {
            "result": [
                {
                    "values": [
                        {"value": "1001", "key": "zespol"},
                        {"value": "01", "key": "slupek"},
                        {"value": "Kijowska", "key": "nazwa_zespolu"},
                        {"value": "2201", "key": "id_ulicy"},
                        {"value": 52.248455, "key": "szer_geo"},
                        {"value": 21.044827, "key": "dlug_geo"},
                        {"value": "al.Zieleniecka", "key": "kierunek"},
                        {"value": "2023-09-23 00:00:00.0",
                         "key": "obowiazuje_od"}
                    ]
                }
            ]
        }
        self.mock_get.return_value = mock_response
        correct_output = {"1001,01": {
            "Lon,Lat": (21.044827, 52.248455),
            "stop_name": "Kijowska"
        }
        }

        output = self.ZTM._ZTMFetcher__fetch_busstop_coordinates_helper()
        self.assertEqual(output, correct_output)

    def test_fetch_lines_for_busstop(self):
        mock_response = MagicMock(status_code=200)
        response = {'result':
                    [
                        {'values': [{'value': '138', 'key': 'linia'}]},
                        {'values': [{'value': '143', 'key': 'linia'}]},
                        {'values': [{'value': '523', 'key': 'linia'}]},
                        {'values': [{'value': '525', 'key': 'linia'}]},
                        {'values': [{'value': 'N25', 'key': 'linia'}]}
                    ]
                    }
        mock_response.json.return_value = response
        self.mock_get.return_value = mock_response
        output = self.ZTM.fetch_lines_for_busstop("1000", "01")
        correct_output = ["138", "143", "523", "525", "N25"]
        self.assertEqual(correct_output, output)

    @patch('ztm_buses.ZTMFetcher.json')
    def test_fetch_routes(self, json_mock):
        mock_response = MagicMock(status_code=200)
        response = {"result": {"128": {
            "TD-3BAN":
            {"1": {"ulica_id": "2513", "nr_zespolu": "R-03",
                   "nr_przystanku": "00", "typ": "6", "odleglosc": 0},
             "2": {"ulica_id": "1205", "nr_zespolu": "3240",
                   "nr_przystanku": "04", "typ": "5", "odleglosc": 245}
             }
        }
        }}
        mock_response.json.return_value = response
        self.mock_get.return_value = mock_response

        filename = "dummy.txt"
        open_mock = mock_open()
        with patch('ztm_buses.ZTMFetcher.open', open_mock, create=True):
            self.ZTM.fetch_routes(filename)

        correct_output = defaultdict(lambda: defaultdict(dict))
        correct_output["128"]["TD-3BAN"] = {1: "R-03,00", 2: "3240,04"}
        open_mock.assert_called_once_with(filename, 'w', encoding='utf-8')
        # it doesn't work because json.dump was called with defaultdict and it
        # the function calling it
        # json_mock.dump.assert_called_once_with(correct_output, open_mock() ,ensure_ascii=False)
        out_dict = dict(json_mock.dump.call_args[0][0])

        self.assertEqual(out_dict, dict(correct_output))


if __name__ == '__main__':
    unittest.main()
