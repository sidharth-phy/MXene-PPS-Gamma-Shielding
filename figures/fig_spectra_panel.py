# -*- coding: utf-8 -*-
"""Figure 12 of the manuscript: transmitted spectra at the six energies as one
2x3 panel, read straight from the deposited spectrum CSVs.
Data loading and plotting logic copied verbatim from
figures/superseded/fig_spectra.py.

Usage:
    python3 figures/fig_spectra_panel.py [path/to/spectra_dir] [outfile]
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
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import LogLocator

# Defaults to the deposited spectra and the working directory, as every
# other figure script does and as figures/README.md states. Without them
# running the script on its own raised IndexError.
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
spectra_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, 'data', 'phase2', 'spectra')
out = sys.argv[2] if len(sys.argv) > 2 else 'Figure12.png'

energies = ["59.5", "356", "511", "662", "1173", "1332"]
materials = ['PPS', 'Ti3C2O2', 'Pb', 'W', 'BaSO4', 'Bi2O3']
colors = {'PPS': 'orange', 'Ti3C2O2': 'blue', 'Pb': 'black', 'W': 'red', 'BaSO4': 'green', 'Bi2O3': 'purple'}
# Above 356 keV the six spectra coincide to within a few per cent, so a solid
# line drawn later hides every earlier one completely. Distinct dash patterns
# let all six show through where they overlie, and also separate the series in
# greyscale and for a reader with a colour vision deficiency.
dashes = {'PPS': (None, None), 'Ti3C2O2': (6, 2), 'Pb': (1, 2),
          'W': (5, 2, 1, 2), 'BaSO4': (9, 3), 'Bi2O3': (3, 2, 1, 2)}
labels = {
    'PPS': 'pure PPS (baseline)',
    'Ti3C2O2': 'Ti$_{3}$C$_{2}$O$_{2}$/PPS, 30 wt %',
    'Pb': 'Pb/PPS, 30 wt %',
    'W': 'W/PPS, 30 wt %',
    'BaSO4': 'BaSO$_{4}$/PPS, 30 wt %',
    'Bi2O3': 'Bi$_{2}$O$_{3}$/PPS, 30 wt %',
}

fig, axes = plt.subplots(2, 3, figsize=(11.7, 6.75))
for k, energy in enumerate(energies):
    ax = axes[k // 3][k % 3]
    energy_filename = energy.replace(".", "p")
    for mat in materials:
        fname = f"spec_{mat}{'0' if mat=='PPS' else '30'}Wt_10mm_{energy_filename}keV.csv"
        fpath = os.path.join(spectra_dir, fname)
        if not os.path.exists(fpath):
            print('  [MISSING]', fname); continue
        df = pd.read_csv(fpath, comment='#', header=None, sep=r'\s+|,', engine='python')
        x = pd.to_numeric(df.iloc[:, 0]); y = pd.to_numeric(df.iloc[:, 1])
        # No fill under the steps: six fills at 5 % tint stack into a flat
        # grey that an offset press cannot hold and that hides the traces.
        _d = dashes[mat]
        _ln, = ax.plot(x, y, drawstyle='steps-mid', color=colors[mat],
                       linewidth=1.3, alpha=0.95)
        if _d[0] is not None:
            _ln.set_dashes(_d)
    ax.set_yscale('log')
    ax.set_ylim(bottom=10)
    e_val = float(energy)
    ax.set_xlim(e_val - 50 if e_val > 50 else 0, e_val + 50)
    # Major grid only. With which="both" the log y axis draws every minor
    # line when a panel spans few decades and thins them out when it spans
    # many, so the 1173 and 1332 keV panels came out four times as heavily
    # ruled as the rest and read as striped.
    ax.grid(True, which="major", ls="-", alpha=0.25)
    ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=6))
    ax.tick_params(labelsize=16)
    ax.set_title(f'({"abcdef"[k]}) {energy} keV', fontsize=22,
                 fontweight='bold', pad=8)

# the channel width belongs on the axis: counts alone do not say what a
# point on this ordinate means
fig.supylabel('Transmitted photon counts per 1 keV channel', fontsize=20)
handles = []
for m in materials:
    _h = Line2D([0], [0], color=colors[m], lw=2.2, label=labels[m])
    if dashes[m][0] is not None:
        _h.set_dashes(dashes[m])
    handles.append(_h)
fig.tight_layout(rect=[0.015, 0.20, 1, 1])
fig.supxlabel('Energy (keV)', fontsize=20, y=0.165)
fig.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.5, 0.0),
           ncol=3, fontsize=18, frameon=True)
fig.savefig(out, dpi=400, bbox_inches='tight', facecolor='white')
from PIL import Image
print('written', out, Image.open(out).size)
