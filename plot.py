## Bylo použito pro experimenty s distribučními funkcemi
## Použito pro funkci will_grow uvnitř sleuth.cpp

import numpy as np
import matplotlib.pyplot as plt

def plot_growth_probability():
    x = np.linspace(0, 1, 500)

    coefficients = [0, 25, 50, 75, 100]

    plt.figure(figsize=(10, 6))

    for coeff in coefficients:
        alpha = 1.0 + 10.0 * (coeff / 100.0)
        
        y = np.power(x, alpha)
        
        plt.plot(x, y, label=f'coeff = {coeff} (alpha={alpha:.1f})', linewidth=2)

    plt.title('Probability of Growth vs. Cell Value', fontsize=14)
    plt.xlabel('Normalized Cell Value (cell_val / max_val)', fontsize=12)
    plt.ylabel('Probability of Growth', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    plt.plot([0, 1], [0, 1], 'k--', alpha=0.2) 
    
    plt.show()

if __name__ == "__main__":
    plot_growth_probability()
