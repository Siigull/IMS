import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap

# --- KONFIGURACE BAREV ---
# Definice vlastních, velmi výrazných "neonových" barev pro černý podklad
# Používáme Hex kódy pro: Cyan, Magenta, Lime Green, Bright Yellow, Bright Red, Electric Blue, Orange
DISTINCT_COLORS = [
    '#00FFFF', # Azurová (Cyan)
    '#FF00FF', # Purpurová (Magenta)
    '#00FF00', # Limetková zelená
    '#FFFF00', # Jasně žlutá
    '#FF3333', # Jasně červená
    '#3366FF', # Elektrická modrá
    '#FF9933', # Oranžová
    '#B366FF', # Fialová
]

def main():
    # 1. Kontrola argumentů
    if len(sys.argv) < 3:
        print("Použití: python overlay.py <soubor1> <soubor2> ... <souborN>")
        sys.exit(1)

    filenames = sys.argv[1:]
    grids = []

    # 2. Načtení matic
    try:
        for fname in filenames:
            grid = np.loadtxt(fname)
            grids.append(grid)
    except Exception as e:
        print(f"Chyba při načítání souboru: {e}")
        sys.exit(1)

    # 3. Kontrola rozměrů
    base_shape = grids[0].shape
    for i, grid in enumerate(grids[1:]):
        if grid.shape != base_shape:
            print(f"Chyba: Soubor {filenames[i+1]} má jiný rozměr {grid.shape} než první soubor {base_shape}")
            sys.exit(1)

    # --- PŘÍPRAVA ČERNÉHO POZADÍ ---
    # Nastavení barvy pozadí obrázku (to okolo grafu)
    fig = plt.figure(figsize=(10, 8), facecolor='black')
    
    # Získání aktuálních os a nastavení jejich pozadí (samotná plocha grafu)
    ax = plt.gca()
    ax.set_facecolor('black')

    # Nastavení titulku na bílou barvu, aby byl čitelný
    plt.title(f"Overlay porovnání ({len(grids)} souborů)", color='white', fontsize=14, pad=20)

    legend_elements = []
    colors = DISTINCT_COLORS

    # 4. Vykreslování vrstev
    for i, grid in enumerate(grids):
        # Výběr barvy z našeho vlastního seznamu
        color = colors[i % len(colors)]
        
        # Maska pro skrytí nulových hodnot (pozadí)
        masked_grid = np.ma.masked_where(grid <= 0, grid)
        
        # Vytvoření colormapy pro tuto jednu barvu
        cmap = ListedColormap([color])

        # Vykreslení vrstvy
        # alpha=0.6: Mírně zvýšená neprůhlednost, aby barvy více zářily na černé
        plt.imshow(masked_grid, cmap=cmap, interpolation='nearest', alpha=1, vmin=0, vmax=1)

        # Přidání do legendy
        legend_elements.append(
            Patch(facecolor=color, label=f'{filenames[i]}', alpha=0.6)
        )

    # Odstranění os (aby nerušily černý vzhled)
    plt.axis('off')
    
    # --- NASTAVENÍ LEGENDY PRO TMAVÝ REŽIM ---
    # frameon=True: Zobrazit rámeček legendy
    # facecolor='black': Černé pozadí legendy
    # edgecolor='gray': Šedý okraj rámečku
    # labelcolor='white': Bílý text (vyžaduje novější matplotlib, jinak se text přizpůsobí globálnímu nastavení)
    leg = plt.legend(
        handles=legend_elements, 
        loc='upper right', 
        bbox_to_anchor=(1.35, 1), 
        title="Vstupy",
        frameon=True,
        facecolor='black', 
        edgecolor='#555555'
    )
    
    # Ruční nastavení barvy textu v legendě na bílou (pro jistotu kompatibility)
    plt.setp(leg.get_title(), color='white')
    for text in leg.get_texts():
        plt.setp(text, color='white')
    
    plt.tight_layout()
    
    # Uložení obrázku (volitelné, zachová černé pozadí při uložení)
    # plt.savefig("overlay_dark.png", facecolor=fig.get_facecolor(), edgecolor='none')
    
    plt.show()

if __name__ == "__main__":
    main()
