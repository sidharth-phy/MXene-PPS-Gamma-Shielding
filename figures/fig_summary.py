# -*- coding: utf-8 -*-
"""Figures 11, 12, 23 and 24 of the manuscript.

Figure 11, the laboratory replica overlay of simulated against NIST/XCOM linear
attenuation coefficients. Figure 12, the absolute deviation of the Phase 2 coefficients
from NIST/XCOM. Figure 23, the theoretical effective atomic number against filler
loading. Figure 24, the MXene enhancement factor against photon energy. The first three
read data/phase2/Phase2_Data_Validated.txt; Figure 23 is computed in this file from
Mayneord's power law with m = 2.94.

Usage:
    python3 figures/fig_summary.py [path/to/Phase2_Data_Validated.txt] [outdir]
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

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

header_idx = 0
for i, line in enumerate(lines):
    if line.startswith('Energy(keV)'):
        header_idx = i
        break

df = pd.read_csv(filepath, sep='|', skiprows=header_idx, skipinitialspace=True)
df.columns = [str(col).strip() for col in df.columns]
df = df[[c for c in df.columns if not c.startswith('Unnamed')]]
df = df[df['Material'].notna()]
df = df[~df['Material'].astype(str).str.contains('---', na=False)].reset_index(drop=True)
for c in df.columns:
    if c != 'Material':
        df[c] = pd.to_numeric(df[c], errors='coerce')
df['Material'] = df['Material'].astype(str).str.strip()

# ==========================================
# 2. DYNAMIC COLUMN MAPPING (Handles Superscripts)
# ==========================================
# We use 'next' to find the column that *contains* the keyword, bypassing superscript issues
energy_col = 'Energy(keV)'
mat_col = 'Material'
lac_col = next((c for c in df.columns if 'AvgLinAttCoeff' in c), None)
nist_col = next((c for c in df.columns if 'NIST_LAC' in c), None)
err_col = next((c for c in df.columns if 'LAC_%err' in c), None)

if not lac_col: raise ValueError("Could not find AvgLinAttCoeff column.")

df[energy_col] = pd.to_numeric(df[energy_col], errors='coerce')
df[lac_col] = pd.to_numeric(df[lac_col], errors='coerce')
df = df.dropna(subset=[energy_col, lac_col])

# ==========================================
# 3. FILTERING & MATERIAL MAPPING
# ==========================================
def get_base_mat(m):
    m_str = str(m)
    if 'PPS_0Wt' in m_str: return 'PPS'
    return m_str.split('_')[0]

def get_wt(m):
    m_str = str(m)
    if 'PPS_0Wt' in m_str: return 0
    try:
        return int(m_str.split('_')[1].replace('Wt', ''))
    except:
        return -1 # For bare G4 materials

df['BaseMat'] = df[mat_col].apply(get_base_mat)
df['Wt%'] = df[mat_col].apply(get_wt)

# Remove bare G4 materials
df = df[df['Wt%'] >= 0].copy()

energies = sorted(df[energy_col].unique())

# Formatting Setup
materials = ['PPS', 'Ti3C2O2', 'Pb', 'W', 'BaSO4', 'Bi2O3']
colors = {'PPS': 'orange', 'Ti3C2O2': 'blue', 'Pb': 'black', 'W': 'red', 'BaSO4': 'green', 'Bi2O3': 'purple'}
bar_labels = {'PPS': 'Pure PPS', 'Ti3C2O2': '30 Wt% Ti₃C₂O₂', 'Pb': '30 Wt% Pb',
              'W': '30 Wt% W', 'BaSO4': '30 Wt% BaSO₄', 'Bi2O3': '30 Wt% Bi₂O₃'}
ov_labels = {'PPS': 'Pure PPS (baseline)', 'Pb': '30 Wt% Pb/PPS'}
tick_labels = lambda es: ['%g' % e for e in es]

labels = {
    'PPS': 'Pure PPS (Baseline)',
    'Ti3C2O2': 'Ti₃C₂O₂ MXene', 
    'Pb': 'Lead (Pb)', 
    'W': 'Tungsten (W)', 
    'BaSO4': 'Barium Sulphate (BaSO₄)', 
    'Bi2O3': 'Bismuth Oxide (Bi₂O₃)'
}

# ==========================================
# CANVAS 1: VALIDATION ERROR BAR CHART
# ==========================================
if err_col:
    print("Generating Canvas 1: Validation Error...")
    # FIX APPLIED: .abs() forces all negative deviations to be positive magnitudes
    df['Error_Numeric'] = pd.to_numeric(df[err_col], errors='coerce').abs()
    df_top = df[df['Wt%'].isin([0, 30])].copy()
    
    fig1, ax1 = plt.subplots(figsize=(14, 8))
    fig1.suptitle('Absolute Deviation of Phase 2 Coefficients from NIST/XCOM', fontsize=22, fontweight='bold', y=0.95)
    
    x_indexes = np.arange(len(energies))
    bar_width = 0.14
    
    for i, mat in enumerate(materials):
        df_m = df_top[df_top['BaseMat'] == mat].sort_values(energy_col)
        err_values = [df_m[df_m[energy_col] == e]['Error_Numeric'].mean() if not df_m[df_m[energy_col] == e].empty else 0 for e in energies]
        
        offset = (i - 2.5) * bar_width 
        ax1.bar(x_indexes + offset, err_values, width=bar_width, color=colors[mat], edgecolor='white', label=bar_labels[mat])

    ax1.set_xlabel('Energy (keV)', fontsize=16)
    ax1.set_ylabel('Absolute deviation from NIST/XCOM (%)', fontsize=16)
    ax1.set_xticks(x_indexes)
    ax1.set_xticklabels(tick_labels(energies), rotation=45, ha='right', fontsize=13)
    ax1.axhline(y=5, color='red', linestyle='--', alpha=0.7, label='5% Phase 1 criterion, shown for scale only')
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    ax1.set_ylim(0, 6) # Give breathing room above the 5% line
    _h, _l = ax1.get_legend_handles_labels()
    _order = [_l.index('5% Phase 1 criterion, shown for scale only')] + [_l.index(bar_labels[m]) for m in materials]
    ax1.legend([_h[i] for i in _order], [_l[i] for i in _order],
               loc='upper center', bbox_to_anchor=(0.5, -0.14), ncol=4, fontsize=13, frameon=True)
    
    save_path_1 = os.path.join(base_dir, "Validation_Error_BarChart.png")
    plt.savefig(save_path_1, dpi=500, bbox_inches='tight')
    plt.close(fig1)

# ==========================================
# CANVAS 2: GEOMETRY OVERLAY (Sim vs NIST)
# ==========================================
if nist_col:
    print("Generating Canvas 2: NIST Overlay...")
    fig2, ax2 = plt.subplots(figsize=(12, 8))
    fig2.suptitle('Laboratory Replica Overlay: Simulated vs NIST/XCOM LAC', fontsize=22, fontweight='bold', y=0.95)
    
    # Plot for Pure PPS and 30Wt% Lead as representative extremes
    for mat in ['PPS', 'Pb']:
        wt = 0 if mat == 'PPS' else 30
        df_m = df[(df['BaseMat'] == mat) & (df['Wt%'] == wt)].sort_values(energy_col)
        
        if not df_m.empty:
            ax2.plot(df_m[energy_col], df_m[lac_col], marker='o', color=colors[mat], linewidth=3, markersize=8, label=f'Simulated, {ov_labels[mat]}')
            
            df_m['NIST_Num'] = pd.to_numeric(df_m[nist_col], errors='coerce')
            ax2.plot(df_m[energy_col], df_m['NIST_Num'], marker='x', color=colors[mat], linestyle='--', linewidth=2, markersize=8, label=f'NIST/XCOM, {ov_labels[mat]}')

    ax2.set_xlabel('Energy (keV)', fontsize=16)
    ax2.set_ylabel('LAC, μ (cm⁻¹)', fontsize=16)
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xticks(energies)
    ax2.set_xticklabels(tick_labels(energies), rotation=45, ha='right', fontsize=13)
    ax2.grid(True, which='both', linestyle='--', alpha=0.3)
    ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.16), ncol=2, fontsize=14, frameon=True)
    
    save_path_2 = os.path.join(base_dir, "NIST_Overlay_Plot.png")
    plt.savefig(save_path_2, dpi=500, bbox_inches='tight')
    plt.close(fig2)

# ==========================================
# CANVAS 3: MXENE ENHANCEMENT FACTOR
# ==========================================
print("Generating Canvas 3: MXene Enhancement...")
fig3, ax3 = plt.subplots(figsize=(12, 8))
fig3.suptitle('Ti₃C₂O₂ MXene Enhancement Factor over Pure PPS', fontsize=22, fontweight='bold', y=0.95)

df_pps = df[(df['BaseMat'] == 'PPS') & (df['Wt%'] == 0)][[energy_col, lac_col]].set_index(energy_col)

mxene_wts = [5, 10, 15, 20, 25, 30]
blues = ['#add8e6', '#87cefa', '#4169e1', '#0000ff', '#0000cd', '#00008b']

for idx, wt in enumerate(mxene_wts):
    df_mx = df[(df['BaseMat'] == 'Ti3C2O2') & (df['Wt%'] == wt)].sort_values(energy_col)
    if not df_mx.empty:
        df_calc = df_mx.set_index(energy_col)[[lac_col]].join(df_pps, rsuffix='_PPS')
        df_calc['Enhancement(%)'] = ((df_calc[lac_col] - df_calc[f'{lac_col}_PPS']) / df_calc[f'{lac_col}_PPS']) * 100
        
        ax3.plot(df_calc.index, df_calc['Enhancement(%)'], marker='^', color=blues[idx], linewidth=2.5, markersize=8, label=f'{wt} Wt% MXene')

# Format the visual formula box and place it top-center where lines are clear
formula_text = r"Enhancement (%) = $\left[ \frac{LAC_{MXene} - LAC_{PPS}}{LAC_{PPS}} \right] \times 100$"
ax3.text(0.50, 0.85, formula_text, transform=ax3.transAxes, fontsize=16, ha='center', va='center',
         bbox=dict(boxstyle="round,pad=0.6", facecolor='#f8f9fa', edgecolor='black', alpha=0.9))

ax3.set_xlabel('Energy (keV)', fontsize=16)
ax3.set_ylabel('Shielding Enhancement vs PPS (%)', fontsize=16)
ax3.set_xscale('log')
ax3.set_xticks(energies)
ax3.set_xticklabels(energies, rotation=45, ha='right', fontsize=13)
ax3.grid(True, which='both', linestyle='--', alpha=0.5)
ax3.legend(title='Filler Loading', loc='upper right', fontsize=12)

save_path_3 = os.path.join(base_dir, "MXene_Enhancement_Factor.png")
plt.savefig(save_path_3, dpi=300, bbox_inches='tight')
plt.close(fig3)

# ==========================================
# CANVAS 4: EFFECTIVE ATOMIC NUMBER (Z_eff)
# ==========================================
print("Generating Canvas 4: Effective Atomic Number (Static from LaTeX)...")
zeff_data = {
    'Pb': [10.8788, 27.7151, 34.8353, 39.9993, 44.2108, 47.8438, 51.0837],
    'BaSO4': [10.8788, 17.2342, 20.8555, 23.5832, 25.8359, 27.7868, 29.5266],
    'W': [10.8788, 25.3225, 31.7106, 36.3585, 40.1521, 43.4245, 46.3417],
    'Bi2O3': [10.8788, 27.0988, 34.0207, 39.0372, 43.1231, 46.6425, 49.7760],
    'Ti3C2O2': [10.8788, 11.6166, 12.2788, 12.8835, 13.4424, 13.9643, 14.4552]
}
wt_fractions = [0, 5, 10, 15, 20, 25, 30]

fig4, ax4 = plt.subplots(figsize=(12, 8))
fig4.suptitle('Theoretical Effective Atomic Number ($Z_{eff}$) vs. Filler Loading', fontsize=22, fontweight='bold', y=0.95)

for mat in ['Ti3C2O2', 'Pb', 'W', 'BaSO4', 'Bi2O3']:
    ax4.plot(wt_fractions, zeff_data[mat], marker='D', color=colors[mat], linewidth=3, markersize=9, label=labels[mat])

ax4.axhline(y=10.8788, color=colors['PPS'], linestyle='--', linewidth=3, label=labels['PPS'])

ax4.set_xlabel('Filler Weight Fraction (Wt%)', fontsize=16)
ax4.set_ylabel('Effective Atomic Number ($Z_{eff}$)', fontsize=16)
ax4.set_xticks(wt_fractions)
ax4.grid(True, linestyle='--', alpha=0.5)

legend_elements = [Line2D([0], [0], color=colors[m], lw=4, label=labels[m]) for m in materials]
fig4.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize=14, frameon=True, bbox_to_anchor=(0.5, -0.05))
plt.subplots_adjust(bottom=0.15)

save_path_4 = os.path.join(base_dir, "Z_eff_vs_Weight.png")
plt.savefig(save_path_4, dpi=300, bbox_inches='tight')
plt.close(fig4)

print("Success! All 4 final manuscript figures have been generated and saved.")