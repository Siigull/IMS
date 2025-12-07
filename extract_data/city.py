import osmium
import geopandas
from shapely.geometry import shape, box
import matplotlib.pyplot as plt

class PrintHandler(osmium.SimpleHandler):
    def node(self, n):
        print(n)

    def way(self, w):
        print(w)

    def relation(self, r):
        print(r)

    def area(self, a):
        print(a)

    def changeset(self, c):
        print(c)

class BoxFilter:
    # def way(self, n):
    #     print(n.lat)
    #     return n.lat > 16.50 and n.lon > 49.10 and\
    #             n.lat < 16.70 and n.lon < 49.30

    def node(self, n):
        return n.lat > 16.50 and n.lon > 49.10 and\
                n.lat < 16.70 and n.lon < 49.30

min_lon, min_lat = 16.45, 49.10
max_lon, max_lat = 16.75, 49.30

        # .with_locations()\
        # .with_filter(osmium.filter.EntityFilter(osmium.osm.WAY))\
        # .with_filter(osmium.filter.KeyFilter('building'))\
        # .with_filter(osmium.filter.GeoInterfaceFilter())

fp = osmium.FileProcessor('maps_czechia/220101.osm.pbf')\
        .with_locations()\
        .with_filter(osmium.filter.KeyFilter('building'))\
        .with_filter(osmium.filter.EntityFilter(osmium.osm.WAY))\
        .with_filter(osmium.filter.GeoInterfaceFilter())

# my_handler = PrintHandler()

# fp.apply(my_handler)

print("done")

features = []
for obj in fp:

    # Each object now implements __geo_interface__
    gi = getattr(obj, "__geo_interface__", None)
    if not gi:
        continue 

    geom = shape(gi["geometry"])
    features.append({
        "id": obj.id,
        "highway": obj.tags.get("highway"),
        "geometry": geom,
    })

print("done 2")

# Create GeoDataFrame
gdf = geopandas.GeoDataFrame(features, geometry="geometry", crs="EPSG:4326")

bbox = box(min_lon, min_lat, max_lon, max_lat)
gdf = gdf[gdf.intersects(bbox)]

ax = gdf.plot(figsize=(10, 10), linewidth=1, color="blue")
plt.title("Highways in Brno")
plt.savefig("brnoimage.png", dpi=600)
plt.show()
