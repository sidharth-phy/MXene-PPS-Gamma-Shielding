# -*- coding: utf-8 -*-
"""Figure 14 of the manuscript: three panels on one canvas.

(a) mass attenuation coefficient against photon energy on logarithmic axes,
(b) half-value layer against photon energy, (c) radiation protection efficiency
at 10 mm panel thickness. All for pure PPS and the five 30 wt % composites.

The data pipeline and every plotted value, colour, scale, limit and label are
copied unchanged from fig_hvl_rpe.py, which drew the same three plots as three
separate figures. Only the layout differs: one canvas, one shared legend.

Usage:
    python3 figures/fig_merit_panel.py [path/to/Phase2_Data_Validated.txt] [outfile]
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


def panel_letters(fig, pairs, fontsize, min_title=None, level=True):
    """Put (a), (b), ... on the same line as each panel title, clear of its
    left edge. The title is centred on its axes and overhangs when it is wider
    than the axes, so the gap is measured from the title actually drawn rather
    than assumed: a letter at a fixed offset inside the axes ends up underneath
    a wide title. If a title leaves no room, it is stepped down a point at a
    time until it does."""
    need = 0.030 + fontsize / 1400.0          # letter width plus a gap
    for ax, _ in pairs:
        while True:
            fig.canvas.draw()
            bb = ax.title.get_window_extent(
                fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
            size = ax.title.get_fontsize()
            if bb.x0 >= need or min_title is None or size <= min_title:
                break
            ax.title.set_fontsize(size - 1)
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    inv = fig.transFigure.inverted()
    for ax, lab in pairs:
        bb = ax.title.get_window_extent(rend).transformed(inv)
        if level:
            # on the title's own line, clear of its left edge
            fig.text(max(0.004, bb.x0 - 0.014), 0.5 * (bb.y0 + bb.y1), lab,
                     fontsize=fontsize, fontweight='bold',
                     ha='right' if bb.x0 - 0.014 > 0.02 else 'left', va='center')
        else:
            # above the title: used where a title is wider than its panel and
            # would otherwise reach the next panel's letter
            pos = ax.get_position()
            fig.text(max(0.004, pos.x0 - 0.02), bb.y1 + 0.004, lab,
                     fontsize=fontsize, fontweight='bold', ha='left',
                     va='bottom')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.gridspec import GridSpec

filepath = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, 'data', 'phase2', 'Phase2_Data_Validated.txt')
out = sys.argv[2] if len(sys.argv) > 2 else 'Figure14.png'

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

df_top['HVL(cm)'] = np.log(2) / df_top['AvgLinAttCoeff(cm-1)']
df_top['RPE(%)'] = (1 - np.exp(-df_top['AvgLinAttCoeff(cm-1)'] * 1.0)) * 100

exact_latex_densities = {
    'PPS': 1.3500,
    'Ti3C2O2': 1.7432,
    'Pb': 1.8350,
    'W': 1.8723,
    'BaSO4': 1.7089,
    'Bi2O3': 1.8109,
}
df_top['Density(g/cm3)'] = df_top['BaseMat'].map(exact_latex_densities)
df_top['MAC(cm2/g)'] = df_top['AvgLinAttCoeff(cm-1)'] / df_top['Density(g/cm3)']

energies = sorted(df_top['Energy(keV)'].unique())
materials = ['PPS', 'Ti3C2O2', 'Pb', 'W', 'BaSO4', 'Bi2O3']
colors = {'PPS': 'orange', 'Ti3C2O2': 'blue', 'Pb': 'black',
          'W': 'red', 'BaSO4': 'green', 'Bi2O3': 'purple'}
labels = {
    'PPS': 'pure PPS (baseline)',
    'Ti3C2O2': 'Ti$_{3}$C$_{2}$O$_{2}$/PPS',
    'Pb': 'Pb/PPS',
    'W': 'W/PPS',
    'BaSO4': 'BaSO$_{4}$/PPS',
    'Bi2O3': 'Bi$_{2}$O$_{3}$/PPS',
}
markers = {'PPS': 'o', 'Ti3C2O2': 's', 'Pb': '^', 'W': 'D',
           'BaSO4': 'v', 'Bi2O3': 'P'}
# hatch as well as colour, so the bar groups of panel (c) survive greyscale
# printing and red-green colour vision deficiency
hatches = {'PPS': '', 'Ti3C2O2': '///', 'Pb': 'xxx', 'W': '...',
           'BaSO4': '\\\\\\', 'Bi2O3': '+++'}

fig = plt.figure(figsize=(9.95, 8.72))
gs = GridSpec(2, 2, figure=fig, height_ratios=[1.0, 1.0],
              hspace=0.78, wspace=0.30,
              left=0.082, right=0.985, top=0.885, bottom=0.235)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[1, :])

TS, LS, TK = 15, 15, 12


def _elab(es):
    """Energy tick labels. 1173 and 1332 keV are 0.056 decades apart, which is
    narrower than the labels themselves on a logarithmic axis, so the second of
    the pair is dropped to a lower line instead of being overprinted."""
    out = []
    for e in es:
        t = '%g' % e
        out.append('\n' + t if abs(float(e) - 1332.0) < 1e-6 else t)
    return out

from matplotlib.ticker import LogLocator, FuncFormatter

# ---- (a) MAC against energy ----
ax1.set_title('(a) Mass Attenuation Coefficient (MAC)\nfor 30 wt % composites',
              fontsize=TS, fontweight='bold', pad=10)
for mat in materials:
    df_m = df_top[df_top['BaseMat'] == mat].sort_values('Energy(keV)')
    if not df_m.empty:
        ax1.plot(df_m['Energy(keV)'], df_m['MAC(cm2/g)'], marker=markers[mat],
                 color=colors[mat], linewidth=2.0, markersize=7)
ax1.set_xlabel('Energy (keV)', fontsize=LS)
ax1.set_ylabel('MAC, μ/ρ (cm²/g)', fontsize=LS)
ax1.set_xscale('log'); ax1.set_yscale('log')
ax1.set_xticks(energies)
ax1.set_xticklabels(_elab(energies), rotation=45, ha='right', fontsize=TK)
ax1.tick_params(axis='y', labelsize=TK)
ax1.grid(True, which='both', linestyle='--', alpha=0.3)

# ---- (b) HVL against energy ----
ax2.set_title('(b) Half-Value Layer (HVL)\nfor 30 wt % composites',
              fontsize=TS, fontweight='bold', pad=10)
for mat in materials:
    df_m = df_top[df_top['BaseMat'] == mat].sort_values('Energy(keV)')
    if not df_m.empty:
        ax2.plot(df_m['Energy(keV)'], df_m['HVL(cm)'], marker=markers[mat],
                 color=colors[mat], linewidth=2.0, markersize=7)
ax2.set_xlabel('Energy (keV)', fontsize=LS)
ax2.set_ylabel('HVL (cm)', fontsize=LS)
ax2.set_xscale('log'); ax2.set_yscale('log')
ax2.set_xticks(energies)
ax2.set_xticklabels(_elab(energies), rotation=45, ha='right', fontsize=TK)
# four of the six series sit below 1 cm at 59.5 keV, so the decade labels
# alone leave them unreadable; label the 2/3/5 minor ticks as well
ax2.yaxis.set_minor_locator(LogLocator(base=10.0, subs=(2.0, 3.0, 5.0), numticks=20))
ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, p: ('%g' % v)))
ax2.yaxis.set_minor_formatter(FuncFormatter(lambda v, p: ('%g' % v)))
ax2.tick_params(axis='y', which='minor', labelsize=TK)
ax2.tick_params(axis='y', labelsize=TK)
ax2.grid(True, which='both', linestyle='--', alpha=0.3)

# ---- (c) RPE at 10 mm ----
ax3.set_title('(c) Radiation Protection Efficiency (RPE)\nat 10 mm thickness, 30 wt % composites',
              fontsize=TS, fontweight='bold', pad=10)
x_indexes = np.arange(len(energies))
bar_width = 0.14
for i, mat in enumerate(materials):
    df_m = df_top[df_top['BaseMat'] == mat].sort_values('Energy(keV)')
    rpe_values = []
    for e in energies:
        val = df_m[df_m['Energy(keV)'] == e]['RPE(%)'].values
        rpe_values.append(val[0] if len(val) > 0 else 0)
    ax3.bar(x_indexes + (i - 2.5) * bar_width, rpe_values, width=bar_width,
            color=colors[mat], edgecolor='white', hatch=hatches[mat],
            linewidth=0.5)
ax3.set_xlabel('Energy (keV)', fontsize=LS)
ax3.set_ylabel('RPE (%)', fontsize=LS)
ax3.set_xticks(x_indexes)
# panel (c) is a categorical axis with even spacing, so the pair needs no
# dropped line and a staggered row would read as a mistake
ax3.set_xticklabels(['%g' % e for e in energies], rotation=45, ha='right',
                    fontsize=TK)
ax3.tick_params(axis='y', labelsize=TK)
# axes.axisbelow defaults to 'line', which rules the grid across bars and
# their hatching; True puts it behind the data
ax3.set_axisbelow(True)
ax3.grid(axis='y', linestyle='--', alpha=0.5)
ax3.set_ylim(0, 105)

# Panel letters are set at the head of each panel title, the one rule used
# across every figure in this paper. A letter placed outside the axes has
# to be positioned against a title whose height and width change with the
# text, and it does not scale down to the small panels of Figures 5 to 10.

# Each key shows both the line-and-marker used in panels (a) and (b) and the
# hatched swatch used in panel (c), so one legend serves all three.
from matplotlib.patches import Patch
from matplotlib.legend_handler import HandlerTuple
handles = [(Patch(facecolor=colors[m], edgecolor='white', hatch=hatches[m],
                  linewidth=0.5),
            Line2D([0], [0], color=colors[m], lw=2.2, marker=markers[m],
                   markersize=7))
           for m in materials]
fig.legend(handles=handles, labels=[labels[m] for m in materials],
           loc='lower center', bbox_to_anchor=(0.5, 0.002), ncol=3,
           fontsize=14, frameon=True, handlelength=3.4, handletextpad=0.7,
           handler_map={tuple: HandlerTuple(ndivide=None, pad=0.4)})

fig.savefig(out, dpi=400, facecolor='white')
from PIL import Image
print('written', out, Image.open(out).size)
