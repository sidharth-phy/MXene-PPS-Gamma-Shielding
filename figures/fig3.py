# -*- coding: utf-8 -*-
"""Figure 3: to-scale side elevation of the Phase 2 transmission geometry."""
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

PB, AL, CU, SN = '#5a5a5a', '#c9cdd1', '#b87333', '#8fa1b3'
NAI, SAMP, BEAM = '#f2e6a8', '#2e6fb7', '#c0392b'   # SAMP matches fig2 TARGET

FS = 15          # label size
FIGW = 7.40      # inches; on-page size is FS * 6.5 / FIGW

fig, ax = plt.subplots(figsize=(FIGW, 6.38))


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
ax.plot([-10.6, 11.6], [0, 0], color='black', lw=0.6, ls=(0, (6, 4)),
        alpha=0.5, zorder=1)

# labels: few, short, well separated. Every leader runs from the foot of its
# own text to the edge of the object it names, through free space: a leader
# that stops short reads as a stray mark, and one that crosses a block reads
# as part of the drawing.
lab(-10.5, 2.9, 'Source')
lab(-5.0, 6.4, 'Primary\ncollimator (Pb)')
# the sample disc is named from the gap between it and the secondary
# collimator, the only corridor that reaches the disc itself rather than the
# holder ring stacked above and below it
lab(0.9, 6.15, 'Sample')
leader(0.78, 5.72, 0.27, 2.2)
# the holder ring is named from below, where a short vertical leader reaches
# the lower ring without crossing anything
lab(-0.95, -4.95, 'Al\nholder')
leader(-0.55, -4.12, -0.16, -3.55)
lab(1.6, -7.9, 'Secondary\ncollimator (Pb)')
leader(1.6, -6.85, 2.0, -5.1)
lab(8.9, 0.0, 'NaI(Tl) crystal')
lab(10.2, 11.4, 'Graded-Z castle')
leader(10.2, 10.95, 9.6, 9.10)

# key: the beam and the scattered photons stopped on the collimator face.
# Without it the dashed rays and their crosses are unexplained marks.
from matplotlib.lines import Line2D
_key = [Line2D([0], [0], color=BEAM, lw=1.6, marker='>', ms=6,
               label='Primary beam (3 mm)'),
        Line2D([0], [0], color=BEAM, lw=1.1, ls=(0, (3, 2)), marker='x',
               ms=7, mew=1.6, label='Scattered, stopped')]
ax.legend(handles=_key, loc='upper left', bbox_to_anchor=(0.005, 1.0),
          fontsize=FS, frameon=True, borderpad=0.5, labelspacing=0.5,
          handlelength=2.2).set_zorder(10)

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
ax.set_ylim(-12.2, 15.2)
ax.set_aspect('equal')
ax.axis('off')
plt.tight_layout(pad=0.1)
fig.savefig('Figure3_Phase2_schematic.png', dpi=500,
            bbox_inches='tight', facecolor='white')
print('ok')
