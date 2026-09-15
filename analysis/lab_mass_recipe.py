import pandas as pd
import math

# ==========================================
# 1. CONSTANTS & PROPERTIES
# ==========================================
rho_pps = 1.35
densities_filler = {'Pb': 11.34, 'BaSO4': 4.50, 'W': 19.25, 'Bi2O3': 8.90, 'Ti3C2O2': 5.44}

# Volume of a 5cm diameter, 2mm thick disc
volume_cm3 = math.pi * (2.5**2) * 0.2
wt_percents = [0, 5, 10, 15, 20, 25, 30]

print(f"--- SAMPLE VOLUME: {volume_cm3:.4f} cm³ ---\n")

# ==========================================
# 2. CALCULATE AND PRINT LAB RECIPES
# ==========================================
for filler, rho_f in densities_filler.items():
    recipe_data = {
        'Wt %': [],
        'PPS Mass (g)': [],
        f'{filler} Mass (g)': [],
        'Total Mass (g)': [],
        'Composite Density (g/cm³)': []
    }
    
    for wt in wt_percents:
        w_f = wt / 100.0
        w_m = 1.0 - w_f
        
        # Step A: Inverse Rule of Mixtures for Density
        rho_c = 1.0 / ((w_f / rho_f) + (w_m / rho_pps))
        
        # Step B: Total Mass to fill the mold
        total_mass = rho_c * volume_cm3
        
        # Step C: Individual masses (The Lab Recipe)
        mass_filler = total_mass * w_f
        mass_pps = total_mass * w_m
        
        # Append to our table data
        recipe_data['Wt %'].append(wt)
        recipe_data['PPS Mass (g)'].append(round(mass_pps, 4))
        recipe_data[f'{filler} Mass (g)'].append(round(mass_filler, 4))
        recipe_data['Total Mass (g)'].append(round(total_mass, 4))
        recipe_data['Composite Density (g/cm³)'].append(round(rho_c, 4))
        
    # Print a clean, dedicated table for each filler material
    df = pd.DataFrame(recipe_data)
    print(f"=== LAB PREP RECIPE: PPS + {filler} ===")
    print(df.to_string(index=False))
    print("\n" + "="*60 + "\n")