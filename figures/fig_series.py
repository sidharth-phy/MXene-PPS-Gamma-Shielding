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
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, 'data', 'phase2', 'Phase2_Master_Dataset.txt')
OUT = sys.argv[2] if len(sys.argv) > 2 else '.'

ENERGIES = [59.5, 356.0, 511.0, 662.0, 1173.0, 1332.0]
LOADINGS = [5, 10, 15, 20, 25, 30]

# filler key, legend label, colour
FILLERS = [('Ti3C2O2', 'Ti$_3$C$_2$O$_2$ MXene', '#0000ff'),
           ('Pb', 'Lead (Pb)', '#000000'),
           ('W', 'Tungsten (W)', '#ff0000'),
           ('BaSO4', 'Barium Sulphate (BaSO$_4$)', '#008000'),
           ('Bi2O3', 'Bismuth Oxide (Bi$_2$O$_3$)', '#800080')]
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
    fig, axes = plt.subplots(2, 4, figsize=(26.0, 15.0))
    fig.suptitle('Linear Attenuation Series at %s keV' % (
        '%.1f' % energy if energy != 59.5 else '59.5'),
        fontsize=34, fontweight='bold', y=0.985)

    panels = [(ax, wt) for ax, wt in zip(axes.flat, LOADINGS)]
    for ax, wt in panels:
        for key, _, colour in FILLERS:
            series = data.get((energy, '%s_%dWt' % (key, wt)), {})
            xs = sorted(series)
            if not xs:
                continue
            ax.plot(xs, [series[x] for x in xs], linestyle='--', marker='o',
                    markersize=11, linewidth=2.0, color=colour)
        ax.set_title('Composites at %d Wt%%' % wt, fontsize=25, pad=14)
        ax.set_xlabel('Thickness (mm)', fontsize=21)
        ax.set_ylabel('ln(I$_0$ / I)', fontsize=21)
        ax.tick_params(labelsize=18)
        ax.grid(True, alpha=0.3)

    ax = axes.flat[len(LOADINGS)]
    series = data.get((energy, 'PPS_0Wt'), {})
    xs = sorted(series)
    ax.plot(xs, [series[x] for x in xs], linestyle='-', marker='o',
            markersize=11, linewidth=2.0, color=PPS_COLOUR)
    ax.set_title('Pure PPS (0 Wt%) Baseline', fontsize=25, pad=14)
    ax.set_xlabel('Thickness (mm)', fontsize=21)
    ax.set_ylabel('ln(I$_0$ / I)', fontsize=21)
    ax.tick_params(labelsize=18)
    ax.grid(True, alpha=0.3)

    legend_ax = axes.flat[len(LOADINGS) + 1]
    legend_ax.axis('off')
    handles = [plt.Line2D([], [], color=c, linestyle='--', marker='o',
                          markersize=11, linewidth=2.0, label=lab)
               for _, lab, c in FILLERS]
    handles.append(plt.Line2D([], [], color=PPS_COLOUR, linestyle='-',
                              marker='o', markersize=11, linewidth=2.0,
                              label='Pure PPS (Baseline)'))
    legend_ax.legend(handles=handles, title='Material Types', loc='center',
                     fontsize=22, title_fontsize=25, frameon=True)

    axes.flat[0].set_position(axes.flat[0].get_position())
    fig.tight_layout(rect=(0, 0, 1, 0.95))
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
