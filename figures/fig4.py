# -*- coding: utf-8 -*-
"""Figure 4: sections through the Phase 2 components, normal to the beam axis.
All dimensions from phase2-digital-twin/src/DetectorConstruction.cc."""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Wedge
import matplotlib.patheffects as pe

PB, AL, CU, SN, NAI, BEAM = '#6f6f6f', '#c9cdd1', '#b87333', '#8fa1b3', '#f2e6a8', '#c0392b'
fig, axes = plt.subplots(1, 3, figsize=(15.6, 6.2))


def halo(t):
    return dict(path_effects=[pe.withStroke(linewidth=3.0, foreground='white')])


def collimator(ax, bore_mm, title, sub):
    ax.add_patch(Rectangle((-5, -5), 10, 10, facecolor=PB, edgecolor='black', lw=1.0))
    r = bore_mm / 20.0                       # mm diameter -> cm radius
    ax.add_patch(Circle((0, 0), r, facecolor='white', edgecolor=BEAM, lw=2.0, zorder=3))
    ax.annotate('', xy=(r, 0), xytext=(-r, 0), zorder=5,
                arrowprops=dict(arrowstyle='<->', color=BEAM, lw=1.4))
    ax.plot([0, 3.4], [0, 3.0], color='black', lw=0.9, zorder=4)
    ax.text(3.6, 3.2, f'{bore_mm:g} mm bore', fontsize=14, ha='left', va='center',
            zorder=6, **halo(0))
    ax.annotate('', xy=(5, -6.1), xytext=(-5, -6.1),
                arrowprops=dict(arrowstyle='<->', color='black', lw=0.9))
    ax.text(0, -7.0, '100 mm', fontsize=14, ha='center')
    ax.set_title(title + '\n' + sub, fontsize=15, pad=12)
    ax.set_xlim(-8.2, 10.2); ax.set_ylim(-8.6, 8.6)


collimator(axes[0], 3, '(a) Primary collimator', 'Pb, 100 × 100 mm section, 50 mm deep')
collimator(axes[1], 5, '(b) Secondary collimator', 'Pb, 100 × 100 mm section, 30 mm deep')

ax = axes[2]
for r, c in [(9.06, PB), (4.06, SN), (3.96, CU), (3.91, AL), (3.81, NAI)]:
    ax.add_patch(Circle((0, 0), r, facecolor=c, edgecolor='black', lw=0.7))
ax.add_patch(Wedge((0, 0), 9.06, 20, 70, width=9.06, facecolor='none',
                   edgecolor='black', lw=0.0))
ax.plot([0], [0], marker='+', ms=12, mew=1.6, color=BEAM, zorder=6)
ax.text(0, 0.9, 'NaI(Tl)\n⌀ 76.2 mm', fontsize=14, ha='center', va='center', zorder=6, **halo(0))
for r, name in [(3.86, 'Al 1 mm'), (3.935, 'Cu 0.5 mm'), (4.01, 'Sn 1 mm'), (6.5, 'Pb 50 mm')]:
    a = np.deg2rad({3.86: 62, 3.935: 40, 4.01: 20, 6.5: 78}[r])
    x0, y0 = r * np.cos(a), r * np.sin(a)
    x1, y1 = (10.6, y0 + 2.6) if r < 5 else (5.4, 10.4)
    ax.plot([x0, x1], [y0, y1], color='black', lw=0.9, zorder=5)
    ax.text(x1 + 0.25, y1, name, fontsize=14, ha='left', va='center', zorder=6, **halo(0))
ax.annotate('', xy=(9.06, -10.4), xytext=(-9.06, -10.4),
            arrowprops=dict(arrowstyle='<->', color='black', lw=0.9))
ax.text(0, -11.6, '181.2 mm', fontsize=14, ha='center')
ax.set_title('(c) Detector assembly\nNaI(Tl) crystal within the graded-Z castle', fontsize=15, pad=12)
ax.set_xlim(-11.5, 17.5); ax.set_ylim(-13.2, 12.6)

for a in axes:
    a.set_aspect('equal'); a.axis('off')
plt.tight_layout(pad=0.6)
fig.savefig('Figure4_Phase2_sections.png', dpi=500,
            bbox_inches='tight', facecolor='white')
print('ok')
