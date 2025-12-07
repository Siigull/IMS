import osmium
import geopandas
from shapely.geometry import shape, box
import matplotlib.pyplot as plt

min_lon, min_lat = 16.45, 49.10
max_lon, max_lat = 16.75, 49.30

fp = osmium.FileProcessor('maps_czechia/220101.osm.pbf')\
        .with_locations()\
        .with_filter(osmium.filter.KeyFilter('building'))\
        .with_filter(osmium.filter.EntityFilter(osmium.osm.WAY))\
        .with_filter(osmium.filter.GeoInterfaceFilter())

print("done")

features = []
for obj in fp:
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

gdf = geopandas.GeoDataFrame(features, geometry="geometry", crs="EPSG:4326")

bbox = box(min_lon, min_lat, max_lon, max_lat)
gdf = gdf[gdf.intersects(bbox)]

ax = gdf.plot(figsize=(10, 10), linewidth=0.5, color="blue")
plt.title("Building Areas in Brno")
plt.savefig("brnoimage.png", dpi=600)
plt.show()
