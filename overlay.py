## Script to visualize multiple grids over each other. 
## To check if they are matching spatially, to see new growth...
## python3 overlay.py <file1> <file2> ... <fileN>

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap

DISTINCT_COLORS = [
    '#00FFFF',
    '#FF00FF',
    '#00FF00',
    '#FFFF00',
    '#FF3333',
    '#3366FF',
    '#FF9933',
    '#B366FF',
]

def main():
    # Arg handling
    if len(sys.argv) < 3:
        print("Usage: python overlay.py <file1> <file2> ... <fileN>")
        sys.exit(1)

    filenames = sys.argv[1:]
    grids = []

    try:
        for fname in filenames:
            grid = np.loadtxt(fname)
            grids.append(grid)
    except Exception as e:
        print(f"File load error: {e}")
        sys.exit(1)

    base_shape = grids[0].shape
    for i, grid in enumerate(grids[1:]):
        if grid.shape != base_shape:
            print(f"Error: Mismatched dimensions. File {filenames[i+1]} has different dimensions {grid.shape} than {base_shape}")
            sys.exit(1)

    # Actual script
    fig = plt.figure(figsize=(10, 8), facecolor='black')
    
    ax = plt.gca()
    ax.set_facecolor('black')

    plt.title(f"Comparison ({len(grids)} files)", color='white', fontsize=14, pad=20)

    legend_elements = []
    colors = DISTINCT_COLORS

    # Loop over individual grids
    for i, grid in enumerate(grids):
        color = colors[i % len(colors)]
        
        masked_grid = np.ma.masked_where(grid <= 0, grid)
        
        cmap = ListedColormap([color])

        # Alpha can be changed to also see combinations of grids. Can be confusing 
        plt.imshow(masked_grid, cmap=cmap, interpolation='nearest', alpha=1, vmin=0, vmax=1)

        legend_elements.append(
            Patch(facecolor=color, label=f'{filenames[i]}', alpha=0.6)
        )

    plt.axis('off')
    leg = plt.legend(
        handles=legend_elements, 
        loc='upper right', 
        bbox_to_anchor=(1.35, 1), 
        title="In",
        frameon=True,
        facecolor='black', 
        edgecolor='#555555'
    )
    
    plt.setp(leg.get_title(), color='white')
    for text in leg.get_texts():
        plt.setp(text, color='white')
    
    plt.tight_layout()
    
    plt.show()

if __name__ == "__main__":
    main()
