import numpy as np
import rasterio
from rasterio.enums import Resampling
import matplotlib.pyplot as plt

tif_path = "brno.tif"

# --- Step 1: Read the elevation raster ---
with rasterio.open(tif_path) as src:
    print("Original raster size:", src.height, "x", src.width)

    elevation = src.read(1, masked=True)
    res_x, res_y = src.transform.a, -src.transform.e

# Convert masked to nan
elevation = elevation.filled(np.nan)

# --- Step 2: Compute slope ---
dz_dx = (np.roll(elevation, -1, axis=1) - np.roll(elevation, 1, axis=1)) / (2 * res_x)
dz_dy = (np.roll(elevation, -1, axis=0) - np.roll(elevation, 1, axis=0)) / (2 * res_y)
slope = np.degrees(np.arctan(np.sqrt(dz_dx**2 + dz_dy**2)))
slope = np.nan_to_num(slope, nan=0.0)

print("Original slope shape:", slope.shape)

# --- Step 3: Resample to 1000x1000 using bilinear interpolation ---
target_shape = (1000, 1000)
target_height, target_width = target_shape

# Compute scale factors
scale_y = slope.shape[0] / target_height
scale_x = slope.shape[1] / target_width

# Use rasterio's built-in resampling
slope_resampled = np.empty(target_shape, dtype=np.float32)

with rasterio.MemoryFile() as memfile:
    # Create an in-memory raster with slope data
    profile = {
        "driver": "GTiff",
        "height": slope.shape[0],
        "width": slope.shape[1],
        "count": 1,
        "dtype": "float32"
    }

    with memfile.open(**profile) as dataset:
        dataset.write(slope.astype(np.float32), 1)
        # When `indexes` is an int, rasterio.read returns a 2D array (rows, cols).
        # Passing out_shape for a single band should be (rows, cols) in that case.
        slope_resampled = dataset.read(
            1,
            out_shape=(target_height, target_width),
            resampling=Resampling.bilinear
        ).astype(np.float32)

print("Resampled slope shape:", slope_resampled.shape)

# --- Step 4: Save to text & visualize ---
np.savetxt("slope_grid.txt", slope_resampled, fmt="%.4f")

# plt.figure(figsize=(8, 8))
# plt.imshow(slope_resampled, cmap='gray', vmin=np.nanmin(slope_resampled), vmax=np.nanmax(slope_resampled))
# plt.title("Slope (degrees) - Resampled to 1000x1000 (Bilinear)")
# plt.axis('off')
# plt.colorbar(label="Degrees")
# plt.show()
