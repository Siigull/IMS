import osmium
import geopandas
from shapely.geometry import shape, box
import matplotlib.pyplot as plt
import numpy as np

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
        "building": obj.tags.get("building"),
        "geometry": geom,
        "nodes": [
            (n.location.lat, n.location.lon)
            for n in obj.nodes
            if n.location.valid()
        ]
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

# fig, ax = plt.subplots(figsize=(10, 10))
# gdf[gdf["category"] == "residential"].plot(ax=ax, color="blue", label="Residential", linewidth=0.5)
# gdf[gdf["category"] == "commercial"].plot(ax=ax, color="green", label="Commercial", linewidth=0.5)
# gdf[gdf["category"] == "industrial"].plot(ax=ax, color="red", label="Industrial", linewidth=0.5)
# gdf[gdf["category"] == "other"].plot(ax=ax, color="gray", label="Other", linewidth=0.5)

side_split = 1000 # Splits whole map into side_splitxside_split boxes/cells

# Initialize grid (Rows = Y, Cols = X)
grid = [[False for _ in range(side_split)] for _ in range(side_split)]

for obj, row in gdf.iterrows():
    for lat, lon in row["nodes"]:
        
        # 1. Normalize to 0.0 - 1.0 range
        norm_lat = (lat - min_lat) / (max_lat - min_lat)
        norm_lon = (lon - min_lon) / (max_lon - min_lon)

        # 2. Calculate Indices
        # X is straightforward (Left to Right)
        x_idx = int(norm_lon * side_split)
        
        # Y needs to be INVERTED because array index 0 is the TOP, 
        # but max_lat (1.0) is the North (TOP).
        y_idx = int((1.0 - norm_lat) * side_split)

        # 3. Boundary Checks and Assignment
        # We check 0 <= index < side_split to handle edge cases 
        # (like points exactly on the max_lon/lat border)
        if 0 <= x_idx < side_split and 0 <= y_idx < side_split:
            # Access as grid[ROW][COL] -> grid[Y][X]
            grid[y_idx][x_idx] = True

# Writing the file remains the same, 
# assuming you want the text file to look like the map visually.
with open("building_grid.txt", "w") as f:
    for y in range(side_split):
        for x in range(side_split):
            f.write(str(int(grid[y][x])))
            f.write(" ")
        f.write('\n')


# # Create a mask of non-empty cells
# mask = np.vectorize(lambda x: len(x) > 0)(grid)

# # Convert boolean mask to numeric (1 for colored, 0 for blank)
# data = mask.astype(int)

# # Plot
# plt.figure(figsize=(8, 8))
# plt.imshow(data, cmap='viridis', interpolation='nearest', origin='upper')

# # Optional: make 0 (empty) cells white
# from matplotlib.colors import ListedColormap
# cmap = ListedColormap(['white', 'blue'])  # white=empty, blue=non-empty
# plt.imshow(data, cmap=cmap, interpolation='nearest', origin='upper')

# plt.axis('off')
# plt.savefig("building_grid_14.png", dpi=600)
# plt.show()

# # ax = gdf.plot(figsize=(10, 10), linewidth=1, color="blue")
# plt.title("Buildings by types in Brno")
# plt.savefig("brno_building_types.png", dpi=600)
# plt.show()
