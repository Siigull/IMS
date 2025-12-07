#include <vector>
#include <cstring>
#include <cassert>
#include <iostream>
#include <cstdio>
#include <ctime>
#include <string>
#include <math.h>

#define GRID_HEIGHT 1000
#define GRID_WIDTH 1000

// Standard inputs
#define SLOPE_FILE     "slope_grid.txt"
#define PROTECTED_FILE "protected_grid.txt"
#define FOREST_FILE    "forest_grid.txt"
// Dynamic inputs handled in main

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
    // +1000 padding for safety as seen in original code
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

// Copy just the building layer (the one that changes)
void copy_buildings(Grid* src, Grid* dest) {
    memcpy(dest->buildings, src->buildings, sizeof(uint8_t) * GRID_HEIGHT * GRID_WIDTH);
}

typedef struct {
    uint16_t* building_dis; 
    uint16_t* road_dis; 
} Grid_Calculated;

Grid_Calculated init_grid_calculated() {
    Grid_Calculated grid;
    grid.building_dis = (uint16_t*)malloc(sizeof(uint16_t) * GRID_HEIGHT * GRID_WIDTH);
    grid.road_dis     = (uint16_t*)malloc(sizeof(uint16_t) * GRID_HEIGHT * GRID_WIDTH);
    return grid;
}

void zero_out_grid_calculated(Grid_Calculated* grid) {
    memset(grid->building_dis, 0, sizeof(uint16_t) * GRID_HEIGHT * GRID_WIDTH);
    memset(grid->road_dis,     0, sizeof(uint16_t) * GRID_HEIGHT * GRID_WIDTH);
}

void print_byte_grid(uint8_t* grid) {
    for(int i=0; i < GRID_HEIGHT; i++) {
        for(int j=0; j < GRID_WIDTH; j++) {
            printf("%d ", grid[to_i(i, j)]);
        }
        printf("\n");
    }
}

////// LOADING FROM FILE ////////
/////////////////////////////////

void load_layer_byte(uint8_t* layer, const char* file_name) {
    FILE* f = fopen(file_name, "r");
    if(f == NULL) {
        fprintf(stderr, "Error opening %s\n", file_name);
        exit(1);
    }

    int x, i=0;
    for(; fscanf(f, "%d", &x) == 1; i++) {
        assert(i <= GRID_HEIGHT * GRID_WIDTH);
        layer[i] = (uint8_t)x;
    }
    
    fclose(f);
    assert(i == GRID_HEIGHT * GRID_WIDTH);
}

void load_layer_float(float* layer, const char* file_name) {
    FILE* f = fopen(file_name, "r");
    if(f == NULL) {
        fprintf(stderr, "Error opening %s\n", file_name);
        exit(1);
    }

    int i=0;
    float x;
    for(; fscanf(f, "%f", &x) == 1; i++) {
        assert(i <= GRID_HEIGHT * GRID_WIDTH);
        layer[i] = x;
    }

    fclose(f);
    assert(i == GRID_HEIGHT * GRID_WIDTH);
}

void load_static_layers(Grid* grid) {
    load_layer_float(grid->slope, SLOPE_FILE);
    
    load_layer_byte(grid->protect, PROTECTED_FILE);
    load_layer_byte(grid->forest, FOREST_FILE);
}

void load_dynamic_layers(Grid* grid, int year) {
    char buffer[64];
    
    snprintf(buffer, 64, "building_grid%d.txt", year);
    load_layer_byte(grid->buildings, buffer);

    snprintf(buffer, 64, "road_grid%d.txt", year);
    load_layer_byte(grid->roads, buffer);
}

//////// SIMULATION /////////
/////////////////////////////

#define MAX_COEFF_VALUE 100

// Default coefficient values set
// EDIT
int   coeff_diffusion = 5;   // Spontaneous growth
int   coeff_breed = 15;      // Likelihood of new settlement becoming a spreading center
int   coeff_spread = 15;     // Organic/Edge growth
int   coeff_road = 20;       // Road gravity influence
float critical_slope = 50.0; // Slope at which growth is impossible

