import pandas as pd
import math

# ==========================================
# 1. DEFINE CONSTANTS & MATERIAL PROPERTIES
# ==========================================
rho_pps = 1.35  # Density of pure PPS matrix (g/cm³)

# Densities of various filler materials (g/cm³)
densities_filler = {
    'Pb': 11.34,
    'BaSO4': 4.50,
    'W': 19.25,
    'Bi2O3': 8.90,
    'Ti3C2O2': 5.44
}

# Disc dimensions for physical mass calculation
diameter_cm = 5.0
radius_cm = diameter_cm / 2.0
thickness_cm = 0.2  # 2 mm = 0.2 cm

# Step-by-step volume calculation: V = pi * r^2 * h
volume_cm3 = math.pi * (radius_cm**2) * thickness_cm

# Filler weight percentages to simulate (0% to 30%)
wt_percents = [0, 5, 10, 15, 20, 25, 30]

# Dictionaries to store our generated columns
composite_densities = {'Wt %': wt_percents}
total_masses = {'Wt %': wt_percents}

# ==========================================
# 2. STEP-BY-STEP CALCULATIONS
# ==========================================
for filler, rho_f in densities_filler.items():
    density_col = []
    mass_col = []
    
    for wt in wt_percents:
        # Step A: Convert weight percentage to mathematical fractions
        w_f = wt / 100.0        # Fraction of filler
        w_m = 1.0 - w_f         # Fraction of PPS matrix
        
        # Step B: Calculate theoretical composite density (Inverse Rule of Mixtures)
        term_filler = w_f / rho_f
        term_matrix = w_m / rho_pps
        rho_c = 1.0 / (term_filler + term_matrix)
        
        # Step C: Calculate the total mass required to mold the physical disc
        total_mass = rho_c * volume_cm3
        
        # Save rounded results to the column lists
        density_col.append(round(rho_c, 4))
        mass_col.append(round(total_mass, 4))
        
    # Assign completed columns to the dictionaries
    composite_densities[f"Composite w/ {filler}"] = density_col
    total_masses[f"Mass w/ {filler}"] = mass_col

# ==========================================
# 3. DISPLAY RESULTS CLEARLY
# ==========================================
df_density = pd.DataFrame(composite_densities)
df_mass = pd.DataFrame(total_masses)

print("=== COMPOSITE BULK DENSITIES (g/cm³) ===")
print("Note: The 0 Wt % row represents pure PPS. Therefore, all columns correctly read 1.35 g/cm³.")
print("-" * 80)
print(df_density.to_string(index=False))
print("\n")

print("=== TOTAL REQUIRED SAMPLE MASS (g) ===")
print(f"Sample Volume: {volume_cm3:.4f} cm³ (Diameter: 5cm, Thickness: 2mm)")
print("-" * 80)
print(df_mass.to_string(index=False))