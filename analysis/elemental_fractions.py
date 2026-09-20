
# 1. Elemental mass fractions of pure matrix and fillers
# Calculated from standard molar masses
elements = {
    'PPS': {'C': 0.6663, 'H': 0.0373, 'S': 0.2964},
    'Pb': {'Pb': 1.0000},
    'BaSO4': {'Ba': 0.5884, 'S': 0.1374, 'O': 0.2742},
    'W': {'W': 1.0000},
    'Bi2O3': {'Bi': 0.8970, 'O': 0.1030},
    'Ti3C2O2': {'Ti': 0.7194, 'C': 0.1203, 'O': 0.1603}
}

weight_percents = [5, 10, 15, 20, 25, 30]

print("### Geant4 Elemental Mass Fractions (AddElement variables)\n")

# 2. Loop through each filler and calculate the composite fractions
for filler, f_elements in elements.items():
    if filler == 'PPS': 
        continue
        
    print(f"--- {filler} / PPS Composites ---")
    
    for wt in weight_percents:
        w_f = wt / 100.0        # Filler weight fraction
        w_m = 1.0 - w_f         # Matrix weight fraction
        
        comp_fracs = {}
        
        # Calculate contribution from the PPS Matrix
        for el, frac in elements['PPS'].items():
            comp_fracs[el] = comp_fracs.get(el, 0) + (w_m * frac)
            
        # Calculate contribution from the Filler
        for el, frac in f_elements.items():
            comp_fracs[el] = comp_fracs.get(el, 0) + (w_f * frac)
            
        # Format the output for easy reading/copying into Geant4
        frac_str = " | ".join([f"{el}: {val:.4f}" for el, val in comp_fracs.items()])
        print(f"{wt:2d}% wt ->  {frac_str}")
        
    print("") # Blank line for spacing