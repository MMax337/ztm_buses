from __future__ import annotations
from typing import Optional
from collections import defaultdict
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import plotly_express as px
import webbrowser

class Visualizer:
    def __init__(self) -> Visualizer:
        self.__warsaw_lon = 21.017532
        self.__warsaw_lat = 52.237049

    def heat_map_speeds(self, stats: pd.DataFrame, html_out: Optional[str] = None):
        fig = px.density_mapbox(stats, lat='lat', lon='lon', z='speed', radius=12,
                                center={'lat': self.__warsaw_lat, 'lon': self.__warsaw_lon}, 
                                zoom=12, mapbox_style='open-street-map', height=900)
        fig.update_layout(margin=dict(b=0, t=0, l=0, r=0))
        if html_out is not None:
            fig.write_html(html_out)
        fig.show()

    def scatter_map_speeds(self, stats: pd.DataFrame, html_out: Optional[str] = None):
        fig = px.scatter_mapbox(stats, lat='lat', lon='lon', color='speed',
                                color_continuous_scale=[
                                    [0.0, "green"],
                                    [0.3125, "green"],
                                    [0.3125111111, "yellow"],
                                    [0.53125, "yellow"],
                                    [0.5312511111, "orange"],
                                    [0.75, "orange"],
                                    [0.751111111, "red"],
                                    [1, "red"]],
                                opacity=0.5,
                                mapbox_style='open-street-map'
                                )
        fig.update_layout(margin=dict(b=0, t=0, l=0, r=0))
        if html_out is not None:
            fig.write_html(html_out)
        fig.show()

    def map_punctuality(self, time_stats: pd.DataFrame, html_out: str):
        m = folium.Map(location=(self.__warsaw_lat,
                       self.__warsaw_lon), zoom_start=14)

        data_dict = defaultdict(list)

        for busstop_name, line, lon, lat, arrived, expected, delay \
            in zip(time_stats['Busstop_name'], time_stats['Line'],
                   time_stats['Lon'], time_stats['Lat'],
                   time_stats['Arrived'], time_stats['Expected'],
                   time_stats['Delay [min]']):

            data_dict[busstop_name].append({'line': line, 'arrived': str(arrived),
                                            'lon': lon, 'lat': lat,
                                            'expected': str(expected),
                                            'delay': round(delay, 2)})

        marker_cluster = MarkerCluster().add_to(m)
        for busstop_name, val in data_dict.items():
            accumulator = str()
            for info in val:
                date, arrived_hour = info['arrived'].split(' ')
                excepted_hour = info['expected'].split(' ')[1]
                lon, lat = info['lon'], info['lat']

                accumulator += f"""<li>Bus line: {info['line']},
                           Arrival: {arrived_hour}, Expected: {excepted_hour},
                           Delay: {info['delay']} min</li>"""
            if accumulator == "":
                accumulator = "<li><\li>"
            popup_content = f"""
        <div style="width: 500px;">
        <h4> {busstop_name}, {date}</h4>
        <ul style="font-size: 14px;"> {accumulator}</ul>
        </div>
        """

            folium.Marker(location=[lat, lon], popup=popup_content,
                          icon=folium.Icon()).add_to(marker_cluster)
        
        
        m.save(html_out)
        webbrowser.open_new_tab(html_out)
    

