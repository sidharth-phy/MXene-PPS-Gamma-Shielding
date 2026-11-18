# -*- coding: utf-8 -*-
"""Figure 15 of the manuscript: two panels on one canvas.

(a) theoretical effective atomic number against filler weight fraction,
(b) MXene enhancement factor against photon energy for loadings 5 to 30 wt %.

The data, every plotted value, colour, scale and label are copied unchanged
from fig_summary.py, which drew these as two separate figures. Only the layout
differs: one canvas, two panels.

Usage:
    python3 figures/fig_zeff_ef_panel.py [path/to/Phase2_Data_Validated.txt] [outfile]
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
import pandas as pd
from matplotlib.lines import Line2D

filepath = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, 'data', 'phase2', 'Phase2_Data_Validated.txt')
out = sys.argv[2] if len(sys.argv) > 2 else 'Figure15.png'

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
df = df.dropna(subset=[energy_col, lac_col])

def get_base_mat(m):
    m = str(m)
    return 'PPS' if 'PPS_0Wt' in m else m.split('_')[0]

def get_wt(m):
    m = str(m)
    if 'PPS_0Wt' in m: return 0
    try: return int(m.split('_')[1].replace('Wt', ''))
    except Exception: return -1

df['BaseMat'] = df[mat_col].apply(get_base_mat)
df['Wt%'] = df[mat_col].apply(get_wt)
df = df[df['Wt%'] >= 0].copy()
energies = sorted(df[energy_col].unique())

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
# the six loadings are a ramp of one hue, which collapses in greyscale;
# a distinct marker per loading keeps them separable
ramp = ['o', 's', '^', 'D', 'v', 'P']

zeff_data = {
    'Pb':      [10.8788, 27.7151, 34.8353, 39.9993, 44.2108, 47.8438, 51.0837],
    'BaSO4':   [10.8788, 17.2342, 20.8555, 23.5832, 25.8359, 27.7868, 29.5266],
    'W':       [10.8788, 25.3225, 31.7106, 36.3585, 40.1521, 43.4245, 46.3417],
    'Bi2O3':   [10.8788, 27.0988, 34.0207, 39.0372, 43.1231, 46.6425, 49.7760],
    'Ti3C2O2': [10.8788, 11.6166, 12.2788, 12.8835, 13.4424, 13.9643, 14.4552],
}
wt_fractions = [0, 5, 10, 15, 20, 25, 30]

# Canvas sized so that the chemical subscripts, which matplotlib sets at
# 0.7 of the surrounding size, still clear 6 pt at the width this figure
# is printed. With a tight bounding box the printed size follows the
# ratio of font size to canvas, so the drawing area sets it.
fig, (axA, axB) = plt.subplots(1, 2, figsize=(8.79, 4.33))
fig.subplots_adjust(left=0.115, right=0.975, top=0.73, bottom=0.46, wspace=0.36)
TS, LS, TK = 13, 14, 12


def _elab(es):
    """Energy tick labels. 1173 and 1332 keV are 0.056 decades apart, which is
    narrower than the labels themselves on a logarithmic axis, so the second of
    the pair is dropped to a lower line instead of being overprinted."""
    out = []
    for e in es:
        t = '%g' % e
        out.append('\n' + t if abs(float(e) - 1332.0) < 1e-6 else t)
    return out


# ---- (a) effective atomic number ----
axA.set_title('(a) Effective Atomic Number ($Z_{eff}$)',
              fontsize=TS, fontweight='bold', pad=42)
for mat in ['Ti3C2O2', 'Pb', 'W', 'BaSO4', 'Bi2O3']:
    axA.plot(wt_fractions, zeff_data[mat], marker=markers[mat], color=colors[mat],
             linewidth=2.0, markersize=7)
axA.axhline(y=10.8788, color=colors['PPS'], linestyle='--', linewidth=2.0)
axA.set_xlabel('Filler weight fraction (wt %)', fontsize=LS)
axA.set_ylabel('Effective atomic number', fontsize=LS)
axA.set_xticks(wt_fractions)
axA.tick_params(labelsize=TK)
axA.grid(True, linestyle='--', alpha=0.5)

# ---- (b) MXene enhancement factor ----
axB.set_title('(b) Ti$_{3}$C$_{2}$O$_{2}$ Enhancement over PPS',
              fontsize=TS, fontweight='bold', pad=42)
df_pps = df[(df['BaseMat'] == 'PPS') & (df['Wt%'] == 0)][[energy_col, lac_col]].set_index(energy_col)
mxene_wts = [5, 10, 15, 20, 25, 30]
blues = ['#add8e6', '#87cefa', '#4169e1', '#0000ff', '#0000cd', '#00008b']
for idx, wt in enumerate(mxene_wts):
    df_mx = df[(df['BaseMat'] == 'Ti3C2O2') & (df['Wt%'] == wt)].sort_values(energy_col)
    if not df_mx.empty:
        df_calc = df_mx.set_index(energy_col)[[lac_col]].join(df_pps, rsuffix='_PPS')
        df_calc['Enhancement(%)'] = ((df_calc[lac_col] - df_calc[f'{lac_col}_PPS'])
                                     / df_calc[f'{lac_col}_PPS']) * 100
        # open markers: filled markers of these shapes name the five filler
        # families everywhere else in the paper, so a filled blue square here
        # could be read as Ti3C2O2 rather than as a loading
        axB.plot(df_calc.index, df_calc['Enhancement(%)'], marker=ramp[idx], color=blues[idx],
                 linewidth=2.0, markersize=6, markerfacecolor='white',
                 markeredgewidth=1.4, label=f'{wt}')
# Written on one line rather than as a built-up fraction: a numerator with a
# subscript nests two levels of mathtext shrinking and the subscripts end up
# below the 7 pt floor once the figure is placed at its printed width.
# Two short lines rather than one long one, and mu in place of the spelled
# out LAC, so the box clears the legend and the curves at the printed width.
formula_text = ("Enhancement (%) =\n"
                r"100 ($\mu - \mu_{PPS}$) / $\mu_{PPS}$")
# With the loading key moved out of the axes, the upper right of panel (b)
# is clear above about 30 %, so the definition sits there and the two keys
# below get the whole width between them.
# The definition sits on the axis it defines. Set as a box inside panel
# (b) it covered part of a descending curve wherever it was placed, and
# the key row below has no width left for it.
axB.set_xlabel('Energy (keV)', fontsize=LS)
axB.set_ylabel('Enhancement vs PPS (%)\n'
                r'100 ($\mu - \mu_{PPS}$) / $\mu_{PPS}$',
                fontsize=LS, linespacing=1.5)
axB.set_xscale('log')
axB.set_xticks(energies)
axB.set_xticklabels(_elab(energies), rotation=45, ha='right', fontsize=TK)
axB.tick_params(axis='y', labelsize=TK)
axB.grid(True, which='both', linestyle='--', alpha=0.5)
# Both keys live in the band below the panels. Six legible entries cover
# the curves wherever they are placed inside panel (b), and the panel is
# narrow enough that an in-axes key leaves no clear space.
_bh, _bl = axB.get_legend_handles_labels()
fig.legend(_bh, _bl, title='Panel (b): filler loading (wt %)',
           loc='lower center', bbox_to_anchor=(0.735, 0.008), ncol=3,
           fontsize=12, title_fontsize=12, columnspacing=1.0,
           handlelength=1.4, handletextpad=0.5, borderpad=0.4,
           frameon=True)

# Panel letters are set at the head of each panel title, the one rule used
# across every figure in this paper. A letter placed outside the axes has
# to be positioned against a title whose height and width change with the
# text, and it does not scale down to the small panels of Figures 5 to 10.

handles = [Line2D([0], [0], color=colors[m], lw=2.2,
                  marker=('' if m == 'PPS' else markers[m]), markersize=7,
                  linestyle=('--' if m == 'PPS' else '-'),
                  label=labels[m]) for m in materials]
fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.265, 0.008),
           ncol=2, fontsize=12, frameon=True,
           title='Panel (a): materials', title_fontsize=12)

fig.savefig(out, dpi=400, facecolor='white')
from PIL import Image
print('written', out, Image.open(out).size)
