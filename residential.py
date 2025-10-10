import osmium
import geopandas
from shapely.geometry import shape, box
import matplotlib.pyplot as plt
import numpy as np

min_lon, min_lat = 16.50, 49.14
max_lon, max_lat = 16.70, 49.30

fp = osmium.FileProcessor('maps_czechia/250901.osm.pbf')\
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
        "building": obj.tags.get("building"),
        "geometry": geom,
    })

print("done 2")

gdf = geopandas.GeoDataFrame(features, geometry="geometry", crs="EPSG:4326")

def classify_building(btype):
    if btype in ['house', 'residential', 'apartments', 'detached', 'terrace', 'dwelling_house', 
                 'residences', 'residence', 'home', 'bungalow', 'guest_house', 'villa', 'flat', 
                 'shelter', 'boathouse', 'allotment_house', 'dormitory']:
        return "residential"
    elif btype in ['commercial', 'retail', 'office', 'supermarket', 'kiosk', 'supermarket',
                   'restaurant', 'mall', 'sports_centre', 'bakehouse', 'stadium', 'museum',
                   'château', 'pub', 'toilets', 'wine_cellar', 'riding_hall', 'sports_hall',
                   'parking']:
        return "commercial"
    elif btype in ['industrial', 'warehouse', 'factory', 'workshop', 'production_hall', 
                   'high_bay_warehouse', 'data_center', 'silo', 'garages', 'storage_tank',
                   'station', 'cowshed', 'electricity', 'containers', 'manufacture', 
                   'wine_press_house', 'hangar', 'hospital', 'farm', 'civic', 'chicken_coop', 'barn']:
        return "industrial"
    else:
        return "other"

gdf["category"] = gdf["building"].apply(classify_building)

bbox = box(min_lon, min_lat, max_lon, max_lat)
gdf = gdf[gdf.intersects(bbox)]

fig, ax = plt.subplots(figsize=(10, 10))
gdf[gdf["category"] == "residential"].plot(ax=ax, color="blue", label="Residential", linewidth=0.5)
gdf[gdf["category"] == "commercial"].plot(ax=ax, color="green", label="Commercial", linewidth=0.5)
gdf[gdf["category"] == "industrial"].plot(ax=ax, color="red", label="Industrial", linewidth=0.5)
gdf[gdf["category"] == "other"].plot(ax=ax, color="gray", label="Other", linewidth=0.5)

side_split = 1000 # Splits whole map into side_splitxside_split boxes/cells

grid = [[[] for _ in range(side_split)] for _ in range(side_split)]

for obj, row in gdf.iterrows():

    centroid = row.geometry.centroid
    lat, lon = centroid.y, centroid.x

    x_idx = int((lon - min_lon) / side_split)
    y_idx = int((lat - min_lat) / side_split)

    if 0 <= x_idx < side_split and 0 <= y_idx < side_split:
        grid[(obj.lat - min_lat) / side_split][(obj.lon - min_lon) / side_split].append(obj)

# for y in range(0, side_split):
#     for x in range(0, side_split):
        
# ax = gdf.plot(figsize=(10, 10), linewidth=1, color="blue")
plt.title("Buildings by types in Brno")
plt.savefig("brno_building_types.png", dpi=600)
plt.show()
