# -*- coding: utf-8 -*-
"""Figure 2: Phase 1 narrow-beam geometry, drawn to scale from
phase1-narrow-beam/src/DetectorConstruction.cc and PrimaryGeneratorAction.cc."""
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
from matplotlib.patches import Rectangle
import matplotlib.patheffects as pe

# One colour scheme across the two geometry schematics, Figures 2 and 3:
# the beam is red in both, the sample blue in both, the counting volume
# pale yellow in both. Before this the beam was green here and red in
# Figure 3, while red here meant the counter.
TARGET = '#2e6fb7'   # blue target, as the original caption describes
COUNTER = '#f2e6a8'  # counting volume, the colour Figure 3 gives NaI(Tl)
BEAM = '#c0392b'     # photon track, as in Figure 3
FS = 15
fig, ax = plt.subplots(figsize=(7.26, 4.63))


def box(x0, x1, y0, y1, fc, ec='black', lw=0.8, z=2, alpha=1.0):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=fc,
                           edgecolor=ec, linewidth=lw, zorder=z, alpha=alpha))


def lab(x, y, s, size=FS, ha='center', va='center'):
    ax.text(x, y, s, ha=ha, va=va, fontsize=size, zorder=9,
            path_effects=[pe.withStroke(linewidth=3.0, foreground='white')])


def leader(x0, y0, x1, y1):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0), zorder=8,
                arrowprops=dict(arrowstyle='-', color='black', lw=0.8))


# world volume: 50 cm cube of vacuum (G4Box 25 cm half-length)
lab(0.5, 8.5, 'World volume: 50 cm cube, vacuum', size=FS - 1)

# composite target: G4Tubs r = 2.5 cm at z = 0, thickness 2 to 10 mm
box(-0.5, 0.5, -2.5, 2.5, TARGET, lw=0.8)

# transmission counter: G4Box 10 x 10 cm, 0.2 mm thick, at z = +5 cm.
# Every other dimension in this figure is to scale. A 0.2 mm foil across a
# 150 mm field is thinner than a printed rule, so it is drawn thicker and
# the label says so, rather than letting the reader scale it off.
box(4.9, 5.1, -5.0, 5.0, COUNTER, lw=0.8)

# zero-divergence pencil beam, source at z = -10 cm along +z
ax.annotate('', xy=(4.9, 0), xytext=(-10, 0), zorder=6,
            arrowprops=dict(arrowstyle='-|>', color=BEAM, lw=2.6))
ax.plot([-10], [0], marker='*', ms=17, color='#ffd400', mec='black', mew=0.7, zorder=7)
for x in (-7.6, -4.2, -0.8, 2.6):
    ax.annotate('', xy=(x + 0.9, 0), xytext=(x, 0), zorder=8,
                arrowprops=dict(arrowstyle='-|>', color=BEAM, lw=2.0))

ax.plot([-11, 8.5], [0, 0], color='black', lw=0.6, ls=(0, (6, 4)), alpha=0.5, zorder=1)

lab(-10.0, 4.2, 'Source\n$z$ = −10 cm')
lab(-5.6, 1.75, 'zero-divergence\npencil beam', size=FS - 1)
lab(-4.6, -5.9, 'composite target\nradius 25 mm, 2 to 10 mm thick\n(10 mm shown)')
leader(-1.6, -4.9, -0.55, -2.2)
lab(11.8, 6.0, 'transmission counter\n100 \u00d7 100 mm, 0.2 mm thick\n(thickness exaggerated)')
leader(8.6, 3.85, 5.25, 2.1)
lab(8.0, 0.9, '$z$', size=FS)

# dimension chain
yd = -11.1
for x in (-10.0, 0.0, 5.0):
    ax.plot([x, x], [yd + 0.5, yd - 0.5], color='black', lw=0.8, zorder=8)
ax.annotate('', xy=(0, yd), xytext=(-10, yd), arrowprops=dict(arrowstyle='<->', color='black', lw=0.8))
ax.annotate('', xy=(5.0, yd), xytext=(0, yd), arrowprops=dict(arrowstyle='<->', color='black', lw=0.8))
lab(-5.0, yd + 1.2, '10 cm')
lab(2.5, yd + 1.2, '5 cm')

ax.set_xlim(-13.5, 18.5)
ax.set_ylim(-13.4, 9.4)
ax.set_aspect('equal')
ax.axis('off')
plt.tight_layout(pad=0.1)
fig.savefig('Figure2_Phase1_schematic.png', dpi=500,
            bbox_inches='tight', facecolor='white')
print('ok')
