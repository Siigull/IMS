import glob
import rasterio
from rasterio.merge import merge
from rasterio.windows import from_bounds
from pyproj import Transformer
import numpy as np

# bounding box
min_lon, min_lat = 16.45, 49.10 
max_lon, max_lat = 16.75, 49.30

transformer = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True)

min_lon, min_lat = transformer.transform(min_lon, min_lat)
max_lon, max_lat = transformer.transform(max_lon, max_lat)

print(min_lon, min_lat)
print(max_lon, max_lat)

# directory with tif tiles
tif_dir = "eudem"

# compute integer degrees for the tiles you need
lats = range((int(min_lat / 1000000)) * 10, (int(max_lat / 1000000)) * 10 + 10, 10)
lons = range((int(min_lon / 1000000)) * 10, (int(max_lon / 1000000)) * 10 + 10, 10)

# find all relevant files
tif_files = []
for lat in lats:
    for lon in lons:
        print("a")
        f_name = f"{tif_dir}/N{lat}E{lon}.tif"
        print(f_name)
        matches = glob.glob(f_name)
        tif_files.extend(matches)

print("Tiles covering bbox:", tif_files)

# open all relevant rasters
src_files_to_mosaic = [rasterio.open(tif_files[0], masked=False, nodata=0)]

# for file in src_files_to_mosaic:
#     mask = file.dataset_mask()
#     print("mask unique values:", np.unique(mask))
#     print("CRS:", file.crs)
#     print("Bounds:", file.bounds)
#     print("Res:", file.res)
#     print("Nodata:", file.nodata)

print("here")

# merge them into one raster
mosaic, out_transform = merge(src_files_to_mosaic, nodata=0, masked=False, dtype="float64")
print("Mosaic shape:", mosaic.shape)
print("Mosaic min/max:", mosaic.min(), mosaic.max())

print(mosaic)

# get metadata from one of them
out_meta = src_files_to_mosaic[0].meta.copy()
out_meta.update({
    "driver": "GTiff",
    "height": mosaic.shape[1],
    "width": mosaic.shape[2],
    "transform": out_transform,
})

print(out_transform)

with rasterio.open("whole.tif", 'w', **out_meta) as dest:
    dest.write(mosaic)

window = from_bounds(min_lon, min_lat, max_lon, max_lat, transform=out_transform)

# Crop array manually
row_start, row_stop = map(int, [window.row_off, window.row_off + window.height])
col_start, col_stop = map(int, [window.col_off, window.col_off + window.width])
out_image = mosaic[:, row_start:row_stop, col_start:col_stop]

# Update metadata
out_meta.update({
    "height": out_image.shape[1],
    "width": out_image.shape[2],
    "transform": rasterio.windows.transform(window, out_transform)
})

# Write clipped file
with rasterio.open("brno.tif", "w", **out_meta) as dest:
    dest.write(out_image)

# Cleanup
for src in src_files_to_mosaic:
    src.close()

print("Saved 'whole.tif' and 'brno.tif'")
