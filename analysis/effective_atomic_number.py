import pandas as pd
import math

# ==========================================
# 1. ATOMIC DATA: {Element: (Z, A)}
# ==========================================
elements = {
    'H': (1, 1.008), 'C': (6, 12.011), 'O': (8, 15.999),
    'S': (16, 32.06), 'Ti': (22, 47.867), 'Ba': (56, 137.327),
    'W': (74, 183.84), 'Pb': (82, 207.2), 'Bi': (83, 208.980)
}

# ==========================================
# 2. BASE MATERIAL COMPOSITIONS 
# ==========================================
# Pure PPS (C6H4S) Mass Fractions
mol_pps = 6*elements['C'][1] + 4*elements['H'][1] + 1*elements['S'][1]
pps_frac = {
    'C': (6*elements['C'][1]) / mol_pps,
    'H': (4*elements['H'][1]) / mol_pps,
    'S': (1*elements['S'][1]) / mol_pps
}

# Filler Mass Fractions 
fillers = {
    'Pb': {'Pb': 1.0},
    'BaSO4': {
        'Ba': elements['Ba'][1] / (elements['Ba'][1] + elements['S'][1] + 4*elements['O'][1]),
        'S': elements['S'][1] / (elements['Ba'][1] + elements['S'][1] + 4*elements['O'][1]),
        'O': (4*elements['O'][1]) / (elements['Ba'][1] + elements['S'][1] + 4*elements['O'][1])
    },
    'W': {'W': 1.0},
    'Bi2O3': {
        'Bi': (2*elements['Bi'][1]) / (2*elements['Bi'][1] + 3*elements['O'][1]),
        'O': (3*elements['O'][1]) / (2*elements['Bi'][1] + 3*elements['O'][1])
    },
    'Ti3C2O2': {
        'Ti': (3*elements['Ti'][1]) / (3*elements['Ti'][1] + 2*elements['C'][1] + 2*elements['O'][1]),
        'C': (2*elements['C'][1]) / (3*elements['Ti'][1] + 2*elements['C'][1] + 2*elements['O'][1]),
        'O': (2*elements['O'][1]) / (3*elements['Ti'][1] + 2*elements['C'][1] + 2*elements['O'][1])
    }
}

wt_percents = [0, 5, 10, 15, 20, 25, 30]

# ==========================================
# 3. CORE CALCULATION FUNCTIONS
# ==========================================
def get_composite_fractions(filler_name, wt_percent):
    """Calculates elemental mass fractions (w_i) for a given composite."""
    w_f = wt_percent / 100.0
    w_m = 1.0 - w_f
    
    comp_frac = {}
    # Combine matrix elements
    for el, frac in pps_frac.items():
        comp_frac[el] = comp_frac.get(el, 0.0) + frac * w_m
        
    # Combine filler elements
    for el, frac in fillers[filler_name].items():
        comp_frac[el] = comp_frac.get(el, 0.0) + frac * w_f
        
    return comp_frac

def calculate_ai_zeff(comp_frac, m=2.94):
    """Calculates fractional electron content (a_i) and Z_eff."""
    electron_terms = {}
    total_electron_sum = 0.0
    
    # Calculate (w_i * Z_i / A_i) for each element
    for el, w_i in comp_frac.items():
        Z_i, A_i = elements[el]
        term = w_i * (Z_i / A_i)
        electron_terms[el] = term
        total_electron_sum += term
        
    a_i_dict = {}
    zeff_sum = 0.0
    
    # Calculate a_i and sum for Mayneord's equation
    for el, term in electron_terms.items():
        a_i = term / total_electron_sum
        a_i_dict[el] = a_i
        Z_i = elements[el][0]
        zeff_sum += a_i * math.pow(Z_i, m)
        
    Z_eff = math.pow(zeff_sum, 1/m)
    return a_i_dict, Z_eff

# ==========================================
# 4. GENERATE AND DISPLAY RESULTS
# ==========================================
for filler in fillers.keys():
    print(f"=== {filler} / PPS Composites ===")
    
    results = []
    for wt in wt_percents:
        # Step A: Get weight fractions
        comp_frac = get_composite_fractions(filler, wt)
        
        # Step B: Get a_i and Z_eff
        a_i_dict, z_eff = calculate_ai_zeff(comp_frac)
        
        # Format the a_i dictionary into a clean string for the table
        ai_str = " | ".join([f"{el}: {val:.4f}" for el, val in a_i_dict.items()])
        
        results.append({
            'Wt %': wt,
            'Z_eff': round(z_eff, 4),
            'Fractional Electron Content (a_i)': ai_str
        })
        
    # Print as a clean Pandas DataFrame
    df = pd.DataFrame(results)
    print(df.to_string(index=False))
    print("\n" + "="*90 + "\n")