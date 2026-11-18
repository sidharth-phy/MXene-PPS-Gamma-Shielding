# -*- coding: utf-8 -*-
"""Figure 11 of the manuscript: two panels on one canvas.

(a) laboratory replica overlay against NIST/XCOM, (b) mean absolute deviation
from NIST/XCOM. Panel (b) averages the five per-thickness deviations of the
LAC_%err column within each material and energy, so each bar is a mean of
per-thickness deviations, not the deviation of the averaged coefficient.
Data handling and plotting copied verbatim from figures/superseded/fig_summary.py
canvases 2 and 1.

Usage:
    python3 figures/fig_overlay_dev_stack.py [path/to/Phase2_Data_Validated.txt] [outfile]
"""
import os, sys
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

# Defaults to the deposited dataset and the working directory, as every
# other figure script does and as figures/README.md states. Without them
# running the script on its own raised IndexError.
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
filepath = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, 'data', 'phase2', 'Phase2_Data_Validated.txt')
out = sys.argv[2] if len(sys.argv) > 2 else 'Figure11.png'
lines = open(filepath, encoding='utf-8').readlines()
header_idx = next(i for i, l in enumerate(lines) if l.startswith('Energy(keV)'))
df = pd.read_csv(filepath, sep='|', skiprows=header_idx, skipinitialspace=True)
df.columns = [str(c).strip() for c in df.columns]
df = df[[c for c in df.columns if not c.startswith('Unnamed')]]
df = df[df['Material'].notna()]
df = df[~df['Material'].astype(str).str.contains('---', na=False)].reset_index(drop=True)
for c in df.columns:
    if c != 'Material':
        df[c] = pd.to_numeric(df[c], errors='coerce')
df['Material'] = df['Material'].astype(str).str.strip()

energy_col, mat_col = 'Energy(keV)', 'Material'
lac_col = next(c for c in df.columns if 'AvgLinAttCoeff' in c)
nist_col = next(c for c in df.columns if 'NIST_LAC' in c)
err_col = next(c for c in df.columns if 'LAC_%err' in c)
df[energy_col] = pd.to_numeric(df[energy_col], errors='coerce')
df[lac_col] = pd.to_numeric(df[lac_col], errors='coerce')
df = df.dropna(subset=[energy_col, lac_col])

def get_base_mat(m):
    m = str(m)
    return 'PPS' if 'PPS_0Wt' in m else m.split('_')[0]
def get_wt(m):
    m = str(m)
    if 'PPS_0Wt' in m: return 0
    try: return int(m.split('_')[1].replace('Wt', ''))
    except: return -1
df['BaseMat'] = df[mat_col].apply(get_base_mat)
df['Wt%'] = df[mat_col].apply(get_wt)
df = df[df['Wt%'] >= 0].copy()
energies = sorted(df[energy_col].unique())

materials = ['PPS', 'Ti3C2O2', 'Pb', 'W', 'BaSO4', 'Bi2O3']
colors = {'PPS': 'orange', 'Ti3C2O2': 'blue', 'Pb': 'black', 'W': 'red', 'BaSO4': 'green', 'Bi2O3': 'purple'}
bar_labels = {'PPS': 'pure PPS', 'Ti3C2O2': 'Ti$_{3}$C$_{2}$O$_{2}$/PPS', 'Pb': 'Pb/PPS',
              'W': 'W/PPS', 'BaSO4': 'BaSO$_{4}$/PPS', 'Bi2O3': 'Bi$_{2}$O$_{3}$/PPS'}
# short forms: these four entries set the width of the whole figure, and
# the printed size of every letter on it follows from that width
ov_labels = {'PPS': 'pure PPS', 'Pb': 'Pb/PPS, 30 wt %'}
# Hatch as well as colour: printed in greyscale, or read by someone with a
# red-green colour vision deficiency, the six bar colours are not separable.
hatches = {'PPS': '', 'Ti3C2O2': '///', 'Pb': 'xxx', 'W': '...',
           'BaSO4': '\\\\\\', 'Bi2O3': '+++'}
def tick_labels(es):
    """1173 and 1332 keV are too close on a log axis to sit on one line."""
    return ['\n%g' % e if abs(float(e) - 1332.0) < 1e-6 else '%g' % e
            for e in es]

# The canvas is deliberately smaller than the type: with a tight bounding
# box the printed size of the lettering is set by the ratio of font size
# to canvas, so shrinking the drawing area is what lifts the lettering
# clear of the 7 pt floor at the width this figure is printed.
fig, (ax2, ax1) = plt.subplots(2, 1, figsize=(8.89, 10.26))

