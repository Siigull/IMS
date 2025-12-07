import osmium
import geopandas
from shapely.geometry import shape, box
import matplotlib.pyplot as plt
import numpy as np

min_lon, min_lat = 16.45, 49.10
max_lon, max_lat = 16.75, 49.30

fp = osmium.FileProcessor('maps_czechia/220101.osm.pbf')\
        .with_locations()\
        .with_filter(osmium.filter.EntityFilter(osmium.osm.WAY))\
        .with_filter(osmium.filter.KeyFilter('highway'))\
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
        # "nodes": [
        #     (n.location.lat, n.location.lon)
        #     for n in obj.nodes
        #     if n.location.valid()
        # ]
    })

print("done 2")

# Create GeoDataFrame
gdf = geopandas.GeoDataFrame(features, geometry="geometry", crs="EPSG:4326")

bbox = box(min_lon, min_lat, max_lon, max_lat)
gdf = gdf[gdf.intersects(bbox)]

side_split = 1000 # Splits whole map into side_splitxside_split boxes/cells

grid = [[False for _ in range(side_split)] for _ in range(side_split)]

lon_step = (max_lon - min_lon) / side_split
lat_step = (max_lat - min_lat) / side_split

for geom in gdf.geometry:
    if geom.is_empty:
        continue
    if geom.geom_type == "MultiLineString":
        lines = geom.geoms
    else:
        lines = [geom]
    for line in lines:
        # Sample points along the line
        num_points = max(10, int(line.length * 20000))  # finer sampling if long
        for p in np.linspace(0, 1, num_points):
            pt = line.interpolate(p, normalized=True)
            lon, lat = pt.x, pt.y
            
            # X Index: No change needed (Left -> Right matches Low -> High Longitude)
            x_idx = int((lon - min_lon) / lon_step)
            
            # Y Index: INVERT this.
            # Currently: (lat - min_lat) -> 0 at bottom.
            # Fix: (max_lat - lat) -> 0 at top.
            y_idx = int((max_lat - lat) / lat_step)

            if 0 <= x_idx < side_split and 0 <= y_idx < side_split:
                grid[y_idx][x_idx] = True

with open("road_grid.txt", "w") as f:
    for y in range(side_split):
        for x in range(side_split):
            f.write(str(int(grid[y][x])))
            f.write(" ")
        f.write('\n')

# Plot
plt.figure(figsize=(8, 8))
plt.imshow(grid, cmap='viridis', interpolation='nearest', origin='upper')

# Optional: make 0 (empty) cells white
from matplotlib.colors import ListedColormap
cmap = ListedColormap(['white', 'black'])  # white=empty, blue=non-empty
plt.imshow(grid, cmap=cmap, interpolation='nearest', origin='upper')

# plt.axis('off')
# plt.savefig("road_grid_14.png", dpi=600)
# plt.show()

# ax = gdf.plot(figsize=(10, 10), linewidth=1, color="blue")
# plt.title("Roads in Brno")
# plt.savefig("brnoimage.png", dpi=600)
# plt.show()
