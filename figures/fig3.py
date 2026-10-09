# -*- coding: utf-8 -*-
"""Figure 3: to-scale side elevation of the Phase 2 transmission geometry."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patheffects as pe

PB, AL, CU, SN = '#5a5a5a', '#c9cdd1', '#b87333', '#8fa1b3'
NAI, SAMP, BEAM = '#f2e6a8', '#2e8b8b', '#c0392b'

FS = 15          # label size
FIGW = 11.6      # inches; on-page size is FS * 6.5 / FIGW

fig, ax = plt.subplots(figsize=(FIGW, 10.0))


def box(x0, x1, y0, y1, fc, lw=0.8, z=2):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=fc,
                           edgecolor='black', linewidth=lw, zorder=z))


def lab(x, y, s, size=FS, ha='center', va='center', weight='normal'):
    ax.text(x, y, s, ha=ha, va=va, fontsize=size, fontweight=weight, zorder=9,
            path_effects=[pe.withStroke(linewidth=3.0, foreground='white')])


def leader(x0, y0, x1, y1):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0), zorder=8,
                arrowprops=dict(arrowstyle='-', color='black', lw=0.8))


# source housing, source at z = -10 cm
box(-11.0, -10.0, -1.4, 1.4, PB)
ax.plot([-10.0], [0], marker='*', ms=15, color='#ffd400',
        mec='black', mew=0.7, zorder=6)

# primary collimator: Pb, 10 cm square, 5 cm deep, 3 mm bore
box(-7.5, -2.5, 0.15, 5.0, PB)
box(-7.5, -2.5, -5.0, -0.15, PB)

# sample at z = 0, in its aluminium holder ring
box(-0.25, 0.25, -2.5, 2.5, SAMP, lw=0.7)
box(-0.25, 0.25, 2.5, 3.5, AL, lw=0.7)
box(-0.25, 0.25, -3.5, -2.5, AL, lw=0.7)

# secondary collimator: Pb, 10 cm square, 3 cm deep, 5 mm bore
box(1.0, 4.0, 0.25, 5.0, PB)
box(1.0, 4.0, -5.0, -0.25, PB)

# detector: 0.5 mm Al window, NaI(Tl) crystal, housing, graded-Z shells
box(5.00, 5.05, -3.81, 3.81, AL, lw=0.7)
box(5.05, 12.67, -3.81, 3.81, NAI)
for y0, y1, c in [(3.81, 3.91, AL), (3.91, 3.96, CU),
                  (3.96, 4.06, SN), (4.06, 9.06, PB)]:
    box(5.00, 12.67, y0, y1, c, lw=0.5)
    box(5.00, 12.67, -y1, -y0, c, lw=0.5)
box(12.67, 12.80, -4.06, 4.06, AL, lw=0.5)

# zero-divergence pencil beam, 3 mm diameter, on the collimator bore axis
for s in (1, -1):
    ax.plot([-10.0, 5.05], [0.15 * s, 0.15 * s], color=BEAM, lw=1.6, zorder=5)
ax.add_patch(Rectangle((-10.0, -0.15), 15.05, 0.30, facecolor=BEAM,
                       alpha=0.20, edgecolor='none', zorder=4))
for x in (-8.6, -5.0, -1.4, 2.5, 4.5):
    ax.annotate('', xy=(x + 0.6, 0), xytext=(x, 0), zorder=7,
                arrowprops=dict(arrowstyle='-|>', color=BEAM, lw=1.5))

# photons scattered in the sample, stopped on the secondary collimator face
for ang in (1.15, 0.62, -0.58, -1.05):
    ye = ang * 0.75
    ax.plot([0.25, 1.0], [0, ye], color=BEAM, lw=1.1, ls=(0, (3, 2)),
            zorder=5, alpha=0.9)
    ax.plot([1.0], [ye], marker='x', ms=7, mew=1.6, color=BEAM, zorder=6)

# axis line
ax.plot([-10.6, 13.2], [0, 0], color='black', lw=0.6, ls=(0, (6, 4)),
        alpha=0.5, zorder=1)

# labels: few, short, well separated
lab(-10.5, 2.9, 'Source')
lab(-5.0, 6.4, 'Primary\ncollimator (Pb)')
lab(0.0, 4.9, 'Sample')
lab(2.5, -7.2, 'Secondary\ncollimator (Pb)')
leader(2.5, -6.1, 2.5, -5.1)
lab(8.9, 0.0, 'NaI(Tl) crystal')
lab(8.9, 10.1, 'Graded-Z castle')
leader(8.9, 9.5, 8.9, 9.1)

# dimension chain
yd = -10.4
for x in (-10.0, 0.0, 5.05):
    ax.plot([x, x], [yd + 0.35, yd - 0.35], color='black', lw=0.8, zorder=8)
ax.annotate('', xy=(0, yd), xytext=(-10, yd),
            arrowprops=dict(arrowstyle='<->', color='black', lw=0.8))
ax.annotate('', xy=(5.05, yd), xytext=(0, yd),
            arrowprops=dict(arrowstyle='<->', color='black', lw=0.8))
lab(-5.0, yd + 0.85, '10 cm')
lab(2.5, yd + 0.85, '5.05 cm')

ax.set_xlim(-12.0, 14.2)
ax.set_ylim(-11.6, 11.4)
ax.set_aspect('equal')
ax.axis('off')
plt.tight_layout(pad=0.1)
fig.savefig('Figure3_Phase2_schematic.png', dpi=500,
            bbox_inches='tight', facecolor='white')
print('ok')
