from __future__ import annotations
from math import radians, degrees, sin, cos, sqrt, atan2


class Coordinates:
    earth_radius = 6_364_814  # in meters at Warsaw latitude

    def __init__(self, longtitude: float, latitude: float) -> Coordinates:
        self.__theta = radians(longtitude)
        self.__phi = radians(latitude)

    # The errors are too big
    # def distance(self, other : Coordinates) -> float:
    #   sqr = 2 * (1 -
    #               \ sin(self.__theta)* sin(other.__theta) * cos(self.__phi - other.__phi)
    #                \ - cos(self.__theta)*cos(other.__theta) )
    #   if (sqr < 0):
    #     sqr = 0

    #   return Coordinates.earth_radius * sqrt(sqr)

    def distance(self, other: Coordinates):
        dLat = self.__phi - other.__phi
        dLon = self.__theta - other.__theta
        a = sin(dLat/2)**2 + cos(self.__phi)*cos(other.__phi)*sin(dLon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return Coordinates.earth_radius * c

    def __sub__(self, other: Coordinates) -> Coordinates:
        return self.distance(other)

    @property
    def lon(self) -> float:
        return degrees(self.__theta)

    @property
    def lat(self) -> float:
        return degrees(self.__phi)

    def __str__(self) -> str:
        return f"Lon: {degrees(self.__theta)},  Lat: {degrees(self.__phi)}"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: Coordinates) -> bool:
        return self.__theta == other.__theta and self.__phi == other.__phi
