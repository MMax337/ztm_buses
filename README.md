# ZTM Buses Package

## Visualizations
<table>
  <tr>
    <td align="center">
      <h3>Heatmap</h3>
      <img src="https://github.com/MMax337/ztm_buses/blob/main/readme_images/heatmap.png" width="500" />
    </td>
    <td align="center">
      <h3>Punctuality</h3>
      <img src="https://github.com/MMax337/ztm_buses/blob/main/readme_images/punctuality.png" width="500" />
    </td>
  </tr>
  <tr>
    <td align="center">
      <h3>Scatterplot</h3>
      <img src="https://github.com/MMax337/ztm_buses/blob/main/readme_images/scatterplot.png" width="500" />
    </td>
    <td align="center">
      <h3>Top Delays</h3>
      <img src="https://github.com/MMax337/ztm_buses/blob/main/readme_images/top_delays.png" width="500" />
    </td>
  </tr>
</table>
## Current Features

The package consists of three main functionalities:

1. **ZTMFetcher**
2. **BusStatistician**
3. **Visualizer**

### ZTMFetcher

The `ZTMFetcher` module allows acquiring information from the Warsaw API.

- Import the module:

    ```python
    from ztm_buses import ZTMFetcher
    ```

- Initialize with multiple API keys (may be beneficial when handling a substantial number of requests.):

    ```python
    fetcher = ZTMFetcher(['your_apikey1', 'your_apikey2'])
    ```

    API keys can be obtained on [https://api.um.warszawa.pl/](https://api.um.warszawa.pl/).

- **Fetch Bus Location:**

    ```python
    location = fetcher.fetch_bus_location()
    ```

- **Fetch Bus Location Period:**

    ```python
    hour_location = fetcher.fetch_bus_location_period(period, "filename_to_save_json.json")
    ```

- **Fetch Bus Stop Coordinates and Routes:**

    ```python
    fetcher.fetch_busstop_coordinates("filename_to_save_json.json")
    fetcher.fetch_routes("filename_to_save_json.json")
    ```

    For all methods, if a filename was not given, the data will be automatically saved with the date to avoid overwriting issues.

- **Fetch Lines for Bus Stop:**

    ```python
    list_of_lines = fetcher.fetch_lines_for_busstop(bus_stop_complex_id, bus_stop_id)
    ```

- **Fetch Whole Timetable:**

    ```python
    fetcher.read_the_whole_schedule("filename_to_save_json.json")
    ```

    Beware that fetching the whole timetable requires sending about 28,000 requests and may take from 20 to 50 minutes depending on the server load.

### BusStatistician

The `BusStatistician` module allows obtaining information about the speed and punctuality of buses.

- Import the module:

    ```python
    from ztm_buses import BusStatistician
    ```

- Initialize:

    ```python
    statistician = BusStatistician(bus_coordinates_file, timetable_file, routes_file, bus_stops_file)
    ```

- **Get Speed Statistics:**

    ```python
    speed_data_frame = statistician.get_speed_statistics()
    ```

- **Get Punctuality Statistics:**

    ```python
    punctuality_data_frame = statistician.get_punctuality_statistics()
    ```

    The `speed_data_frame` contains the columns: 'speed', 'lon', 'lat', 'vehicle_number', 'line_number'. The `punctuality_data_frame` contains 'Bus_num', 'Line', 'Busstop_id', 'Busstop_name', 'Lon', 'Lat', 'Arrived', 'Expected', 'Delay [min]'.

Due to the complicated structure of bus routes and imperfections of the data, the punctuality data is prone to some larger errors.

### Visualizer

The `Visualizer` module takes the dataframes from the `BusStatistician` and plots them on the Warsaw map.

- Import the module:

    ```python
    from ztm_buses import Visualizer
    ```

- Initialize:

    ```python
    vis = Visualizer()
    ```

- **Heat Map of Speeds:**

    ```python
    vis.heat_map_speeds(speed_data_frame, html_file_to_save)
    ```

- **Scatter Map of Speeds:**

    ```python
    vis.scatter_map_speeds(speed_data_frame, html_file_to_save)
    ```
  For speed maps output html file is optional and if not given the result
  will not be saved
- **Map of Punctuality:**

    ```python
    vis.map_punctuality(punctuality_data_frame, html_file_to_save)
    ```

    For punctuality map the html file is required parameter

It is worth noting that before visualizing the data, it has to be cleaned up as the API sometimes responds with nonrealistic data (time traveling, hypersonic buses).

## Installation

```bash
pip install ztm_buses
