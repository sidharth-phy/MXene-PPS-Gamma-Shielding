# -*- coding: utf-8 -*-
"""Figures 20, 21 and 22 of the manuscript.

Figure 20, the mass attenuation coefficient against photon energy on logarithmic axes.
Figure 21, the half-value layer against photon energy. Figure 22, the radiation protection
efficiency at 10 mm panel thickness. All three are drawn for pure PPS and the five 30 wt %
composites, from data/phase2/Phase2_Data_Validated.txt.

Usage:
    python3 figures/fig_hvl_rpe.py [path/to/Phase2_Data_Validated.txt] [outdir]
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
from matplotlib.lines import Line2D

filepath = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, 'data', 'phase2', 'Phase2_Data_Validated.txt')
base_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
os.makedirs(base_dir, exist_ok=True)
print("Loading Validated Master Dataset and integrating exact LaTeX densities...")

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
df = df.dropna(subset=['AvgLinAttCoeff(cm-1)'])

# ==========================================
# 2. FILTERING & STRICT ISOLATION
# ==========================================
df = df[~df['Material'].str.startswith('G4_')].copy()

def get_base_mat(m):
    if 'PPS_0Wt' in m: return 'PPS'
    return m.split('_')[0]

def get_wt(m):
    if 'PPS_0Wt' in m: return 0
    return int(m.split('_')[1].replace('Wt', ''))

df['BaseMat'] = df['Material'].apply(get_base_mat)
df['Wt%'] = df['Material'].apply(get_wt)

df_top = df[df['Wt%'].isin([0, 30])].copy()
df_top = df_top.drop_duplicates(subset=['Energy(keV)', 'BaseMat', 'Wt%'])

# ==========================================
# 3. VERIFIED PHYSICS CALCULATIONS
# ==========================================
df_top['HVL(cm)'] = np.log(2) / df_top['AvgLinAttCoeff(cm-1)']
df_top['RPE(%)'] = (1 - np.exp(-df_top['AvgLinAttCoeff(cm-1)'] * 1.0)) * 100

exact_latex_densities = {
    'PPS': 1.3500,        
    'Ti3C2O2': 1.7432,    
    'Pb': 1.8350,         
    'W': 1.8723,          
    'BaSO4': 1.7089,      
    'Bi2O3': 1.8109       
}
df_top['Density(g/cm3)'] = df_top['BaseMat'].map(exact_latex_densities)
df_top['MAC(cm2/g)'] = df_top['AvgLinAttCoeff(cm-1)'] / df_top['Density(g/cm3)']

energies = sorted(df_top['Energy(keV)'].unique())

materials = ['PPS', 'Ti3C2O2', 'Pb', 'W', 'BaSO4', 'Bi2O3']
colors = {'PPS': 'orange', 'Ti3C2O2': 'blue', 'Pb': 'black', 'W': 'red', 'BaSO4': 'green', 'Bi2O3': 'purple'}
labels = {
    'PPS': 'Pure PPS (Baseline)',
    'Ti3C2O2': '30 Wt% Ti₃C₂O₂ MXene', 
    'Pb': '30 Wt% Lead (Pb)', 
    'W': '30 Wt% Tungsten (W)', 
    'BaSO4': '30 Wt% Barium Sulphate (BaSO₄)', 
    'Bi2O3': '30 Wt% Bismuth Oxide (Bi₂O₃)'
}

# Adjusted legend builder to pull the legend tightly up to the text
def add_master_legend(ax_or_fig):
    legend_elements = [Line2D([0], [0], color=colors[m], lw=4, label=labels[m]) for m in materials]
    ax_or_fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.18), 
                     ncol=3, fontsize=14, frameon=True)

# ==========================================
# 4. PLOTTING CANVAS 1: MAC vs Energy
# ==========================================
print("Generating Canvas 1: MAC vs Energy...")
fig1, ax1 = plt.subplots(figsize=(12, 8))
fig1.suptitle('Mass Attenuation Coefficient (MAC) for 30 Wt% Composites', fontsize=22, fontweight='bold', y=0.95)

for mat in materials:
    df_m = df_top[df_top['BaseMat'] == mat].sort_values('Energy(keV)')
    if not df_m.empty:
        ax1.plot(df_m['Energy(keV)'], df_m['MAC(cm2/g)'], marker='o', color=colors[mat], linewidth=3, markersize=9)

ax1.set_xlabel('Energy (keV)', fontsize=16)
ax1.set_ylabel('MAC, μ/ρ (cm²/g)', fontsize=16)
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xticks(energies)
ax1.set_xticklabels(energies, rotation=45, ha='right', fontsize=13)
ax1.grid(True, which='both', linestyle='--', alpha=0.3)

add_master_legend(ax1)
plt.subplots_adjust(bottom=0.18) # Tightened bottom margin
save_path_1 = os.path.join(base_dir, "MAC_vs_Energy.png")
plt.savefig(save_path_1, dpi=300, bbox_inches='tight')
plt.close(fig1)

# ==========================================
# 5. PLOTTING CANVAS 2: HVL vs Energy
# ==========================================
print("Generating Canvas 2: HVL vs Energy...")
fig2, ax2 = plt.subplots(figsize=(12, 8))
fig2.suptitle('Half-Value Layer (HVL) for 30 Wt% Composites', fontsize=22, fontweight='bold', y=0.95)

for mat in materials:
    df_m = df_top[df_top['BaseMat'] == mat].sort_values('Energy(keV)')
    if not df_m.empty:
        ax2.plot(df_m['Energy(keV)'], df_m['HVL(cm)'], marker='s', color=colors[mat], linewidth=3, markersize=9)

ax2.set_xlabel('Energy (keV)', fontsize=16)
ax2.set_ylabel('HVL (cm)', fontsize=16) # Removed subjective text
ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.set_xticks(energies)
ax2.set_xticklabels(energies, rotation=45, ha='right', fontsize=13)
ax2.grid(True, which='both', linestyle='--', alpha=0.3)

add_master_legend(ax2)
plt.subplots_adjust(bottom=0.18) # Tightened bottom margin
save_path_2 = os.path.join(base_dir, "HVL_vs_Energy.png")
plt.savefig(save_path_2, dpi=300, bbox_inches='tight')
plt.close(fig2)

# ==========================================
# 6. PLOTTING CANVAS 3: RPE at 10mm
# ==========================================
print("Generating Canvas 3: RPE at 10mm...")
fig3, ax3 = plt.subplots(figsize=(14, 8))
fig3.suptitle('Radiation Protection Efficiency (RPE) at 10 mm Thickness', fontsize=22, fontweight='bold', y=0.95)

x_indexes = np.arange(len(energies))
bar_width = 0.14

for i, mat in enumerate(materials):
    df_m = df_top[df_top['BaseMat'] == mat].sort_values('Energy(keV)')
    
    rpe_values = []
    for e in energies:
        val = df_m[df_m['Energy(keV)'] == e]['RPE(%)'].values
        rpe_values.append(val[0] if len(val) > 0 else 0)
        
    offset = (i - 2.5) * bar_width 
    ax3.bar(x_indexes + offset, rpe_values, width=bar_width, color=colors[mat], edgecolor='white')

ax3.set_xlabel('Energy (keV)', fontsize=16)
ax3.set_ylabel('RPE (%)', fontsize=16)
ax3.set_xticks(x_indexes)
ax3.set_xticklabels(energies, rotation=45, ha='right', fontsize=13)
ax3.grid(axis='y', linestyle='--', alpha=0.5)
ax3.set_ylim(0, 105) 

add_master_legend(ax3)
plt.subplots_adjust(bottom=0.18) # Tightened bottom margin
save_path_3 = os.path.join(base_dir, "RPE_at_10mm.png")
plt.savefig(save_path_3, dpi=300, bbox_inches='tight')
plt.close(fig3)

print("Success! All 3 formatted physics metrics have been saved as separate high-resolution files.")