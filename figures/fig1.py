# -*- coding: utf-8 -*-
"""Figure 1: side projection of the oxygen-terminated Ti3C2O2 MXene monolayer.

Geometry comes from the two lattice parameters quoted in Section 2.5.2 of the
manuscript, the in-plane constant a = 3.083 A and the single-layer thickness of
5.808 A taken from the first-principles monolayer of reference [23] of the manuscript.

The seven atomic planes are O, Ti, C, Ti, C, Ti, O. Successive planes are offset
in plane by a/3, which is the ABC stacking of close-packed sheets, so each carbon
sits in the hollow of the titanium triangle above it and of the one below it. In
this side projection that offset gives every atom two bonds to the plane below,
one at a/3 and one at 2a/3, which is why the two bonds leaving an atom do not
make the same angle with the sheet. Every coordinate is computed from the two
lattice parameters, except the titanium to oxygen plane separation G_TIO, which is a
drawing choice that fixes how the seven planes are spaced inside the stated thickness."""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch
import matplotlib.patheffects as pe

A_IN = 3.083            # A, in-plane lattice constant
T_ML = 5.808            # A, single-layer thickness, outer oxygen to outer oxygen
N_CELL = 5              # repeats drawn across the sheet

G_TIO = 1.050           # A, vertical Ti to O separation
G_TIC = (T_ML / 2 - G_TIO) / 2    # A, vertical Ti to C separation, so that
#                                   G_TIO + 2*G_TIC is half the thickness
DX = A_IN / 3.0         # A, in-plane offset between successive planes

COL = {'Ti': '#d9b63a', 'C': '#181818', 'O': '#e8471c'}
RAD = {'Ti': 0.40, 'C': 0.25, 'O': 0.30}

# plane name, element, height, in-plane offset
# The offset accumulates by -a/3 from one plane to the next. The lattice repeats
# every a, so each offset is folded into the interval (-a/2, a/2]. That leaves the
# geometry untouched and keeps the sheet level across the drawing instead of
# marching sideways from the top plane to the bottom one.
def fold(k):
    return ((k * -DX + A_IN / 2) % A_IN) - A_IN / 2


PLANES = [('O_top',  'O',  T_ML / 2,             fold(0)),
          ('Ti_top', 'Ti', T_ML / 2 - G_TIO,     fold(0)),
          ('C_top',  'C',  G_TIC,                fold(1)),
          ('Ti_mid', 'Ti', 0.0,                  fold(2)),
          ('C_bot',  'C', -G_TIC,                fold(3)),
          ('Ti_bot', 'Ti', -(T_ML / 2 - G_TIO),  fold(4)),
          ('O_bot',  'O', -T_ML / 2,             fold(4))]

plane = {}
for name, el, z, off in PLANES:
    plane[name] = [(off + i * A_IN, z, el) for i in range(N_CELL)]

X0 = min(p[0] for v in plane.values() for p in v)
X1 = max(p[0] for v in plane.values() for p in v)

ZT = dict((n, zz) for n, _, zz, _ in PLANES)

fig, ax = plt.subplots(figsize=(11.4, 8.4))


def rod(p, q, c1, c2, lw=6.5, dbl=False):
    """Two-tone bond. dbl draws the pair of parallel rods used for Ti-O."""
    if dbl:
        dx, dy = q[0] - p[0], q[1] - p[1]
        n = np.hypot(dx, dy)
        ox, oy = -dy / n * 0.105, dx / n * 0.105
        for s in (-1, 1):
            rod((p[0] + s * ox, p[1] + s * oy), (q[0] + s * ox, q[1] + s * oy),
                c1, c2, lw=lw * 0.55)
        return
    xm, ym = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    ax.plot([p[0], xm], [p[1], ym], color=c1, lw=lw, solid_capstyle='butt', zorder=2)
    ax.plot([xm, q[0]], [ym, q[1]], color=c2, lw=lw, solid_capstyle='butt', zorder=2)


# Ti-C bonds: each atom reaches the plane below at a/3 and at 2a/3
cut = np.hypot(2 * DX, abs(ZT['Ti_top'] - ZT['C_top'])) * 1.02
for (na, ea, _, _), (nb, eb, _, _) in zip(PLANES[1:5], PLANES[2:6]):
    for p in plane[na]:
        for q in plane[nb]:
            if np.hypot(p[0] - q[0], p[1] - q[1]) < cut:
                rod(p[:2], q[:2], COL[ea], COL[eb])

# Ti-O terminations, drawn as the double rod of the reference schematic
for nt, no in (('Ti_top', 'O_top'), ('Ti_bot', 'O_bot')):
    for p in plane[nt]:
        for q in plane[no]:
            if abs(p[0] - q[0]) < 1e-6:
                rod(p[:2], q[:2], COL['Ti'], COL['O'], dbl=True)

# guide lines through the three titanium planes
for name in ('Ti_top', 'Ti_mid', 'Ti_bot'):
    ax.plot([X0 - 1.3, X1 + 1.3], [ZT[name]] * 2, color='#b0b0b0', lw=1.0, zorder=1)