void calculate_calc_grids(Grid* grid, Grid_Calculated* calc) {
#define BUILD_CONV_SQUARE 7 // EDIT
    for(int i=0; i < GRID_HEIGHT; i++) {
        for(int j=0; j < GRID_WIDTH; j++) {
            calc->building_dis[to_i(i, j)] = 0;
            // Simplified boundary check for speed in brute force
            int top   = (i - BUILD_CONV_SQUARE < 0) ? 0 : i - BUILD_CONV_SQUARE;
            int bot   = (i + BUILD_CONV_SQUARE >= GRID_HEIGHT) ? GRID_HEIGHT - 1 : i + BUILD_CONV_SQUARE;
            int left  = (j - BUILD_CONV_SQUARE < 0) ? 0 : j - BUILD_CONV_SQUARE;
            int right = (j + BUILD_CONV_SQUARE >= GRID_WIDTH) ? GRID_WIDTH - 1 : j + BUILD_CONV_SQUARE;

            for(int im=top; im <= bot; im++) {
                for(int jm=left; jm <= right; jm++) {
                     calc->building_dis[to_i(i, j)] += grid->buildings[to_i(im, jm)];
                }
            }
        }
    }

#define ROAD_CONV_SQUARE 10 // EDIT
    memset(calc->road_dis, 0, sizeof(uint16_t) * GRID_HEIGHT * GRID_WIDTH);
    
    for(int i=0; i < GRID_HEIGHT; i++) {
        for(int j=0; j < GRID_WIDTH; j++) {
            if(grid->roads[to_i(i, j)]) {
                int top   = (i - ROAD_CONV_SQUARE < 0) ? 0 : i - ROAD_CONV_SQUARE;
                int bot   = (i + ROAD_CONV_SQUARE >= GRID_HEIGHT) ? GRID_HEIGHT - 1 : i + ROAD_CONV_SQUARE;
                int left  = (j - ROAD_CONV_SQUARE < 0) ? 0 : j - ROAD_CONV_SQUARE;
                int right = (j + ROAD_CONV_SQUARE >= GRID_WIDTH) ? GRID_WIDTH - 1 : j + ROAD_CONV_SQUARE;

                for(int im=top; im <= bot; im++) {
                    for(int jm=left; jm <= right; jm++) {
                        calc->road_dis[to_i(im, jm)]++;
                    }
                }
            }
        }
    }
}

bool can_grow(Grid* g, int i, int j) {
    size_t idx = to_i(i, j);
    if (i < 0 || i >= GRID_HEIGHT || j < 0 || j >= GRID_WIDTH) return false;
    if (g->buildings[idx] > 0) return false;
    if (g->protect[idx] > 0) return false;
    if (g->roads[idx]) return false; // Usually roads aren't built over, but logic kept from source

    if (g->slope[idx] >= critical_slope) return false;

    if (g->forest[idx]) {
        if(rand() % 10) return false; // 90% resistance
    }

    float slope_factor = 1.0f - (g->slope[idx] / critical_slope);
    if ((rand() % 100) > (slope_factor * 100)) return false;

    return true;
}

bool will_grow(int cell_val, float max_cell_val, float coeff) {
#define ADJUST 10
    return ((rand() % MAX_COEFF_VALUE) / (max_cell_val * ADJUST)) * cell_val > coeff;
}

