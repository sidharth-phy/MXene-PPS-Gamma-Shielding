# -*- coding: utf-8 -*-
"""Render every manuscript figure, Figures 1 to 24, writing both a PNG at the dpi each
script sets and a vector PDF for typesetting. Run from anywhere: python3 figures/render_all.py

Each figN.py is executed unchanged. The only thing this wrapper does is wrap
Figure.savefig so that a second, vector copy is written alongside the raster one."""
import os
import runpy
import sys
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure

HERE = os.path.dirname(os.path.abspath(__file__))
_orig = Figure.savefig


def savefig(self, fname, *a, **kw):
    out = _orig(self, fname, *a, **kw)
    name = fname if isinstance(fname, str) else None
    if name and name.lower().endswith('.png'):
        kw.pop('dpi', None)
        _orig(self, name[:-4] + '.pdf', *a, **kw)
    return out


Figure.savefig = savefig

for n in (1, 2, 3, 4):
    runpy.run_path(os.path.join(HERE, 'fig%d.py' % n), run_name='__main__')
    print('figure %d written' % n)

for script, figures in (('fig_series.py', 'figures 5 to 10'),
                        ('fig_summary.py', 'figures 11, 12, 23 and 24'),
                        ('fig_spectra.py', 'figures 13 to 18'),
                        ('fig_lac_loading.py', 'figure 19'),
                        ('fig_hvl_rpe.py', 'figures 20 to 22')):
    sys.argv = [script]
    runpy.run_path(os.path.join(HERE, script), run_name='__main__')
    print('%s written' % figures)
