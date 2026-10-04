# -*- coding: utf-8 -*-
"""Render every manuscript figure, writing both a 500 dpi PNG for review and a
vector PDF for typesetting. Run from anywhere: python3 figures/render_all.py

Each figN.py is executed unchanged. The only thing this wrapper does is wrap
Figure.savefig so that a second, vector copy is written alongside the raster one."""
import os
import runpy
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
