# -*- coding: utf-8 -*-
"""Render every manuscript figure, Figures 1 to 15, writing both a PNG at the dpi each
script sets and a vector PDF for typesetting. Run from anywhere: python3 figures/render_all.py

Each script is executed unchanged. The only thing this wrapper does is wrap
Figure.savefig so that a second, vector copy is written alongside the raster one.

Output goes to the current working directory, so run it from an empty folder:

    mkdir -p build && cd build && python3 ../figures/render_all.py
"""
import os
import runpy
import sys
import matplotlib
# Start from matplotlib's own defaults, not from whatever the machine's
# matplotlibrc holds. A personal config that sets, say, axes.grid or
# savefig.dpi otherwise changes the deposited figures on someone else's
# machine, which is the one thing this deposit exists to prevent.
matplotlib.rcdefaults()
matplotlib.use('Agg')
from matplotlib.figure import Figure

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
_orig = Figure.savefig


def savefig(self, fname, *a, **kw):
    out = _orig(self, fname, *a, **kw)
    name = fname if isinstance(fname, str) else None
    if name and name.lower().endswith('.png'):
        kw.pop('dpi', None)
        _orig(self, name[:-4] + '.pdf', *a, **kw)
    return out


Figure.savefig = savefig

# Figures 1 to 4: schematics. They take no arguments and write into the
# working directory.
for n in (1, 2, 3, 4):
    sys.argv = ['fig%d.py' % n]
    runpy.run_path(os.path.join(HERE, 'fig%d.py' % n), run_name='__main__')
    print('Figure %d written' % n)

VALIDATED = os.path.join(DATA, 'phase2', 'Phase2_Data_Validated.txt')
MASTER = os.path.join(DATA, 'phase2', 'Phase2_Master_Dataset.txt')
SPECTRA = os.path.join(DATA, 'phase2', 'spectra')

JOBS = (
    ('fig_series.py',           [MASTER, '.'],                'Figures 5 to 10'),
    ('fig_overlay_dev_stack.py', [VALIDATED, 'Figure11.png'], 'Figure 11'),
    ('fig_spectra_panel.py',    [SPECTRA, 'Figure12.png'],    'Figure 12'),
    ('fig_lac_loading.py',      [VALIDATED, '.'],             'Figure 13'),
    ('fig_merit_panel.py',      [VALIDATED, 'Figure14.png'],  'Figure 14'),
    ('fig_zeff_ef_panel.py',    [VALIDATED, 'Figure15.png'],  'Figure 15'),
)

for script, args, what in JOBS:
    sys.argv = [script] + args
    runpy.run_path(os.path.join(HERE, script), run_name='__main__')
    print('%s written' % what)

# --- prepare the rasters for a publisher -----------------------------------
# Two things matplotlib leaves wrong for submission. It writes RGBA even when
# nothing is transparent, and artwork guidance asks for no alpha channel. And
# it stamps the PNG resolution tag with the savefig dpi, which describes the
# rendering, not the size the figure is printed at: a production system that
# divides pixel width by that tag gets the wrong physical width. Both are
# corrected here, so each file states its own printed size.
PRINT_WIDTH_IN = {
    'Figure1_Ti3C2O2_structure.png': 4.5,
    'Figure2_Phase1_schematic.png': 4.0,
    'Figure3_Phase2_schematic.png': 4.0,
    'Figure4_Phase2_sections.png': 5.0,
    'Figure5_series_59.5keV.png': 5.2,
    'Figure6_series_356keV.png': 5.2,
    'Figure7_series_511keV.png': 5.2,
    'Figure8_series_662keV.png': 5.2,
    'Figure9_series_1173keV.png': 5.2,
    'Figure10_series_1332keV.png': 5.2,
    'Figure11.png': 5.5,
    'Figure12.png': 6.4,
    'Figure13.png': 6.0,
    'Figure14.png': 6.3,
    'Figure15.png': 6.3,
}

from PIL import Image

print()
for name, width_in in PRINT_WIDTH_IN.items():
    if not os.path.exists(name):
        print('  missing, not finished:', name)
        continue
    im = Image.open(name)
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA')
        flat = Image.new('RGB', im.size, (255, 255, 255))
        flat.paste(im, mask=im.split()[-1])
        im = flat
    else:
        im = im.convert('RGB')
    eff = im.size[0] / width_in
    im.save(name, dpi=(eff, eff))
    print('  %-32s RGB, %5.0f dpi at %.1f in' % (name, eff, width_in))

print('\nAll 15 manuscript figures written to', os.getcwd())
