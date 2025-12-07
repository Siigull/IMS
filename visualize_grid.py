## Visualizes grids, multiple arguments multiple grids in different windows
## python3 visualize_grid.py <file1> <file2> ...

import sys
import numpy as np
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) < 2:
        print("Usage: python visualize_grid.py <file1> <file2> ...")
        sys.exit(1)

    for filename in sys.argv[1:]:
        try:
            grid = np.loadtxt(filename)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            continue

        plt.figure()
        plt.title(filename)
        plt.imshow(grid, cmap='gray', interpolation='nearest')
        plt.axis('off')

    plt.show()

if __name__ == "__main__":
    main()