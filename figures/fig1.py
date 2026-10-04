# -*- coding: utf-8 -*-
"""Figure 1: side projection of the oxygen-terminated Ti3C2O2 MXene monolayer,
drawn to scale from the lattice parameters used in the manuscript:
in-plane constant a = 3.083 A, monolayer thickness 5.808 A (ref [18]).

The sheet is the five-atom Ti-C-Ti-C-Ti stack with an oxygen terminating the
outer titanium on each face. Positions are computed, not drawn by hand."""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.patheffects as pe

A_IN = 3.083          # A, in-plane lattice constant
T_ML = 5.808          # A, monolayer thickness, outer O to outer O
N_CELL = 5            # repeats drawn along the in-plane direction

# layer heights, symmetric about z = 0, spanning the monolayer thickness
Z = {'O_top':  T_ML / 2,
     'Ti_top': T_ML / 2 - 1.05,
     'C_top':  0.60,
     'Ti_mid': 0.0,
     'C_bot': -0.60,
     'Ti_bot': -(T_ML / 2 - 1.05),
     'O_bot': -T_ML / 2}

COL = {'Ti': '#d4b43c', 'C': '#1a1a1a', 'O': '#e04a1f'}
RAD = {'Ti': 0.62, 'C': 0.34, 'O': 0.46}

fig, ax = plt.subplots(figsize=(11.0, 9.6))

# in-plane x positions: Ti on one sublattice, C offset by half a cell
x_ti = np.arange(N_CELL) * A_IN
x_c = x_ti[:-1] + A_IN / 2

atoms = []
for x in x_ti:
    atoms += [(x, Z['O_top'], 'O'), (x, Z['Ti_top'], 'Ti'),
              (x, Z['Ti_bot'], 'Ti'), (x, Z['O_bot'], 'O')]
for x in x_c + A_IN / 2 - A_IN / 2:
    pass
for x in x_c:
    atoms += [(x, Z['C_top'], 'C'), (x, Z['C_bot'], 'C')]
for x in x_ti[:-1] + A_IN / 2:
    atoms += [(x, Z['Ti_mid'], 'Ti')]


def bond(p, q, c1, c2, lw=5.5):
    xm, ym = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    ax.plot([p[0], xm], [p[1], ym], color=c1, lw=lw, solid_capstyle='round', zorder=2)
    ax.plot([xm, q[0]], [ym, q[1]], color=c2, lw=lw, solid_capstyle='round', zorder=2)


# Ti-C bonds within the stack, nearest neighbours only
def nearest(src, dst, cut):
    out = []
    for a in src:
        for b in dst:
            if np.hypot(a[0] - b[0], a[1] - b[1]) < cut:
                out.append((a, b))
    return out


ti_top = [(x, Z['Ti_top']) for x in x_ti]
ti_mid = [(x, Z['Ti_mid']) for x in x_ti[:-1] + A_IN / 2]
ti_bot = [(x, Z['Ti_bot']) for x in x_ti]
c_top = [(x, Z['C_top']) for x in x_c]
c_bot = [(x, Z['C_bot']) for x in x_c]

for a, b in nearest(ti_top, c_top, 2.9):
    bond(a, b, COL['Ti'], COL['C'])
for a, b in nearest(ti_mid, c_top, 2.9):
    bond(a, b, COL['Ti'], COL['C'])
for a, b in nearest(ti_mid, c_bot, 2.9):
    bond(a, b, COL['Ti'], COL['C'])
for a, b in nearest(ti_bot, c_bot, 2.9):
    bond(a, b, COL['Ti'], COL['C'])
# Ti-O terminations, vertical
for x in x_ti:
    bond((x, Z['Ti_top']), (x, Z['O_top']), COL['Ti'], COL['O'], lw=5.0)
    bond((x, Z['Ti_bot']), (x, Z['O_bot']), COL['Ti'], COL['O'], lw=5.0)

