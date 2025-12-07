import osmium
import geopandas as gpd
from shapely.geometry import box
import shapely.wkb as wkb
import matplotlib.pyplot as plt
from rasterio import features, transform
import numpy as np

# --- 1. Define ROI in Lat/Lon ---
min_lon, min_lat = 16.45, 49.10
max_lon, max_lat = 16.75, 49.30

# --- 2. Handler (Standard) ---
class ProtectedAreaHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.features = []
        self.wkbfab = osmium.geom.WKBFactory()

    def area(self, a):
        self._process(a, False)
    def way(self, w):
        self._process(w, True)

    def _process(self, o, is_way):
        tags = o.tags
        if (tags.get("landuse") == "forest"):
            try:
                func = self.wkbfab.create_linestring if is_way else self.wkbfab.create_multipolygon
                geom = wkb.loads(func(o), hex=True)
                self.features.append({"geometry": geom})
            except: pass

print("Extracting...")
handler = ProtectedAreaHandler()
handler.apply_file("maps_czechia/220101.osm.pbf", locations=True)

if handler.features:
    # Load as Lat/Lon
    gdf = gpd.GeoDataFrame(handler.features, geometry="geometry", crs="EPSG:4326")
    
    # 1. Clip to the bounding box first (in Lat/Lon)
    bbox = box(min_lon, min_lat, max_lon, max_lat)
    gdf = gdf[gdf.geometry.is_valid].clip(bbox)

    # --- THE CRITICAL FIX: Reproject to Meters ---
    # EPSG:3857 is what Google Maps/OSM use. This fixes the "shape" of the polygons.
    gdf = gdf.to_crs("EPSG:3857")
    
    # We must also re-calculate the bounds in the NEW coordinate system
    # to ensure our transform matches the 1000x1000 grid exactly
    gdf_bounds = gpd.GeoSeries([bbox], crs="EPSG:4326").to_crs("EPSG:3857")
    minx, miny, maxx, maxy = gdf_bounds.total_bounds

    # --- Rasterize into 1000x1000 ---
    width, height = 1000, 1000
    
    # Create transform based on the METRIC bounds
    out_transform = transform.from_bounds(minx, miny, maxx, maxy, width, height)

    raster = features.rasterize(
        shapes=((g, 1) for g in gdf.geometry),
        out_shape=(height, width),
        transform=out_transform,
        fill=0,
        dtype=np.uint8,
        all_touched=True
    )

    np.savetxt("forest_grid.txt", raster, fmt="%d")
    print(f"✅ Saved 1000x1000 grid. Shape alignment corrected.")

    # # Check the output
    # plt.imshow(raster, cmap='gray', origin='upper') # origin='upper' puts (0,0) at top-left
    # plt.title("Forest Areas (Projected & Squashed to 1000x1000)")
    # plt.show()
