# -*- coding: utf-8 -*-
"""Figure 1: side projection of the oxygen-terminated Ti3C2O2 MXene monolayer.

The drawing is set by the two lattice parameters quoted in Section 2.5.2 of the
manuscript, the in-plane constant a = 3.083 A and the single-layer thickness of
5.808 A taken from the first-principles monolayer of reference [18]. The five
atomic planes of the Ti-C-Ti-C-Ti core are spaced evenly between the two oxygen
planes, which carry the full thickness between them, and successive planes are
offset in plane by a/2 so that every carbon sits in the hollow between the
titanium atoms above and below it. Every coordinate here is computed from those
two numbers. Nothing is placed by hand."""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch
import matplotlib.patheffects as pe

A_IN = 3.083           # A, in-plane lattice constant
T_ML = 5.808           # A, single-layer thickness, outer oxygen to outer oxygen
N_CELL = 5             # repeats drawn along the in-plane direction

G_TIO = 1.500          # A, vertical Ti to O separation
G_TIC = (T_ML / 2 - G_TIO) / 2     # A, vertical Ti to C separation, so that
#                                    G_TIO + 2*G_TIC is half the thickness

Z = {'O_top':   T_ML / 2,
     'Ti_top':  T_ML / 2 - G_TIO,
     'C_top':   G_TIC,
     'Ti_mid':  0.0,
     'C_bot':  -G_TIC,
     'Ti_bot': -(T_ML / 2 - G_TIO),
     'O_bot':  -T_ML / 2}

COL = {'Ti': '#d9b63a', 'C': '#181818', 'O': '#e8471c'}
RAD = {'Ti': 0.44, 'C': 0.27, 'O': 0.33}

fig, ax = plt.subplots(figsize=(11.4, 9.0))

# two in-plane sublattices, offset by half a cell
x_a = np.arange(N_CELL) * A_IN                     # titanium columns
x_b = x_a[:-1] + A_IN / 2                          # carbon columns

ti_top = [(x, Z['Ti_top']) for x in x_a]
ti_mid = [(x, Z['Ti_mid']) for x in x_a]
ti_bot = [(x, Z['Ti_bot']) for x in x_a]
c_top = [(x, Z['C_top']) for x in x_b]
c_bot = [(x, Z['C_bot']) for x in x_b]
o_top = [(x, Z['O_top']) for x in x_a]
o_bot = [(x, Z['O_bot']) for x in x_a]


def rod(p, q, c1, c2, lw=7.0, dbl=False):
    """Two-tone bond. dbl draws the pair of parallel rods used for Ti-O."""
    if dbl:
        dx, dy = q[0] - p[0], q[1] - p[1]
        n = np.hypot(dx, dy)
        ox, oy = -dy / n * 0.13, dx / n * 0.13
        for s in (-1, 1):
            rod((p[0] + s * ox, p[1] + s * oy), (q[0] + s * ox, q[1] + s * oy),
                c1, c2, lw=lw * 0.52)
        return
    xm, ym = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    ax.plot([p[0], xm], [p[1], ym], color=c1, lw=lw, solid_capstyle='butt', zorder=2)
    ax.plot([xm, q[0]], [ym, q[1]], color=c2, lw=lw, solid_capstyle='butt', zorder=2)


def pairs(src, dst):
    """Nearest neighbours between two planes: the half-cell offset makes the
    separation sqrt((a/2)^2 + dz^2), so anything longer is not a bond."""
    cut = np.hypot(A_IN / 2, abs(src[0][1] - dst[0][1])) * 1.05
    return [(p, q) for p in src for q in dst
            if np.hypot(p[0] - q[0], p[1] - q[1]) < cut]


for (upper, eu), (lower, el_) in (((ti_top, 'Ti'), (c_top, 'C')),
                                  ((c_top, 'C'), (ti_mid, 'Ti')),
                                  ((ti_mid, 'Ti'), (c_bot, 'C')),
                                  ((c_bot, 'C'), (ti_bot, 'Ti'))):
    for p, q in pairs(upper, lower):
        rod(p, q, COL[eu], COL[el_])

for ti, ox in ((ti_top, o_top), (ti_bot, o_bot)):
    for p, q in zip(ti, ox):
        rod(p, q, COL['Ti'], COL['O'], lw=7.0, dbl=True)

# guide lines through the three titanium planes
for key in ('Ti_top', 'Ti_mid', 'Ti_bot'):
    ax.plot([-1.7, x_a[-1] + 1.7], [Z[key]] * 2, color='#b0b0b0', lw=1.0, zorder=1)


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


