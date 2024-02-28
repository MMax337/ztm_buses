import json


class RoutesManager:
    def __init__(self, filename: str):
        with open(filename, 'r', encoding='utf8') as file:
            self.__routes = json.load(file)

    def get_route(self, line: str, route_name: str):
        return self.__routes[line][route_name]
