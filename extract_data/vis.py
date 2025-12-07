import tifffile
import matplotlib.pyplot as plt

# Load the TIFF
img = tifffile.imread("brno.tif")

# norm = (img - img.min()) / (img.max() - img.min())s
norm = img

# Display it
plt.imshow(norm, cmap='gray')
plt.axis('off')
plt.show()