atoms = ([(x, z, 'O') for x, z in o_top + o_bot]
         + [(x, z, 'Ti') for x, z in ti_top + ti_mid + ti_bot]
         + [(x, z, 'C') for x, z in c_top + c_bot])
for x, z, el in sorted(atoms, key=lambda t: t[1]):
    sphere(x, z, el)


def lab(x, y, s, size=17, ha='center'):
    ax.text(x, y, s, fontsize=size, ha=ha, va='center', zorder=9,
            path_effects=[pe.withStroke(linewidth=3.4, foreground='white')])


def arrow(x0, y0, x1, y1):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0), zorder=8,
                arrowprops=dict(arrowstyle='-|>', color='black', lw=1.4))


lab(x_a[1] + 0.3, Z['O_top'] + 2.45, 'Oxygen (O)\nsurface termination')
arrow(x_a[1] + 0.3, Z['O_top'] + 1.75, x_a[1] + 0.12, Z['O_top'] + 0.62)
lab(-3.3, Z['Ti_top'] + 1.5, 'Titanium (Ti)\nlayers')
arrow(-2.5, Z['Ti_top'] + 0.95, -0.75, Z['Ti_top'] + 0.18)
lab(x_b[-1] + 1.15, Z['O_top'] + 2.35, 'Carbon (C)\natoms')
arrow(x_b[-1] + 0.7, Z['O_top'] + 1.65, x_b[-1] + 0.1, Z['C_top'] + 0.4)
lab(x_a[2] + 1.5, Z['O_bot'] - 1.95, 'Ti surface layer')
arrow(x_a[2] + 1.1, Z['O_bot'] - 1.5, x_a[2] + 0.4, Z['Ti_bot'] - 0.5)

# thickness dimension, outer oxygen plane to outer oxygen plane
xd = x_a[-1] + 1.15
ax.annotate('', xy=(xd, Z['O_top']), xytext=(xd, Z['O_bot']),
            arrowprops=dict(arrowstyle='<->', color='black', lw=1.2))
for zz in (Z['O_top'], Z['O_bot']):
    ax.plot([x_a[-1], xd + 0.35], [zz, zz], color='black', lw=0.8, zorder=3)
lab(xd + 0.5, 0.0, '%.3f Å' % T_ML, size=15, ha='left')

# in-plane lattice constant
ya = Z['O_bot'] - 0.95
ax.annotate('', xy=(x_a[1], ya), xytext=(x_a[0], ya),
            arrowprops=dict(arrowstyle='<->', color='black', lw=1.2))
for xx in (x_a[0], x_a[1]):
    ax.plot([xx, xx], [ya - 0.3, ya + 0.3], color='black', lw=0.8)
lab((x_a[0] + x_a[1]) / 2, ya - 0.72, 'a = %.3f Å' % A_IN, size=15)

lab(x_a[-1] - 0.3, Z['O_bot'] - 2.75, 'Ti$_3$C$_2$O$_2$', size=28)

# legend
hx, hy = x_a[-1] + 3.15, Z['O_bot'] + 0.55
ax.add_patch(FancyBboxPatch((hx - 0.85, hy - 2.55), 3.5, 3.2,
                            boxstyle='round,pad=0.12', facecolor='white',
                            edgecolor='#2b2b2b', lw=1.1, zorder=7))
ax.text(hx + 0.9, hy + 0.32, 'Atom legend', fontsize=14, ha='center',
        va='center', zorder=8, fontweight='bold')
for i, (el, name) in enumerate([('Ti', 'Titanium'), ('C', 'Carbon'), ('O', 'Oxygen')]):
    yy = hy - 0.45 - i * 0.68
    ax.add_patch(Circle((hx, yy), 0.27, facecolor=COL[el], edgecolor='#2b2b2b',
                        lw=0.9, zorder=8))
    ax.text(hx + 0.5, yy, '%s  %s' % (el, name), fontsize=13, va='center', zorder=8)

ax.set_xlim(-5.2, x_a[-1] + 8.0)
ax.set_ylim(Z['O_bot'] - 3.5, Z['O_top'] + 3.5)
ax.set_aspect('equal')
ax.axis('off')
plt.tight_layout(pad=0.2)
fig.savefig('Figure1_Ti3C2O2_structure.png', dpi=500,
            bbox_inches='tight', facecolor='white')
print('ok')
