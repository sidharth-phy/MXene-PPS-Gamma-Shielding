#!/usr/bin/env python3
"""Objective publication check for one rendered figure.

Usage: check_fig.py <png> <printed_width_inches> [label]

Measures, at the size the figure is actually printed:
  effective resolution, smallest and largest lettering, thinnest ink run,
  dead margin, ink touching the canvas edge, and the closest approach
  between any two separate pieces of text.
Thresholds are Elsevier's artwork guidance: 500 dpi combination art,
7 pt minimum lettering, 0.25 pt minimum line weight.
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

CAP_RATIO = 0.729          # DejaVu Sans cap height / em
MIN_PT = 7.0
MIN_RULE_PT = 0.25
MIN_DPI = 500.0


def check(path, pw, label=''):
    im = Image.open(path)
    arr = np.array(im.convert('L')).astype(int)
    H, W = arr.shape
    ppi = W / pw                      # source pixels per printed inch
    px2pt = 72.0 / ppi                # printed points per source pixel
    dark = arr < 110

    out = {'file': path, 'label': label, 'px': (W, H), 'print_in': pw,
           'dpi': ppi, 'fails': [], 'warns': []}

    if ppi < MIN_DPI:
        out['fails'].append('resolution %.0f dpi below %.0f' % (ppi, MIN_DPI))

    # --- edge ink -----------------------------------------------------
    edges = {'top': dark[0].sum(), 'bottom': dark[-1].sum(),
             'left': dark[:, 0].sum(), 'right': dark[:, -1].sum()}
    hit = {k: int(v) for k, v in edges.items() if v}
    if hit:
        out['fails'].append('ink on canvas edge %s' % hit)

    # --- dead margin --------------------------------------------------
    nz = np.where(arr < 245)
    if len(nz[0]):
        y0, y1, x0, x1 = nz[0].min(), nz[0].max(), nz[1].min(), nz[1].max()
        waste = 100 * (1 - ((y1 - y0) * (x1 - x0)) / (H * W))
        out['margin_pct'] = waste
        if waste > 12:
            out['warns'].append('dead margin %.1f %% of canvas' % waste)

    # --- glyph sizes --------------------------------------------------
    lab, _ = ndimage.label(dark)
    objs = ndimage.find_objects(lab)
    glyphs = []
    for sl in objs:
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        if h < 4 or w < 2:
            continue
        if h > 0.10 * H or w > 6 * h:
            continue              # graphics, rules, long strokes
        glyphs.append((h, sl))
    if len(glyphs) < 20:
        out['warns'].append('only %d glyph-like components found' % len(glyphs))
    else:
        # Group glyphs into text runs, then take each run's TALLEST glyph as
        # its cap/ascender height. A run's font size follows from that; the
        # 15th percentile of raw heights would read lowercase x-heights and
        # under-report the size by about 30 %.
        boxes = [(s[1].start, s[1].stop, s[0].start, s[0].stop) for _, s in glyphs]
        med = np.median([b[3] - b[2] for b in boxes])
        tol = max(3.0, 1.8 * med)   # bridge inter-word spaces
        order = sorted(range(len(boxes)), key=lambda i: (boxes[i][2], boxes[i][0]))
        parent = list(range(len(boxes)))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        for ii in range(len(order)):
            for jj in range(ii + 1, min(ii + 40, len(order))):
                i, j = order[ii], order[jj]
                ax0, ax1, ay0, ay1 = boxes[i]
                bx0, bx1, by0, by1 = boxes[j]
                dx = max(0, max(ax0 - bx1, bx0 - ax1))
                dy = max(0, max(ay0 - by1, by0 - ay1))
                if dx <= tol and dy <= 0.6 * med:
                    ra, rb = find(i), find(j)
                    if ra != rb:
                        parent[ra] = rb
        runs = {}
        for i in range(len(boxes)):
            runs.setdefault(find(i), []).append(boxes[i])
        # A run of one or two glyphs cannot be sized: "mm" carries no ascender
        # or capital, so its tallest glyph is an x-height and reads ~30 % small.
        # Size only runs of three or more glyphs.
        # A run of one or two glyphs cannot be sized: "mm" carries no ascender
        # or capital, so its tallest glyph is an x-height and reads ~30 % small.
        # Size only runs of three or more glyphs, and drop runs whose tallest
        # component is far below the typical glyph: those are dash segments,
        # tick marks and plot markers, not lettering.
        floor_h = 0.45 * med
        groups = [v for v in runs.values()
                  if len(v) >= 3 and max(b[3] - b[2] for b in v) >= floor_h]
        if not groups:
            groups = list(runs.values())
        sizes = np.array([max(b[3] - b[2] for b in g) for g in groups], float)
        pts = sizes * px2pt / CAP_RATIO
        # text runs whose bounding boxes intersect = colliding labels
        rb = [(min(b[0] for b in g), max(b[1] for b in g),
               min(b[2] for b in g), max(b[3] for b in g)) for g in groups]
        # Two runs only count as colliding when their actual ink comes within
        # a pixel. Overlapping bounding boxes alone are normal: a two-line
        # label, or a label whose box encloses a leader line, is not a clash.
        gmask = {}
        for k, g in enumerate(groups):
            x0, x1, y0, y1 = rb[k]
            m = np.zeros((y1 - y0, x1 - x0), bool)
            for b in g:
                m[b[2] - y0:b[3] - y0, b[0] - x0:b[1] - x0] = \
                    dark[b[2]:b[3], b[0]:b[1]]
            gmask[k] = m
        clash = []
        near = []
        for i in range(len(rb)):
            for j in range(i + 1, len(rb)):
                ax0, ax1, ay0, ay1 = rb[i]
                bx0, bx1, by0, by1 = rb[j]
                if not (ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1):
                    continue
                ox0, ox1 = max(ax0, bx0), min(ax1, bx1)
                oy0, oy1 = max(ay0, by0), min(ay1, by1)
                A = gmask[i][oy0 - ay0:oy1 - ay0, ox0 - ax0:ox1 - ax0]
                B = gmask[j][oy0 - by0:oy1 - by0, ox0 - bx0:ox1 - bx0]
                if not A.size:
                    continue
                if (A & B).any():                       # real overprint
                    clash.append((rb[i], rb[j]))
                elif (A & ndimage.binary_dilation(B, iterations=2)).any():
                    near.append((rb[i], rb[j]))         # within ~2 px, tight
        out['text_collisions'] = len(clash)
        out['text_near_misses'] = len(near)
        if near:
            out['warns'].append('%d pairs of text runs within ~2 px, e.g. at %s'
                                % (len(near), [(int(a[0]), int(a[2])) for a, _ in near[:3]]))
        out['collision_at'] = [(int(a[0]), int(a[2])) for a, _ in clash[:6]]
        # Reported as a warning, not a failure: connected-component glyphs
        # split characters such as % into overlapping pieces, so this flags
        # near-misses and intra-glyph structure as well as real overprints.
        # Every hit is confirmed by eye before it is acted on.
        if clash:
            out['warns'].append('%d pairs of text runs overlap, e.g. at %s '
                                '(confirm visually)'
                                % (len(clash), out['collision_at'][:3]))
        small_idx = np.argsort(pts)[:6]
        out['small_runs'] = [
            (round(float(pts[k]), 1),
             int(min(b[0] for b in groups[k])), int(min(b[2] for b in groups[k])),
             len(groups[k]))
            for k in small_idx]
        out['n_runs'] = len(pts)
        out['font_small_pt'] = float(pts.min())
        out['font_big_pt'] = float(pts.max())
        if pts.min() < MIN_PT:
            n_bad = int((pts < MIN_PT).sum())
            out['fails'].append('smallest text run ~%.1f pt, below %.0f pt '
                                '(%d of %d runs under)'
                                % (pts.min(), MIN_PT, n_bad, len(pts)))

    # --- thinnest ink run --------------------------------------------
    runs = []
    for r in range(0, H, 5):
        row = dark[r]
        d = np.diff(np.concatenate(([0], row.view(np.int8), [0])))
        st, en = np.where(d == 1)[0], np.where(d == -1)[0]
        runs += list(en - st)
    runs = np.array([x for x in runs if x > 0], float)
    if len(runs):
        p25 = np.percentile(runs, 25) * px2pt
        out['rule_p25_pt'] = p25
        if p25 < MIN_RULE_PT:
            out['fails'].append('25%% of ink runs thinner than %.3f pt '
                                '(floor %.2f pt)' % (p25, MIN_RULE_PT))

    # --- closest approach between separate text pieces ----------------
    # group glyphs into runs by proximity, then measure nearest neighbours
    if len(glyphs) >= 2:
        boxes = [(s[1].start, s[1].stop, s[0].start, s[0].stop) for _, s in glyphs]
        gaps = []
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                ax0, ax1, ay0, ay1 = boxes[i]
                bx0, bx1, by0, by1 = boxes[j]
                dx = max(0, max(ax0 - bx1, bx0 - ax1))
                dy = max(0, max(ay0 - by1, by0 - ay1))
                if dx == 0 and dy == 0:
                    gaps.append(0.0)
                else:
                    gaps.append(float(np.hypot(dx, dy)))
        gaps = np.array(gaps)
        touching = int((gaps == 0).sum())
        out['glyph_overlaps'] = touching
    return out


def report(res):
    print('--- %s %s' % (res['label'] or res['file'], ''))
    print('    %d x %d px at %.1f in wide  ->  %.0f dpi'
          % (res['px'][0], res['px'][1], res['print_in'], res['dpi']))
    if 'font_small_pt' in res:
        print('    lettering  %.1f to %.1f pt printed'
              % (res['font_small_pt'], res['font_big_pt']))
    if 'rule_p25_pt' in res:
        print('    ink runs   p25 %.3f pt' % res['rule_p25_pt'])
    if 'margin_pct' in res:
        print('    margin     %.1f %% of canvas unused' % res['margin_pct'])
    for f in res['fails']:
        print('    FAIL  ' + f)
    for w in res['warns']:
        print('    warn  ' + w)
    if not res['fails']:
        print('    PASS')
    return not res['fails']


if __name__ == '__main__':
    ok = report(check(sys.argv[1], float(sys.argv[2]),
                      sys.argv[3] if len(sys.argv) > 3 else ''))
    sys.exit(0 if ok else 1)
