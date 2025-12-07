#include <vector>
#include <cstring>
#include <cassert>
#include <iostream>

#define GRID_HEIGHT 1000
#define GRID_WIDTH 1000

#define BUILDING_FILE  "building_grid25.txt"
#define PROTECTED_FILE "protected_grid.txt"
#define ROAD_FILE      "road_grid25.txt"
#define SLOPE_FILE     "slope_grid.txt"
#define FOREST_FILE    "forest_grid.txt"

/////// DATA TYPES ///////
//////////////////////////

size_t to_i(int i, int j) {
    return i * GRID_WIDTH + j;
}

typedef struct {
    float* slope;
    uint8_t* buildings;
    uint8_t* roads;
    uint8_t* protect;
    uint8_t* forest;
} Grid;

Grid init_grid() {
    Grid grid;
    grid.slope     = (float*)malloc(sizeof(float) * GRID_HEIGHT * GRID_WIDTH + 1000);
    grid.buildings = (uint8_t*)malloc(sizeof(uint8_t) * GRID_HEIGHT * GRID_WIDTH + 1000);
    grid.roads     = (uint8_t*)malloc(sizeof(uint8_t) * GRID_HEIGHT * GRID_WIDTH + 1000);
    grid.protect   = (uint8_t*)malloc(sizeof(uint8_t) * GRID_HEIGHT * GRID_WIDTH + 1000);
    grid.forest    = (uint8_t*)malloc(sizeof(uint8_t) * GRID_HEIGHT * GRID_WIDTH + 1000);

    return grid;
}

void zero_out_grid(Grid* grid) {
    memset(grid->slope,     0, sizeof(float)   * GRID_HEIGHT * GRID_WIDTH);
    memset(grid->buildings, 0, sizeof(uint8_t) * GRID_HEIGHT * GRID_WIDTH);
    memset(grid->roads,     0, sizeof(uint8_t) * GRID_HEIGHT * GRID_WIDTH);
    memset(grid->protect,   0, sizeof(uint8_t) * GRID_HEIGHT * GRID_WIDTH);
    memset(grid->forest,    0, sizeof(uint8_t) * GRID_HEIGHT * GRID_WIDTH);
}

typedef struct {
    uint16_t* building_dis; // Count of near buildings. "Near" specified with BUILD_CONV_SQUARE
    uint16_t* road_dis; // Count of near roads. "Near" specified with ROAD_CONV_SQUARE
} Grid_Calculated;

Grid_Calculated init_grid_calculated() {
    Grid_Calculated grid;
    grid.building_dis = (uint16_t*)malloc(sizeof(uint16_t) * GRID_HEIGHT * GRID_WIDTH);
    grid.road_dis     = (uint16_t*)malloc(sizeof(uint16_t) * GRID_HEIGHT * GRID_WIDTH);

    return grid;
}

void zero_out_grid_calculated(Grid_Calculated* grid) {
    memset(grid->building_dis, 0, sizeof(uint8_t) * GRID_HEIGHT * GRID_WIDTH);
    memset(grid->road_dis,     0, sizeof(uint8_t) * GRID_HEIGHT * GRID_WIDTH);
}

typedef struct {
    float slope;
    float land_cover;
    float excluded;
    float urban;
    float transportation;
} Coeffs;

////// LOADING FROM FILE ////////
/////////////////////////////////

void load_buildings(Grid* grid, const char* file_name) {
    FILE* f = fopen(file_name, "r");
    if(f == NULL) exit(1);

    int x = 0, i=0;
    for(; fscanf(f, "%d", &x) == 1; i++) {
        assert(x >= 0 && x <= 255);
        assert(i <= GRID_HEIGHT * GRID_WIDTH);

        grid->buildings[i] = x;
    }
}

void load_slope(Grid* grid, const char* file_name) {
    FILE* f = fopen(file_name, "r");
    if(f == NULL) exit(1);

    int i=0;
    float x;
    for(; fscanf(f, "%f", &x) == 1; i++) {
        assert(i <= GRID_HEIGHT * GRID_WIDTH);

        grid->slope[i] = x;
    }

    assert(i == GRID_HEIGHT * GRID_WIDTH);
}

