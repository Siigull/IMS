# IMS Urban Growth Simulation
## Structure

- `sleuth.cpp` — Main C++ simulation (urban growth model)
- `Makefile` — Simple build/run for `sleuth.cpp`
- `extract_data/` — Python scripts for preparing input grids (slope, protected, forest, etc.)
- `maps_czechia/` — Raw OSM map data (not required for running the simulation)
- `*_grid.txt` — Input grids (slope, protected, road, building, etc.)

## Prerequisites

- C++ compiler (e.g., `clang++` or `g++` supporting C++11)
- Python 3 with `numpy`, `matplotlib`, `rasterio` (for data prep)

## Usage

### 1. Prepare Input Grids (Python)

From `extract_data/`, run the scripts to generate the required grid files:

```bash
cd extract_data
python3 slope.py
python3 forest.py
# ...other scripts as needed
```

This will produce files like `slope_grid.txt`, `forest_grid.txt`, etc. <br>
extract_grids.sh can be used 

### 2. Build and Run the Simulation (C++)

The simulation has two mains one which just runs it with specified coeffs and other which finds optimal coefficients. Have one commented and one uncommented based on what you want to do.<br>
The variables and values which can be edited to adjust the simulation contain a comment with EDIT.

From the project root:

```bash
make        # builds sleuth from sleuth.cpp
make run    # runs the simulation and automatically outputs stdout to out.txt
```

Output is printed to stdout (or use `make run > out.txt` to save results).

### 3. Visualize or Post-process

You can use the following Python scripts for visualization and post-processing:

- `visualize_grid.py` — Visualize and analyze grid files, with options for color mapping and overlays.
- `overlay.py` — Overlay two grid files and output the result (e.g., compare simulation to ground truth or combine layers).

Example usage:

```bash
python3 plot.py out.txt
python3 visualize_grid.py slope_grid.txt road_grid25.txt
python3 overlay.py out.txt building_grid25.txt
python3 overlay.py result.txt building_grid25.txt
```

These scripts help you inspect, compare, and visualize the simulation and input data.

## Notes



## License

MIT License (or specify your own).
