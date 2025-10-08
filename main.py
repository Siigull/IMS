import osmium
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString
import matplotlib.pyplot as plt
from pathlib import Path

class RoadHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.data = []

    def way(self, w):
        if 'highway' in w.tags and len(w.nodes) > 1:
            coords = [(n.lon, n.lat) for n in w.nodes]
            self.data.append({
                'highway': w.tags.get('highway'),
                'geometry': LineString(coords)
            })

def load_pbf_to_gdf(pbf_file):
    handler = RoadHandler()
    handler.apply_file(pbf_file, locations=True, idx='flex_mem')
    gdf = gpd.GeoDataFrame(handler.data, crs="EPSG:4326")
    return gdf

# Folder containing your PBFs
pbf_folder = Path("maps_czechia")
pbf_files = sorted(pbf_folder.glob("*.osm.pbf"))

# Load each file
gdfs = []
for f in pbf_files:
    print(f"Processing {f.name} ...")
    gdf = load_pbf_to_gdf(f)
    gdf['source_file'] = f.name
    gdfs.append(gdf)

# Combine for visualization
combined = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs="EPSG:4326")

# Plot (for example, color by file/time)
plt.figure(figsize=(10, 10))
combined.plot(column="source_file", legend=True, linewidth=0.5)
plt.title("Historical OSM Road Network Snapshots")
plt.show()
