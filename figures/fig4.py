# -*- coding: utf-8 -*-
"""Figure 4: sections through the Phase 2 components, normal to the beam axis.
All dimensions from phase2-digital-twin/src/DetectorConstruction.cc.

Panel (c) carries a magnified strip through the shield wall, because at the
scale of the 181.2 mm assembly the 1 mm, 0.5 mm and 1 mm graded-Z shells are
thinner than a printed rule and cannot be told apart in the section itself.
"""
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


def panel_letters(fig, pairs, fontsize, min_title=None, level=True):
    """Put (a), (b), ... on the same line as each panel title, clear of its
    left edge. The title is centred on its axes and overhangs when it is wider
    than the axes, so the gap is measured from the title actually drawn rather
    than assumed: a letter at a fixed offset inside the axes ends up underneath
    a wide title. If a title leaves no room, it is stepped down a point at a
    time until it does."""
    need = 0.030 + fontsize / 1400.0          # letter width plus a gap
    for ax, _ in pairs:
        while True:
            fig.canvas.draw()
            bb = ax.title.get_window_extent(
                fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
            size = ax.title.get_fontsize()
            if bb.x0 >= need or min_title is None or size <= min_title:
                break
            ax.title.set_fontsize(size - 1)
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    inv = fig.transFigure.inverted()
    top = max(ax.title.get_window_extent(rend).transformed(inv).y1
              for ax, _ in pairs)
    for ax, lab in pairs:
        bb = ax.title.get_window_extent(rend).transformed(inv)
        if level:
            # on the title's own line, clear of its left edge
            fig.text(max(0.004, bb.x0 - 0.014), 0.5 * (bb.y0 + bb.y1), lab,
                     fontsize=fontsize, fontweight='bold',
                     ha='right' if bb.x0 - 0.014 > 0.02 else 'left', va='center')
        else:
            # Above the title: used where a title is wider than its panel and
            # would otherwise reach the next panel's letter. Every letter is
            # set on one baseline, the highest title top in the figure, so
            # that panels whose titles sit at different heights do not end up
            # with their letters at different heights.
            pos = ax.get_position()
            fig.text(max(0.004, pos.x0 - 0.02), top + 0.004, lab,
                     fontsize=fontsize, fontweight='bold', ha='left',
                     va='bottom')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.gridspec import GridSpec
import matplotlib.patheffects as pe

PB, AL, CU, SN, NAI, BEAM = '#6f6f6f', '#c9cdd1', '#b87333', '#8fa1b3', '#f2e6a8', '#c0392b'
FS, TS = 14, 14

# No chemical subscripts anywhere in this figure, so only the 7 pt floor
# for ordinary lettering applies and the canvas keeps its original size.
fig = plt.figure(figsize=(10.4, 3.55))
gs = GridSpec(1, 3, width_ratios=[1.18, 1.18, 1.75], wspace=0.04, figure=fig)
axes = [fig.add_subplot(gs[0, i]) for i in range(3)]


def halo(lw=3.0):
    return dict(path_effects=[pe.withStroke(linewidth=lw, foreground='white')])


MAG_BORE = 10.0          # enlargement of the bore inset in panels (a) and (b)


def collimator(ax, bore_mm, letter, title, sub):
    """Section through a collimator, with the bore drawn twice.

    At 100 mm across the page the 3 mm and 5 mm bores are about half a printed
    point wide. Drawn once, at true scale, the aperture that the panel exists
    to show is smaller than the rule around it and reads as a smudge. It is
    therefore drawn at true scale in the block, where its size relative to the
    lead is the point, and again beside the block at ten times that size,
    where its diameter can be seen and dimensioned. The enlargement is stated
    on the figure so that nothing is read off the inset as if it were to
    scale."""
    ax.add_patch(Rectangle((-5, -5), 10, 10, facecolor=PB, edgecolor='black', lw=1.0))
    r = bore_mm / 20.0                       # mm diameter -> cm radius
    # true scale, in the block: white, with a thin dark edge so it reads as a
    # hole rather than as a mark laid on the lead
    ax.add_patch(Circle((0, 0), r, facecolor='white', edgecolor='black',
                        lw=0.5, zorder=3))

    # locator box around the bore, the same idiom panel (c) uses for its
    # magnified strip, so the two enlargements read the same way
    ax.add_patch(Rectangle((-0.5, -0.5), 1.0, 1.0, facecolor='none',
                           edgecolor='black', lw=0.8, zorder=5))
    # enlarged, below the block, where the label beside it has clear ground.
    # Set beside the block the label runs back over the lead.
    R = r * MAG_BORE
    cx, cy = 0.0, -5.0 - 1.4 - R
    for sgn in (1, -1):
        ax.plot([sgn * 0.5, cx + sgn * R * 0.72], [-0.5, cy + R * 0.72],
                color='black', lw=0.7, ls=(0, (2, 2)), zorder=6)
    ax.add_patch(Circle((cx, cy), R, facecolor='white', edgecolor=BEAM,
                        lw=1.6, zorder=7))
    ax.annotate('', xy=(cx + R, cy), xytext=(cx - R, cy), zorder=8,
                arrowprops=dict(arrowstyle='<->', color=BEAM, lw=1.2,
                                shrinkA=0, shrinkB=0))
    ax.text(cx + R + 0.7, cy, '%g mm bore\nshown ×%g' % (bore_mm, MAG_BORE),
            fontsize=FS, ha='left', va='center', zorder=8, linespacing=1.3)

    ax.annotate('', xy=(5, 6.1), xytext=(-5, 6.1),
                arrowprops=dict(arrowstyle='<->', color='black', lw=0.9))
    ax.text(0, 6.6, '100 mm', fontsize=FS, ha='center', va='bottom', **halo())
    ax.set_title(letter + ' ' + title + '\n' + sub, fontsize=TS, pad=10,
                 linespacing=1.35)
    ax.set_xlim(-8.6, 14.4); ax.set_ylim(cy - R - 1.4, 9.4)


collimator(axes[0], 3, '(a)', 'Primary collimator',
           'Pb, 100 × 100 mm\nsection, 50 mm deep')
collimator(axes[1], 5, '(b)', 'Secondary collimator',
           'Pb, 100 × 100 mm\nsection, 30 mm deep')

# ---------------------------------------------------------------- panel (c)
ax = axes[2]
for r, c in [(9.06, PB), (4.06, SN), (3.96, CU), (3.91, AL), (3.81, NAI)]:
    ax.add_patch(Circle((0, 0), r, facecolor=c, edgecolor='black', lw=0.7))
ax.plot([0], [0], marker='+', ms=11, mew=1.5, color=BEAM, zorder=6)
# named from outside the assembly with a leader, so the label sits on
# white rather than on the lead, and its ends cannot merge into the
# black shell ring as they did when it was set inside the crystal
ax.annotate('NaI(Tl)', xy=(-3.2, -2.4), xytext=(-14.2, -7.0),
            fontsize=FS, ha='left', va='center', zorder=7,
            arrowprops=dict(arrowstyle='-|>', color='black', lw=0.9,
                            shrinkA=2, shrinkB=1))
# on the true diameter, through the centre. Drawn as two halves so the
# beam-axis marker stays visible: a line set below the centre is a
# chord, and quoting it as the diameter would be wrong.
for _inner, _outer in ((-0.8, -3.81), (0.8, 3.81)):
    ax.annotate('', xy=(_outer, 0.0), xytext=(_inner, 0.0), zorder=6,
                arrowprops=dict(arrowstyle='-|>', color='black', lw=0.8,
                                shrinkA=0, shrinkB=0))
ax.text(0, -5.9, '⌀ 76.2 mm', fontsize=FS, ha='center', va='center',
        zorder=6, **halo())

# lead wall callout, clear of the magnified strip
# set low and to the left, clear of the two-line note above: at its old
# height the callout ran into '(Pb and NaI truncated)'
# set on the lead it names, inside the annulus, so no leader is needed and
# the label cannot reach either the circle's edge or the note above it
ax.text(-2.6, 5.2, 'Pb 50 mm', fontsize=FS, ha='center', va='center',
        zorder=6, **halo())

# --- magnified strip through the shield wall ------------------------------
# radii 3.81 -> 4.06 cm carry Al 1 mm, Cu 0.5 mm, Sn 1 mm. Drawn here at 20x
# so the three shells are separable; the Pb and NaI blocks are truncated.
SX, SW = 12.2, 2.3                      # strip left edge and width
MAG = 30.0
base = 3.81
layers = [('NaI(Tl) crystal', NAI, 0.055), ('Al 1 mm', AL, 0.10),
          ('Cu 0.5 mm', CU, 0.05), ('Sn 1 mm', SN, 0.10), ('Pb 50 mm', PB, 0.060)]
y = -5.8
for name, colour, thick_cm in layers:
    h = thick_cm * MAG
    ax.add_patch(Rectangle((SX, y), SW, h, facecolor=colour,
                           edgecolor='black', lw=0.7, zorder=4))
    ax.text(SX + SW + 0.35, y + h / 2.0, name, fontsize=FS, ha='left',
            va='center', zorder=6)
    y += h
# tie the strip back to the wall it magnifies
ax.plot([3.95, SX], [2.4, y], color='black', lw=0.8, ls=':', zorder=3)
ax.plot([3.95, SX], [-1.2, -5.8], color='black', lw=0.8, ls=':', zorder=3)
ax.add_patch(Rectangle((3.70, -1.2), 0.47, 3.6, facecolor='none',
                       edgecolor='black', lw=0.9, zorder=5))
# placed above the lead circle: at this width the caption line is wider than
# the strip and would otherwise run across the assembly
# right-aligned to the panel edge: centred on the strip this two-line note
# reaches back across the assembly and runs into the 'Pb 50 mm' callout
ax.text(20.2, 10.4, 'graded-Z shells, ×30\n(Pb and NaI truncated)',
        fontsize=FS, ha='right', va='bottom', zorder=6, linespacing=1.25)

ax.annotate('', xy=(9.06, -10.6), xytext=(-9.06, -10.6),
            arrowprops=dict(arrowstyle='<->', color='black', lw=0.9))
ax.text(0, -12.3, '181.2 mm', fontsize=FS, ha='center', va='center', **halo())
ax.set_title('(c) Detector assembly\nNaI(Tl) crystal within\nthe graded-Z castle',
             fontsize=TS, pad=10, linespacing=1.35)
ax.set_xlim(-14.8, 20.4); ax.set_ylim(-14.2, 16.0)

for a in axes:
    a.set_aspect('equal'); a.axis('off')
# Panel letters are set at the head of each panel title, the one rule used
# across every figure in this paper. A letter placed outside the axes has
# to be positioned against a title whose height and width change with the
# text, and it does not scale down to the small panels of Figures 5 to 10.
fig.savefig('Figure4_Phase2_sections.png', dpi=500,
            bbox_inches='tight', pad_inches=0.04, facecolor='white')
print('ok')
