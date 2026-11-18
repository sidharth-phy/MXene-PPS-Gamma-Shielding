# -*- coding: utf-8 -*-
"""Figures 5 to 10: Phase 2 five-point Beer-Lambert series, one figure per energy.

Each panel plots ln(I0/I) against slab thickness for the six composite families
at one filler loading, with a seventh panel for the unfilled matrix. Every point
is computed from the transmitted and reference counts of
data/phase2/Phase2_Master_Dataset.txt. The points are joined for legibility.
No line is fitted: the coefficient reported in the manuscript is the mean of the
five per-thickness values ln(I0/I)/x, as Section 2.8 describes.

Usage:
    python3 figures/fig_series.py [path/to/Phase2_Master_Dataset.txt] [outdir]
"""
import math
import os
import sys
from collections import defaultdict

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

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, 'data', 'phase2', 'Phase2_Master_Dataset.txt')
OUT = sys.argv[2] if len(sys.argv) > 2 else '.'

ENERGIES = [59.5, 356.0, 511.0, 662.0, 1173.0, 1332.0]
LOADINGS = [5, 10, 15, 20, 25, 30]

# filler key, legend label, colour
# filler key, legend label, colour, marker. The marker carries the same
# information as the colour, so the series stay separable in greyscale and
# for readers with a colour vision deficiency.
FILLERS = [('Ti3C2O2', 'Ti$_3$C$_2$O$_2$/PPS', '#0000ff', 's'),
           ('Pb', 'Pb/PPS', '#000000', '^'),
           ('W', 'W/PPS', '#ff0000', 'D'),
           ('BaSO4', 'BaSO$_4$/PPS', '#008000', 'v'),
           ('Bi2O3', 'Bi$_2$O$_3$/PPS', '#800080', 'P')]
PPS_COLOUR = '#ffa500'


def load(path):
    """Return {(energy, material): {thickness_mm: ln(I0/I)}}."""
    out = defaultdict(dict)
    for line in open(path):
        if '|' not in line or 'Energy(keV)' in line:
            continue
        f = [s.strip() for s in line.split('|')]
        if len(f) < 5:
            continue
        try:
            energy = float(f[0])
            thickness = float(f[2])
            i0 = float(f[3])
            i = float(f[4])
        except ValueError:
            continue
        if i <= 0 or thickness <= 0:
            continue
        out[(energy, f[1])][thickness] = math.log(i0 / i)
    return out


def draw(data, energy):
    # No figure-level title inside the artwork: the caption carries both the
    # subject and the energy, and Elsevier asks for the title in the caption.
    # The canvas is also smaller than before, which is what lifts the printed
    # lettering: with a tight bounding box the printed size follows the ratio
    # of font size to canvas, not the font size alone.
    fig, axes = plt.subplots(2, 4, figsize=(10.60, 6.10))

    panels = [(ax, wt) for ax, wt in zip(axes.flat, LOADINGS)]
    for ax, wt in panels:
        for key, _, colour, mk in FILLERS:
            series = data.get((energy, '%s_%dWt' % (key, wt)), {})
            xs = sorted(series)
            if not xs:
                continue
            ax.plot(xs, [series[x] for x in xs], linestyle='--', marker=mk,
                    markersize=7, linewidth=1.6, color=colour)
        # one short line: the caption already says these are the composite
        # families, so the panel only has to say which loading it carries. A
        # two-line title was wider than its cell and reached the legend.
        ax.set_title('(%s) %d wt %%' % ('abcdefg'[panels.index((ax, wt))], wt),
                     fontsize=21, pad=8)
        ax.set_xlabel('Thickness (mm)', fontsize=20)
        ax.set_ylabel('ln(I$_0$ / I)', fontsize=20)
        ax.tick_params(labelsize=18)
        # Ticks on the thicknesses that were run, but only every other one
        # carries a number: at this panel width the labels 8 and 10 came
        # within 1.3 pt of each other, closer than a word space.
        ax.set_xticks([2, 6, 10])
        ax.set_xticks([4, 8], minor=True)
        ax.margins(x=0.08, y=0.10)   # keep end markers off the spines
        ax.grid(True, alpha=0.3)

    ax = axes.flat[len(LOADINGS)]
    series = data.get((energy, 'PPS_0Wt'), {})
    xs = sorted(series)
    ax.plot(xs, [series[x] for x in xs], linestyle='-', marker='o',
            markersize=7, linewidth=1.6, color=PPS_COLOUR)
    ax.set_title('(g) pure PPS', fontsize=21, pad=8)
    ax.set_xlabel('Thickness (mm)', fontsize=20)
    ax.set_ylabel('ln(I$_0$ / I)', fontsize=20)
    ax.tick_params(labelsize=18)
    ax.set_xticks([2, 6, 10])
    ax.set_xticks([4, 8], minor=True)
    ax.margins(x=0.08, y=0.10)
    ax.grid(True, alpha=0.3)

    legend_ax = axes.flat[len(LOADINGS) + 1]
    legend_ax.axis('off')
    handles = [plt.Line2D([], [], color=c, linestyle='--', marker=mk,
                          markersize=7, linewidth=1.6, label=lab)
               for _, lab, c, mk in FILLERS]
    handles.append(plt.Line2D([], [], color=PPS_COLOUR, linestyle='-',
                              marker='o', markersize=7, linewidth=1.6,
                              label='pure PPS'))
    legend_ax.legend(handles=handles, title='Materials', loc='center',
                     fontsize=18, title_fontsize=20, frameon=True,
                     labelspacing=0.45, handlelength=1.6, borderpad=0.45,
                     handletextpad=0.45)

    axes.flat[0].set_position(axes.flat[0].get_position())
    fig.tight_layout()
    return fig


def main():
    data = load(SRC)
    os.makedirs(OUT, exist_ok=True)
    for n, energy in enumerate(ENERGIES, start=5):
        fig = draw(data, energy)
        path = os.path.join(OUT, 'Figure%d_series_%gkeV.png' % (n, energy))
        fig.savefig(path, dpi=300, facecolor='white', bbox_inches='tight')
        plt.close(fig)
        print('wrote', path)


if __name__ == '__main__':
    main()