void load_roads(Grid* grid, const char* file_name) {
    FILE* f = fopen(file_name, "r");
    if(f == NULL) exit(1);

    int x = 0, i=0;
    for(; fscanf(f, "%d", &x) == 1; i++) {
        assert(x >= 0 && x <= 255);
        assert(i <= GRID_HEIGHT * GRID_WIDTH);

        grid->roads[i] = x;
    }

    assert(i == GRID_HEIGHT * GRID_WIDTH);
}

void load_protected(Grid* grid, const char* file_name) {
    FILE* f = fopen(file_name, "r");
    if(f == NULL) exit(1);

    int x = 0, i=0;
    for(; fscanf(f, "%d", &x) == 1; i++) {
        assert(x >= 0 && x <= 255);
        assert(i <= GRID_HEIGHT * GRID_WIDTH);

        grid->protect[i] = x;
    }

    assert(i == GRID_HEIGHT * GRID_WIDTH);
}

void load_forest(Grid* grid, const char* file_name) {
    FILE* f = fopen(file_name, "r");
    if(f == NULL) exit(1);

    int x = 0, i=0;
    for(; fscanf(f, "%d", &x) == 1; i++) {
        assert(x >= 0 && x <= 255);
        assert(i <= GRID_HEIGHT * GRID_WIDTH);

        grid->forest[i] = x;
    }

    assert(i == GRID_HEIGHT * GRID_WIDTH);
}

void load_grid(Grid* grid) {
    load_slope(grid, SLOPE_FILE);
    load_buildings(grid, BUILDING_FILE);
    load_roads(grid, ROAD_FILE);
    load_protected(grid, PROTECTED_FILE);
    load_forest(grid, FOREST_FILE);
}

void print_single_grid(uint8_t* grid) {
    for(int i=0; i < GRID_HEIGHT; i++) {
        for(int j=0; j < GRID_WIDTH; j++) {
            printf("%d ", grid[to_i(i, j)]);
        }
        printf("\n");
    }
}

//////// SIMULATION /////////
/////////////////////////////

#define MAX_COEFF_VALUE 100

// Default coefficient values set
int   coeff_diffusion = 5;   // Spontaneous growth
int   coeff_breed = 15;      // Likelihood of new settlement becoming a spreading center
int   coeff_spread = 20;     // Organic/Edge growth
int   coeff_road = 15;       // Road gravity influence
float critical_slope = 25.0; // Slope at which growth is impossible

/**
 * @brief Extracts additional information from source data.
 *        Count of buildings/roads in a "convolution square" around the cell.
 *        Size of conv squares is set with BUILD_CONV_SQUARE and ROAD_CONV_SQUARE
 * 
 * @param grid source data
 * @param calc result
 */
void calculate_calc_grids(Grid* grid, Grid_Calculated* calc) {
#define BUILD_CONV_SQUARE 10 // The square is (2*thisvalue+1)^2.
    for(int i=0; i < GRID_HEIGHT; i++) {
        for(int j=0; j < GRID_WIDTH; j++) {
            calc->building_dis[to_i(i, j)] = 0;
            for(int im=i-BUILD_CONV_SQUARE; im <= i+BUILD_CONV_SQUARE; im++) {
                for(int jm=j-BUILD_CONV_SQUARE; jm <= j+BUILD_CONV_SQUARE; jm++) {
                    if(im < 0 || im >= GRID_HEIGHT ||
                       jm < 0 || jm >= GRID_WIDTH) {
                    } else {
                        calc->building_dis[to_i(i, j)] += grid->buildings[to_i(im, jm)];
                    }
                }
            }
        }
    }

#define ROAD_CONV_SQUARE 15 // The square is (2*thisvalue+1)^2.
    for(int i=0; i < GRID_HEIGHT; i++) {
        for(int j=0; j < GRID_WIDTH; j++) {
            if(grid->roads[to_i(i, j)]) {
                for(int im=i-ROAD_CONV_SQUARE; im <= i+ROAD_CONV_SQUARE; im++) {
                    for(int jm=j-ROAD_CONV_SQUARE; jm <= j+ROAD_CONV_SQUARE; jm++) {
                        if(im < 0 || im >= GRID_HEIGHT ||
                            jm < 0 || jm >= GRID_WIDTH) {
                        } else {
                            calc->road_dis[to_i(im, jm)]++;
                        }
                    }
                }
            }
        }
    }
}

