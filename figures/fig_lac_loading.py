# -*- coding: utf-8 -*-
"""Figure 13 of the manuscript.

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
# Start from matplotlib's own defaults, not from whatever the machine's
# matplotlibrc holds. A personal config that sets, say, axes.grid or
# savefig.dpi otherwise changes the deposited figures on someone else's
# machine, which is the one thing this deposit exists to prevent.
matplotlib.rcdefaults()
matplotlib.use('Agg')
# Typography is pinned here so these scripts redraw the published figures on
# any machine. DejaVu Sans ships with matplotlib, so it is present everywhere,
# and mathtext is set to the same face: without this, chemical subscripts are
# typeset in a different font from the characters around them. TrueType
# (type 42) rather than Type 3, which Elsevier does not accept in vector
# artwork.
matplotlib.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.sans-serif': ['DejaVu Sans'],
    'mathtext.fontset': 'dejavusans',
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
})
import matplotlib.pyplot as plt
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

# No figure-level title inside the artwork: the caption carries the subject.
# The canvas is smaller than before, which is what lifts the printed lettering.
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(10.60, 6.95))
axes = axes.flatten()

# Formatting dictionaries
materials = ['Ti3C2O2', 'Pb', 'W', 'BaSO4', 'Bi2O3']
colors = {'Ti3C2O2': 'blue', 'Pb': 'black', 'W': 'red', 'BaSO4': 'green', 'Bi2O3': 'purple'}
markers = {'Ti3C2O2': 's', 'Pb': '^', 'W': 'D', 'BaSO4': 'v', 'Bi2O3': 'P'}
labels = {
    'Ti3C2O2': 'Ti$_{3}$C$_{2}$O$_{2}$/PPS', 
    'Pb': 'Pb/PPS', 
    'W': 'W/PPS', 
    'BaSO4': 'BaSO$_{4}$/PPS', 
    'Bi2O3': 'Bi$_{2}$O$_{3}$/PPS'
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
            
            ax.plot(wts, lacs, marker=markers[mat], color=colors[mat], linewidth=1.8,
                    markersize=7, label=labels[mat])
            
    ax.set_title('(%s) %g keV' % ('abcdef'[i], float(energy)), fontsize=20, pad=12)
    ax.set_xlabel('Filler weight fraction (wt %)', fontsize=16, labelpad=7)
    ax.set_ylabel('LAC, μ (cm⁻¹)', fontsize=16, labelpad=6)
    ax.tick_params(labelsize=16)
    ax.set_xticks([0, 5, 10, 15, 20, 25, 30])
    ax.margins(x=0.06, y=0.10)   # keep end markers off the spines
    ax.grid(True, alpha=0.3)

# 6. Global Formatting
handles, lgd_labels = axes[0].get_legend_handles_labels()
fig.legend(handles, lgd_labels, loc='lower center', ncol=5, fontsize=16, frameon=True, bbox_to_anchor=(0.5, 0.03))

plt.subplots_adjust(top=0.95, bottom=0.20, left=0.07, right=0.985, hspace=0.80, wspace=0.42)

# Save and Show
save_path = os.path.join(base_dir, "Figure13.png")
plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"Success! High-resolution canvas saved to:\n{save_path}")

plt.show()