// The iteration logic follows standard cellular automata rules:
// Spontaneous -> Spreading Center -> Edge Growth -> Road Gravity
void iter(Grid* from, Grid* to, Grid_Calculated* calc) {
    std::cerr << "Iter" << "\n";
    calculate_calc_grids(from, calc);

    // Copy existing state first
    copy_buildings(from, to);

    // Spontaneous growth
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
    for (int idx : new_spontaneous_indices) {
        if (will_grow(1, 1, coeff_breed)) {
            int r_i = idx / GRID_WIDTH;
            int r_j = idx % GRID_WIDTH;
#define NSTATEK 1 // EDIT
            for (int ni = r_i - NSTATEK; ni <= r_i + NSTATEK; ni++) {
                for (int nj = r_j - NSTATEK; nj <= r_j + NSTATEK; nj++) {
                    if (can_grow(from, ni, nj)) {
                        to->buildings[to_i(ni, nj)] = 1;
                    }
                }
            }
        }
    }

    // Edges and Roads
    for(int i=0; i < GRID_HEIGHT; i++) {
        for(int j=0; j < GRID_WIDTH; j++) {
            if (from->buildings[to_i(i, j)] > 0) continue;
            if (!can_grow(from, i, j)) continue;
            
            int idx = to_i(i, j);

            // Edge Growth
            if (will_grow(calc->building_dis[idx], 
                          BUILD_CONV_SQUARE*BUILD_CONV_SQUARE, 
                          coeff_spread)) {
                to->buildings[idx] = 1;
                continue; 
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

////////// LEARNING LOGIC ///////////
/////////////////////////////////////

float calculate_iou_score(Grid* sim, Grid* truth) {
    long intersection = 0;
    long union_count = 0;

    for(int i=0; i < GRID_HEIGHT * GRID_WIDTH; i++) {
        bool s = sim->buildings[i] > 0;
        bool t = truth->buildings[i] > 0;

        if (s && t) intersection++;
        if (s || t) union_count++;
    }

    if (union_count == 0) return 0.0f;
    return (float)intersection / (float)union_count;
}

int main() {
    Grid main_grid = init_grid(); // Working grid
    Grid result_grid = init_grid(); // Double buffer

    Grid_Calculated calc = init_grid_calculated();

    zero_out_grid(&main_grid);
    zero_out_grid(&result_grid);
    zero_out_grid_calculated(&calc);

    load_static_layers(&main_grid);
    load_dynamic_layers(&main_grid, 22);

    std::cerr << "Grids loaded\n";

    iter(&main_grid, &result_grid, &calc);

    print_byte_grid(result_grid.buildings);
}

// int main() {
//     srand(time(NULL));

//     Grid main_grid = init_grid(); // Working grid
//     Grid buffer_grid = init_grid(); // Double buffer
    
//     Grid truth_14 = init_grid();
//     Grid truth_18 = init_grid();
//     Grid truth_22 = init_grid();

//     Grid_Calculated calc = init_grid_calculated();
//     zero_out_grid_calculated(&calc);

//     std::cerr << "Loading static layers...\n";
//     load_static_layers(&main_grid);

//     memcpy(truth_14.slope,   main_grid.slope, sizeof(float)*GRID_HEIGHT*GRID_WIDTH);
//     memcpy(truth_14.forest,  main_grid.forest, sizeof(uint8_t)*GRID_HEIGHT*GRID_WIDTH);
//     memcpy(truth_14.protect, main_grid.protect, sizeof(uint8_t)*GRID_HEIGHT*GRID_WIDTH);

//     std::cerr << "Loading dynamic layers...\n";
//     load_dynamic_layers(&truth_14, 14);
//     load_dynamic_layers(&truth_18, 18);
//     load_dynamic_layers(&truth_22, 22);

//     ///////// SIMULATION /////////
//     //////////////////////////////

//     int best_diff = 0, best_breed = 0, best_spread = 0, best_road = 0;
//     float best_score = -1.0f;

//     int ATTEMPTS = 100; 
//     int values[100][2] = {{10, 10},{10, 20},{10, 30},{10, 40},{10, 50},{10, 60},{10, 70},{10, 80},{10, 90},{10, 100},{20, 10},{20, 20},{20, 30},{20, 40},{20, 50},{20, 60},{20, 70},{20, 80},{20, 90},{20, 100},{30, 10},{30, 20},{30, 30},{30, 40},{30, 50},{30, 60},{30, 70},{30, 80},{30, 90},{30, 100},{40, 10},{40, 20},{40, 30},{40, 40},{40, 50},{40, 60},{40, 70},{40, 80},{40, 90},{40, 100},{50, 10},{50, 20},{50, 30},{50, 40},{50, 50},{50, 60},{50, 70},{50, 80},{50, 90},{50, 100},{60, 10},{60, 20},{60, 30},{60, 40},{60, 50},{60, 60},{60, 70},{60, 80},{60, 90},{60, 100},{70, 10},{70, 20},{70, 30},{70, 40},{70, 50},{70, 60},{70, 70},{70, 80},{70, 90},{70, 100},{80, 10},{80, 20},{80, 30},{80, 40},{80, 50},{80, 60},{80, 70},{80, 80},{80, 90},{80, 100},{90, 10},{90, 20},{90, 30},{90, 40},{90, 50},{90, 60},{90, 70},{90, 80},{90, 90},{90, 100},{100, 10},{100, 20},{100, 30},{100, 40},{100, 50},{100, 60},{100, 70},{100, 80},{100, 90},{100, 100}};

//     std::cerr << "Starting Brute Force Learning (" << ATTEMPTS << " attempts)...\n";

//     for(int n=0; n < ATTEMPTS; n++) {
//         // coeff_diffusion = (rand() % MAX_COEFF_VALUE) + 1;
//         // coeff_breed     = (rand() % MAX_COEFF_VALUE) + 1;
//         coeff_spread    = values[n][0];
//         coeff_road      = values[n][1];

//         // B. Simulation Phase 1: 2014 -> 2018
//         // Reset working grid to 2014 state
//         copy_buildings(&truth_14, &main_grid);
//         // Load 2014 roads into main_grid for physics
//         memcpy(main_grid.roads, truth_14.roads, sizeof(uint8_t)*GRID_HEIGHT*GRID_WIDTH);

//         // Run 4 years
//         iter(&main_grid, &buffer_grid, &calc);
//         copy_buildings(&buffer_grid, &main_grid);
//         float score1 = calculate_iou_score(&main_grid, &truth_18);

//         // C. Simulation Phase 2: 2018 -> 2022
//         // Reset working grid to 2018 state (Ground Truth, not simulated result, to correct errors)
//         copy_buildings(&truth_18, &main_grid);
//         memcpy(main_grid.roads, truth_18.roads, sizeof(uint8_t)*GRID_HEIGHT*GRID_WIDTH);

//         // Run 4 years
//         iter(&main_grid, &buffer_grid, &calc);
//         copy_buildings(&buffer_grid, &main_grid);
//         float score2 = calculate_iou_score(&main_grid, &truth_22);

//         float avg_score = (score1 + score2) / 2.0f;

//         if (avg_score > best_score) {
//             best_score  = avg_score;
//             best_diff   = coeff_diffusion;
//             best_breed  = coeff_breed;
//             best_spread = coeff_spread;
//             best_road   = coeff_road;
            
//             std::cerr << "New Best [" << n << "]: " << avg_score * 100 << "% IoU | "
//                       << "Diff: " << best_diff << " Breed: " << best_breed 
//                       << " Sprd: " << best_spread << " Road: " << best_road << "\n";
//         }
//     }

//     std::cerr << "--------------------------------\n";
//     std::cerr << "CALIBRATION COMPLETE\n";
//     std::cerr << "Best Coefficients found:\n";
//     std::cerr << "Diffusion: " << best_diff << "\n";
//     std::cerr << "Breed:     " << best_breed << "\n";
//     std::cerr << "Spread:    " << best_spread << "\n";
//     std::cerr << "Road:      " << best_road << "\n";
//     std::cerr << "--------------------------------\n";
    
//     return 0;
// }