// Helper to check growth validity (slope, protection, bounds)
// Also adds probabilites of growth for forest and slope
bool can_grow(Grid* g, int i, int j) {
    size_t idx = to_i(i, j);
    if (i < 0 || i >= GRID_HEIGHT || j < 0 || j >= GRID_WIDTH) return false;
    if (g->buildings[idx] > 0) return false;
    if (g->protect[idx] > 0) return false;
    if (g->roads[idx]) return false;

    if (g->slope[idx] >= critical_slope) return false;

    // It is hard to get a permit to build in a forest
    if (g->forest[idx]) {
        if(rand() % 10) return false;
    }

    float slope_factor = 1.0f - (g->slope[idx] / critical_slope);
    if ((rand() % 100) > (slope_factor * 100)) return false;

    return true;
}

/**
 * @brief Roll of dice if cell will grow with coefficients
 *        (1 coeff == (1% chance to grow / ADJUST)) outside of slope and forest factors in can_grow
 *        
 */
bool will_grow(int cell_val, float max_cell_val, float coeff) {
#define ADJUST 10
    return ((rand() % MAX_COEFF_VALUE) / (max_cell_val * ADJUST)) * cell_val > coeff;
}

void iter(Grid* from, Grid* to, Grid_Calculated* calc) {
    std::cerr<< "Iter starting.\n";
    calculate_calc_grids(from, calc);

    // Spontaneous growth - Randomly selected pixels become urbanized
    int diffusion_attempts = (GRID_HEIGHT * GRID_WIDTH * coeff_diffusion) / 1000000; 
    std::vector<int> new_spontaneous_indices;

    for(int k=0; k < diffusion_attempts; k++) {
        int rand_i = rand() % GRID_HEIGHT;
        int rand_j = rand() % GRID_WIDTH;

        if (can_grow(from, rand_i, rand_j)) {
            to->buildings[to_i(rand_i, rand_j)] = 1;

            new_spontaneous_indices.push_back(to_i(rand_i, rand_j));
        }
    }

    // New spreading centers
    // Spontaneous pixels have a chance to turn into new spreading centers
    for (int idx : new_spontaneous_indices) {
        if (will_grow(1, 1, coeff_breed)) {
            int r_i = idx / GRID_WIDTH;
            int r_j = idx % GRID_WIDTH;

#define NSTATEK 1 // Urbanize immediate (NSTATEK*2+1)^2 square around center
            for (int ni = r_i - NSTATEK; ni <= r_i + NSTATEK; ni++) {
                for (int nj = r_j - NSTATEK; nj <= r_j + NSTATEK; nj++) {
                    if (can_grow(from, ni, nj)) {
                        to->buildings[to_i(ni, nj)] = 1;
                    }
                }
            }
        }
    }

    // Edges (Buildings close) growth and Road (Roads close) growth
    for(int i=0; i < GRID_HEIGHT; i++) {
        for(int j=0; j < GRID_WIDTH; j++) {
            // Skip if already urban or protected/steep
            if (from->buildings[to_i(i, j)] > 0) {
                to->buildings[to_i(i, j)] = from->buildings[to_i(i, j)];
                continue;
            }
            if (!can_grow(from, i, j)) continue;
            
            int idx = to_i(i, j);

            // Edge Growth
            if (will_grow(calc->building_dis[idx], 
                          BUILD_CONV_SQUARE*BUILD_CONV_SQUARE, 
                          coeff_spread)) {
                to->buildings[idx] = 1;
                continue; // Skip road if grew
            }

            // Road Influence
            if (will_grow(calc->road_dis[idx], 
                ROAD_CONV_SQUARE*ROAD_CONV_SQUARE, 
                coeff_road)) {
                to->buildings[idx] = 1;
            }
        }
    }
}

int main() {
    Grid one = init_grid();
    Grid two = init_grid();

    Grid* from = &one;
    Grid* to = &two;
    Grid_Calculated calc = init_grid_calculated();

    zero_out_grid(from);
    zero_out_grid(to);
    zero_out_grid_calculated(&calc);

    load_grid(from);
    std::cerr<< "Grids loaded\n";

    iter(from, to, &calc);
    std::memcpy(from->buildings, to->buildings, sizeof(uint8_t) * GRID_HEIGHT * GRID_WIDTH);

    print_single_grid(from->buildings);
}
