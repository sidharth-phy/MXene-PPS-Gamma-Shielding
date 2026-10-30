# -*- coding: utf-8 -*-
"""Figures 13 to 18 of the manuscript, one per photon energy.

Transmitted NaI(Tl) spectra for pure PPS and the five 30 wt % composites at 10 mm
thickness, plotted from the 1 keV-per-bin histograms in data/phase2/spectra/. Each
histogram is the raw run-time output of phase2-digital-twin/src/RunAction.cc.

Usage:
    python3 figures/fig_spectra.py [path/to/spectra/] [outdir]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

spectra_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, 'data', 'phase2', 'spectra')
base_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
os.makedirs(base_dir, exist_ok=True)

# Define the energies based on your folders
energies = ["59.5", "356", "511", "662", "1173", "1332"]

# Define materials and their specific plotting styles
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

# ==========================================
# 2. THE MASTER PLOTTING LOOP
# ==========================================
for energy in energies:
    # Handle folder naming (59.5 keV folder vs filename 59p5)
    energy_folder = energy
    energy_filename = energy.replace(".", "p")
    
    current_folder = os.path.join(spectra_dir, energy_folder)
    if not os.path.isdir(current_folder):
        current_folder = spectra_dir
    if not os.path.exists(current_folder):
        print(f"Skipping {energy} keV: spectra directory not found.")
        continue

    print(f"Processing Spectra for {energy} keV...")

    # Create Figure
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Track if we actually plotted anything
    plotted_count = 0

    for mat in materials:
        # Construct the filename based on your screenshot pattern
        # e.g., spec_Pb30Wt_10mm_59p5keV.csv
        fname = f"spec_{mat}{'0' if mat=='PPS' else '30'}Wt_10mm_{energy_filename}keV.csv"
        
        # Check for the MXene specific suffix if needed (like the _2 we saw earlier)
        # We try the standard name first, then look for variations
        fpath = os.path.join(current_folder, fname)
        
        if not os.path.exists(fpath):
            # Try to find any file that starts with the material and ends with energy
            potential_files = [f for f in os.listdir(current_folder) if f.startswith(f"spec_{mat}") and energy_filename in f]
            if potential_files:
                fpath = os.path.join(current_folder, potential_files[0])
            else:
                print(f"  [MISSING] {mat} in {energy} keV folder")
                continue

        try:
            # Read Geant4 CSV (ignore '#' headers)
            df = pd.read_csv(fpath, comment='#', header=None, sep=r'\s+|,', engine='python')
            x = pd.to_numeric(df.iloc[:, 0])
            y = pd.to_numeric(df.iloc[:, 1])

            # Scientific Plotting: Step-mid style
            ax.plot(x, y, drawstyle='steps-mid', color=colors[mat], linewidth=2.0, alpha=0.9)
            ax.fill_between(x, y, step="mid", color=colors[mat], alpha=0.05)
            plotted_count += 1
            
        except Exception as e:
            print(f"  [ERROR] Could not plot {mat}: {e}")

    # ==========================================
    # 3. SCIENTIFIC FORMATTING PER ENERGY
    # ==========================================
    ax.set_title(f'Transmitted Gamma Ray Spectra ({energy} keV Source)', fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel('Energy (keV)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Transmitted Photon Counts (Log Scale)', fontsize=14, fontweight='bold')
    
    # 1. Logarithmic Scale to show suppression clearly
    ax.set_yscale('log')
    
    # 2. Filter out "Fuzz" (noise below 10-100 counts)
    ax.set_ylim(bottom=10) 
    
    # 3. Smart Zoom (X-Axis) based on peak position
    e_val = float(energy)
    ax.set_xlim(e_val - 50 if e_val > 50 else 0, e_val + 50)

    # 4. Grid and Legend
    ax.grid(True, which="both", ls="-", alpha=0.2)
    legend_elements = [Line2D([0], [0], color=colors[m], lw=3, label=labels[m]) for m in materials]
    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.13),
              ncol=3, fontsize=12, frameon=True)

    # Save High-Res Image
    output_name = f"Final_Plot_{energy_filename}keV.png"
    plt.savefig(os.path.join(base_dir, output_name), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [SUCCESS] Created {output_name}\n")

print("All plots generated successfully in your main folder!")