def sphere(x, z, el):
    """Flat colour with a soft highlight, built from concentric discs."""
    r = RAD[el]
    base = np.array(matplotlib.colors.to_rgb(COL[el]))
    ax.add_patch(Circle((x, z), r, facecolor=COL[el], edgecolor='#2b2b2b',
                        lw=1.0, zorder=4))
    for i in range(10):
        f = (i + 1) / 10.0
        tint = base + (1.0 - base) * (0.62 * f)
        ax.add_patch(Circle((x - r * 0.26 * f, z + r * 0.28 * f), r * (1 - 0.72 * f),
                            facecolor=tint, edgecolor='none', zorder=4 + f * 0.1))


for name, el, z, off in PLANES:
    for x, zz, ee in plane[name]:
        sphere(x, zz, ee)

x_ti_top = sorted(p[0] for p in plane['Ti_top'])
x_c_top = sorted(p[0] for p in plane['C_top'])
x_ti_bot = sorted(p[0] for p in plane['Ti_bot'])


def lab(x, y, s, size=19, ha='center'):
    ax.text(x, y, s, fontsize=size, ha=ha, va='center', zorder=9,
            path_effects=[pe.withStroke(linewidth=3.4, foreground='white')])


def arrow(x0, y0, x1, y1):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0), zorder=8,
                arrowprops=dict(arrowstyle='-|>', color='black', lw=1.4))


lab(x_ti_top[1] + 0.2, ZT['O_top'] + 2.3, 'Oxygen (O)\nsurface termination')
arrow(x_ti_top[1] + 0.2, ZT['O_top'] + 1.6, x_ti_top[1] + 0.05, ZT['O_top'] + 0.5)
lab(X0 - 3.0, ZT['Ti_top'] + 1.45, 'Titanium (Ti)\nlayers')
arrow(X0 - 2.3, ZT['Ti_top'] + 0.9, X0 - 0.55, ZT['Ti_top'] + 0.2)
lab(x_c_top[-1] + 1.3, ZT['O_top'] + 2.3, 'Carbon (C)\natoms')
arrow(x_c_top[-1] + 0.85, ZT['O_top'] + 1.6, x_c_top[-1] + 0.12, ZT['C_top'] + 0.38)
lab(X0 - 2.75, ZT['Ti_bot'] - 0.35, 'Ti surface\nlayer')
arrow(X0 - 1.75, ZT['Ti_bot'] - 0.35, x_ti_bot[0] - 0.5, ZT['Ti_bot'] - 0.12)

# thickness dimension, outer oxygen plane to outer oxygen plane
xd = X1 + 1.0
ax.annotate('', xy=(xd, T_ML / 2), xytext=(xd, -T_ML / 2),
            arrowprops=dict(arrowstyle='<->', color='black', lw=1.2))
for zz in (T_ML / 2, -T_ML / 2):
    ax.plot([X1 - 0.6, xd + 0.35], [zz, zz], color='black', lw=0.8, zorder=3)
lab(xd + 0.5, 0.0, '%.3f Å' % T_ML, size=17, ha='left')

# in-plane lattice constant
ya = -T_ML / 2 - 0.95
ax.annotate('', xy=(x_ti_bot[1] + A_IN, ya), xytext=(x_ti_bot[1], ya),
            arrowprops=dict(arrowstyle='<->', color='black', lw=1.2))
for xx in (x_ti_bot[1], x_ti_bot[1] + A_IN):
    ax.plot([xx, xx], [ya - 0.3, ya + 0.3], color='black', lw=0.8)
lab(x_ti_bot[1] + A_IN / 2, ya - 0.72, 'a = %.3f Å' % A_IN, size=17)

lab(X1 - 0.4, -T_ML / 2 - 2.7, 'Ti$_3$C$_2$O$_2$', size=30)

# legend
hx, hy = X1 + 3.1, -T_ML / 2 + 0.55
ax.add_patch(FancyBboxPatch((hx - 0.8, hy - 2.5), 4.6, 3.25,
                            boxstyle='round,pad=0.12', facecolor='white',
                            edgecolor='#2b2b2b', lw=1.1, zorder=7))
ax.text(hx + 1.5, hy + 0.35, 'Atom legend', fontsize=15, ha='center',
        va='center', zorder=8, fontweight='bold')
for i, (el, name) in enumerate([('Ti', 'Titanium'), ('C', 'Carbon'), ('O', 'Oxygen')]):
    yy = hy - 0.45 - i * 0.68
    ax.add_patch(Circle((hx, yy), 0.27, facecolor=COL[el], edgecolor='#2b2b2b',
                        lw=0.9, zorder=8))
    ax.text(hx + 0.47, yy, '%s  %s' % (el, name), fontsize=14, va='center', zorder=8)

ax.set_xlim(X0 - 5.0, X1 + 7.6)
ax.set_ylim(-T_ML / 2 - 3.5, T_ML / 2 + 3.4)
ax.set_aspect('equal')
ax.axis('off')
plt.tight_layout(pad=0.2)
fig.savefig('Figure1_Ti3C2O2_structure.png', dpi=500,
            bbox_inches='tight', facecolor='white')
print('ok')
