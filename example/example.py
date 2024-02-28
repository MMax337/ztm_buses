import os
import matplotlib.pyplot as plt

from ztm_buses.BusStatistician import BusStatistician
from ztm_buses.Visualizer import Visualizer



vis = Visualizer()
bus_coordinates = ['bus_coordinates_2024-02-26 12-11-33_duration_3600s.json',
                   'bus_coordinates_2024-02-26 16-59-10_duration_3600s.json']

for i in range(len(bus_coordinates)):

    statistician = BusStatistician(bus_coordinates[i], 'timetable_2024-02-26.json',
                                   'routes_2024-02-26.json', 'busstop_coordinates_2024-02-26.json')

    speed_stats = statistician.get_speed_statistics()
    punctuality_stats = statistician.get_punctuality_statistics()

    speed_stats.to_csv(os.path.join('results', f'speed_stats{i+1}.csv'))
    punctuality_stats.to_csv(os.path.join('results', f'punctuality_stats{i+1}.csv'))

    speed_stats = speed_stats[speed_stats['speed'] < 90]
    speed_stats = speed_stats[speed_stats['speed'] > 40]

    punctuality_stats = punctuality_stats[punctuality_stats['Delay [min]'].apply(
        abs) < 30]

    vis.heat_map_speeds(speed_stats, os.path.join(
        'results', f"heat_speed_map{i+1}.html"))
    vis.scatter_map_speeds(speed_stats, os.path.join(
        'results', f"scatter_speed_map{i+1}.html"))
    vis.map_punctuality(punctuality_stats, os.path.join(
        'results', f"punctuality_map{i+1}.html"))

