import json
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class ZoneManager:

    def __init__(self, layout_file):

        with open(layout_file) as f:
            self.layout = json.load(f)

        self.store_id = self.layout["store_id"]

        self.zones = []

        for z in self.layout["zones"]:

            self.zones.append({
                "zone_id": z["zone_id"],
                "sku_zone": z["sku_zone"],
                "polygon": Polygon(z["polygon"])
            })

    def get_zone(self, x, y):

        point = Point(x, y)

        for zone in self.zones:

            if zone["polygon"].contains(point):
                return zone

        return None