# layer guide lines
for key, lab in [('Ti_top', None), ('Ti_mid', None), ('Ti_bot', None)]:
    ax.plot([-1.4, x_ti[-1] + 1.4], [Z[key]] * 2, color='#9a9a9a', lw=0.9, zorder=1)

# atoms, drawn back to front with a simple specular highlight
for x, z, el in sorted(atoms, key=lambda t: t[1]):
    ax.add_patch(Circle((x, z), RAD[el], facecolor=COL[el], edgecolor='black',
                        lw=0.9, zorder=4))
    ax.add_patch(Circle((x - RAD[el] * 0.3, z + RAD[el] * 0.33), RAD[el] * 0.26,
                        facecolor='white', alpha=0.45, edgecolor='none', zorder=5))


def lab(x, y, s, size=17, ha='center'):
    ax.text(x, y, s, fontsize=size, ha=ha, va='center', zorder=9,
            path_effects=[pe.withStroke(linewidth=3.2, foreground='white')])


def arrow(x0, y0, x1, y1):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0), zorder=8,
                arrowprops=dict(arrowstyle='-|>', color='black', lw=1.3))


lab(-0.2, Z['O_top'] + 2.5, 'Oxygen (O)\nsurface termination')
arrow(0.55, Z['O_top'] + 1.85, x_ti[1] - 0.25, Z['O_top'] + 0.55)
lab(x_ti[-1] + 2.7, Z['C_top'] + 0.9, 'Carbon (C)\natoms', ha='center')
arrow(x_ti[-1] + 1.75, Z['C_top'] + 0.45, x_c[-1] + 0.45, Z['C_top'] + 0.2)
lab(-3.0, Z['Ti_top'], 'Titanium (Ti)\nlayers', ha='center')
arrow(-1.9, Z['Ti_top'] - 0.1, -0.65, Z['Ti_top'])

# thickness dimension
xd = x_ti[-1] + 1.05
ax.annotate('', xy=(xd, Z['O_top']), xytext=(xd, Z['O_bot']),
            arrowprops=dict(arrowstyle='<->', color='black', lw=1.1))
for zz in (Z['O_top'], Z['O_bot']):
    ax.plot([x_ti[-1], xd + 0.3], [zz, zz], color='black', lw=0.7)
lab(xd + 0.55, 0.0, '%.3f Å' % T_ML, size=15, ha='left')

# in-plane lattice constant
ya = Z['O_bot'] - 1.15
ax.annotate('', xy=(x_ti[1], ya), xytext=(x_ti[0], ya),
            arrowprops=dict(arrowstyle='<->', color='black', lw=1.1))
for xx in (x_ti[0], x_ti[1]):
    ax.plot([xx, xx], [ya - 0.28, ya + 0.28], color='black', lw=0.7)
lab((x_ti[0] + x_ti[1]) / 2, ya - 0.72, 'a = %.3f Å' % A_IN, size=15)

lab(x_ti[-1] * 0.5, Z['O_bot'] - 2.6, 'Ti$_3$C$_2$O$_2$', size=26)

# legend
hx, hy = x_ti[-1] + 2.0, Z['O_bot'] + 0.4
for i, (el, name) in enumerate([('Ti', 'Titanium'), ('C', 'Carbon'), ('O', 'Oxygen')]):
    yy = hy - i * 0.95
    ax.add_patch(Circle((hx, yy), 0.33, facecolor=COL[el], edgecolor='black', lw=0.9, zorder=6))
    ax.text(hx + 0.6, yy, '%s  %s' % (el, name), fontsize=14, va='center', zorder=6)

ax.set_xlim(-4.6, x_ti[-1] + 6.4)
ax.set_ylim(Z['O_bot'] - 3.6, Z['O_top'] + 3.4)
ax.set_aspect('equal')
ax.axis('off')
plt.tight_layout(pad=0.2)
fig.savefig('Figure1_Ti3C2O2_structure.png', dpi=500,
            bbox_inches='tight', facecolor='white')
print('ok')