# ---- (a) overlay, from canvas 2 ----
# short panel titles: the caption carries the full description, and at
# full length this title set the width of the figure and so the printed
# size of every letter on it
ax2.set_title('(a) Laboratory Replica Overlay', fontsize=22, fontweight='bold', pad=26)
for mat in ['PPS', 'Pb']:
    wt = 0 if mat == 'PPS' else 30
    df_m = df[(df['BaseMat'] == mat) & (df['Wt%'] == wt)].sort_values(energy_col)
    if not df_m.empty:
        ax2.plot(df_m[energy_col], df_m[lac_col], marker='o', color=colors[mat], linewidth=3,
                 markersize=8, label=f'Simulated, {ov_labels[mat]}')
        df_m = df_m.copy()
        df_m['NIST_Num'] = pd.to_numeric(df_m[nist_col], errors='coerce')
        ax2.plot(df_m[energy_col], df_m['NIST_Num'], marker='x', color=colors[mat], linestyle='--',
                 linewidth=2, markersize=8, label=f'NIST/XCOM, {ov_labels[mat]}')
ax2.set_xlabel('Energy (keV)', fontsize=16)
ax2.set_ylabel('LAC, μ (cm⁻¹)', fontsize=16)
ax2.set_xscale('log'); ax2.set_yscale('log')
ax2.set_xticks(energies)
ax2.set_xticklabels(tick_labels(energies), rotation=45, ha='right', fontsize=16)
ax2.tick_params(axis='y', labelsize=15)
ax2.grid(True, which='both', linestyle='--', alpha=0.3)
# headroom at the top: autoscaled, the 59.5 keV Pb/PPS marker sat on the
# frame and the arms of its NIST cross were cut by it
_lo, _hi = ax2.get_ylim()
ax2.set_ylim(_lo, _hi * 1.55)
# set close under panel (a): at -0.72 the box sat nearer to panel (b)'s
# title than to the panel it belongs to
ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.62), ncol=2, fontsize=16, frameon=True)

# ---- (b) deviation, from canvas 1 ----
ax1.set_title('(b) Mean Absolute Deviation from NIST/XCOM', fontsize=22, fontweight='bold', pad=26)
df['Error_Numeric'] = pd.to_numeric(df[err_col], errors='coerce').abs()
df_top = df[df['Wt%'].isin([0, 30])].copy()
x_indexes = np.arange(len(energies)); bar_width = 0.14
for i, mat in enumerate(materials):
    df_m = df_top[df_top['BaseMat'] == mat].sort_values(energy_col)
    err_values = [df_m[df_m[energy_col] == e]['Error_Numeric'].mean()
                  if not df_m[df_m[energy_col] == e].empty else 0 for e in energies]
    ax1.bar(x_indexes + (i - 2.5) * bar_width, err_values, width=bar_width,
            color=colors[mat], edgecolor='white', label=bar_labels[mat],
            hatch=hatches[mat], linewidth=0.5)
ax1.set_xlabel('Energy (keV)', fontsize=16)
ax1.set_ylabel('Deviation (%)', fontsize=16)   # panel title names the reference
ax1.set_xticks(x_indexes)
ax1.set_xticklabels(tick_labels(energies), rotation=45, ha='right', fontsize=16)
ax1.tick_params(axis='y', labelsize=15)
# the criterion is named on the line itself rather than in the legend: as a
# seventh entry it forced a ragged row and widened the whole figure, which
# shrinks every letter on it once the figure is placed on the page
ax1.axhline(y=5, color='red', linestyle='--', alpha=0.7)
ax1.text(-0.42, 5.14, '5 % Phase 1 criterion, shown for scale only',
         fontsize=16, color='red', ha='left', va='bottom')
# matplotlib's axes.axisbelow default is 'line', which puts grid lines below
# lines but ABOVE patches, so the y grid was ruled across the bars and their
# hatching. True puts the grid behind everything.
ax1.set_axisbelow(True)
ax1.grid(axis='y', linestyle='--', alpha=0.5)
ax1.set_ylim(0, 6)
_h, _l = ax1.get_legend_handles_labels()
_order = [_l.index(bar_labels[m]) for m in materials]
ax1.legend([_h[i] for i in _order], [_l[i] for i in _order],
           loc='upper center', bbox_to_anchor=(0.5, -0.62), ncol=3, fontsize=16, frameon=True)

fig.subplots_adjust(hspace=1.55, left=0.165, right=0.97, top=0.88, bottom=0.30)
# Panel letters are set at the head of each panel title, the one rule used
# across every figure in this paper. A letter placed outside the axes has
# to be positioned against a title whose height and width change with the
# text, and it does not scale down to the small panels of Figures 5 to 10.
fig.savefig(out, dpi=400, bbox_inches='tight', facecolor='white')
from PIL import Image
print('written', out, Image.open(out).size)
