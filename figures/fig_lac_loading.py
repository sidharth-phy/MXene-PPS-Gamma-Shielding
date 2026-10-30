# -*- coding: utf-8 -*-
"""Figure 19 of the manuscript.

Linear attenuation coefficient against filler weight percentage, from 0 to 30 wt %, one
panel per photon energy, drawn from data/phase2/Phase2_Data_Validated.txt.

Usage:
    python3 figures/fig_lac_loading.py [path/to/Phase2_Data_Validated.txt] [outdir]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

filepath = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, 'data', 'phase2', 'Phase2_Data_Validated.txt')
base_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
os.makedirs(base_dir, exist_ok=True)

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

header_idx = 0
for i, line in enumerate(lines):
    if line.startswith('Energy(keV)'):
        header_idx = i
        break

df = pd.read_csv(filepath, sep='|', skiprows=header_idx, skipinitialspace=True)
df.columns = [col.strip() for col in df.columns]
df = df[~df['Energy(keV)'].astype(str).str.contains('-')].copy()

for col in df.columns:
    if df[col].dtype == 'O':
        df[col] = df[col].astype(str).str.strip()

df['Energy(keV)'] = pd.to_numeric(df['Energy(keV)'])
df['AvgLinAttCoeff(cm-1)'] = pd.to_numeric(df['AvgLinAttCoeff(cm-1)'], errors='coerce')

# Drop any rows where AvgLinAttCoeff couldn't be calculated
df = df.dropna(subset=['AvgLinAttCoeff(cm-1)'])

# Filter out pure metal benchmarks (they don't belong on a 0-30% scaling chart)
df = df[~df['Material'].str.startswith('G4_')].copy()

# 3. Helper functions to extract Base Material and Weight Percentage
def get_base_mat(m):
    if 'PPS_0Wt' in m: return 'PPS'
    return m.split('_')[0]

def get_wt(m):
    if 'PPS_0Wt' in m: return 0
    return int(m.split('_')[1].replace('Wt', ''))

df['BaseMat'] = df['Material'].apply(get_base_mat)
df['Wt%'] = df['Material'].apply(get_wt)

# We only need one row per Material/Energy combination
df_unique = df.drop_duplicates(subset=['Energy(keV)', 'BaseMat', 'Wt%'])

# 4. Set up the plotting Canvas (2 rows, 3 columns = 6 subplots)
energies = sorted(df_unique['Energy(keV)'].unique())

# *** FIX 1: Made the canvas taller to give the layout engine more room to breathe ***
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(22, 14))

# *** FIX 2: Locked the suptitle to y=0.95 so it stays near the top but leaves a clean top margin ***
fig.suptitle('Shielding Efficiency: Linear Attenuation vs. Filler Loading', fontsize=28, fontweight='bold', y=0.95)
axes = axes.flatten()

# Formatting dictionaries
materials = ['Ti3C2O2', 'Pb', 'W', 'BaSO4', 'Bi2O3']
colors = {'Ti3C2O2': 'blue', 'Pb': 'black', 'W': 'red', 'BaSO4': 'green', 'Bi2O3': 'purple'}
labels = {
    'Ti3C2O2': 'Ti₃C₂O₂ MXene', 
    'Pb': 'Lead (Pb)', 
    'W': 'Tungsten (W)', 
    'BaSO4': 'Barium Sulphate (BaSO₄)', 
    'Bi2O3': 'Bismuth Oxide (Bi₂O₃)'
}

# 5. Loop through energies and generate plots
for i, energy in enumerate(energies):
    ax = axes[i]
    df_e = df_unique[df_unique['Energy(keV)'] == energy]
    
    # Extract the Pure PPS baseline value for this specific energy safely
    pps_baseline_row = df_e[df_e['BaseMat'] == 'PPS']
    if not pps_baseline_row.empty:
        pps_val = pps_baseline_row['AvgLinAttCoeff(cm-1)'].iloc[0]
    else:
        pps_val = 0 
        
    for mat in materials:
        # The sort_values('Wt%') ensures the line is drawn perfectly from left to right
        df_m = df_e[df_e['BaseMat'] == mat].sort_values('Wt%')
        
        if not df_m.empty:
            # Anchor all lines to the Pure PPS 0 Wt% coordinate
            wts = [0] + df_m['Wt%'].tolist()
            lacs = [pps_val] + df_m['AvgLinAttCoeff(cm-1)'].tolist()
            
            ax.plot(wts, lacs, marker='o', color=colors[mat], linewidth=2.5, markersize=8, label=labels[mat])
            
    ax.set_title(f'{energy} keV', fontsize=20, pad=15)
    ax.set_xlabel('Filler Weight Fraction (Wt%)', fontsize=15)
    ax.set_ylabel('LAC, μ (cm⁻¹)', fontsize=15)
    ax.set_xticks([0, 5, 10, 15, 20, 25, 30])
    ax.grid(True, alpha=0.3)

# 6. Global Formatting
handles, lgd_labels = axes[0].get_legend_handles_labels()
fig.legend(handles, lgd_labels, loc='lower center', ncol=5, fontsize=16, frameon=True, bbox_to_anchor=(0.5, 0.03))

# *** FIX 3: Dropped the 'top' margin to 0.80. This creates a massive gap between the suptitle and the subplot titles. ***
plt.subplots_adjust(top=0.80, bottom=0.20, left=0.06, right=0.98, hspace=0.55, wspace=0.25)

# Save and Show
save_path = os.path.join(base_dir, "Efficiency_Curves_Canvas.png")
plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"Success! High-resolution canvas saved to:\n{save_path}")

plt.show()