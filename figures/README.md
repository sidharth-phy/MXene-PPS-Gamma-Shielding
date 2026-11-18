# Figure scripts

Every one of the fifteen figures in the manuscript is produced by one of these scripts.
The four schematic figures take no input beyond the constants written in the manuscript
and in the Geant4 geometry source, apart from one drawing constant in `fig1.py`, the
separation between the titanium and oxygen planes. The rest read the deposited datasets,
so each figure can be regenerated and checked against the data it claims to show.

| Script | Figure | Output file | Reads |
|---|---|---|---|
| `fig1.py` | 1, Ti3C2O2 monolayer | `Figure1_Ti3C2O2_structure` | in-plane constant 3.083 A and monolayer thickness 5.808 A, Section 2.5.2 of the manuscript |
| `fig2.py` | 2, Phase 1 narrow-beam geometry | `Figure2_Phase1_schematic` | `phase1-narrow-beam/src/DetectorConstruction.cc` and `PrimaryGeneratorAction.cc` |
| `fig3.py` | 3, Phase 2 side elevation | `Figure3_Phase2_schematic` | `phase2-digital-twin/src/DetectorConstruction.cc` |
| `fig4.py` | 4, Phase 2 sections normal to the beam | `Figure4_Phase2_sections` | `phase2-digital-twin/src/DetectorConstruction.cc` |
| `fig_series.py` | 5 to 10, Beer-Lambert series at the six energies | `Figure5_series_59.5keV` to `Figure10_series_1332keV` | `data/phase2/Phase2_Master_Dataset.txt` |
| `fig_overlay_dev_stack.py` | 11, NIST/XCOM overlay and deviation | `Figure11` | `data/phase2/Phase2_Data_Validated.txt` |
| `fig_spectra_panel.py` | 12, transmitted spectra | `Figure12` | `data/phase2/spectra/` |
| `fig_lac_loading.py` | 13, LAC against filler loading | `Figure13` | `data/phase2/Phase2_Data_Validated.txt` |
| `fig_merit_panel.py` | 14, MAC, HVL and RPE | `Figure14` | `data/phase2/Phase2_Data_Validated.txt` |
| `fig_zeff_ef_panel.py` | 15, effective atomic number and enhancement | `Figure15` | `data/phase2/Phase2_Data_Validated.txt` |

## Running them

    mkdir -p build && cd build && python3 ../figures/render_all.py

`render_all.py` runs all ten scripts with no arguments, writes the fifteen PNGs and a
vector PDF beside each one, and then prepares the rasters for a publisher: it flattens the
alpha channel, which Elsevier's artwork guidance asks for, and rewrites each PNG's
resolution tag so the file states the width it is printed at rather than the width it was
rendered at. The printed widths are listed in `PRINT_WIDTH_IN` at the foot of that script
and match the `\includegraphics` widths in the manuscript source.

Any script can also be run on its own, `python3 figures/<script>.py`. Each takes an
optional input path and an optional output directory, in that order, and falls back to the
deposited dataset and the working directory when neither is given.

`matplotlib`, `numpy`, `pandas` and `pillow` are needed. `check_fig.py`, described below,
also needs `scipy`.

## Checking what came out

`check_fig.py` is the quality check used before submission. It takes a rendered PNG and
the width it will be printed at, and measures, at that printed size: effective resolution,
the smallest and largest lettering, the thinnest run of ink, unused margin, ink touching
the canvas edge, and the closest approach between separate pieces of text. The thresholds
are Elsevier's: 500 dpi for combination art, 7 pt minimum lettering, 0.25 pt minimum rule.

    python3 figures/check_fig.py build/Figure11.png 5.5 "Fig 11"

Three notes on reading its output. Hatch fill is broken by the connected-component pass
into fragments it cannot tell from small lettering, so Figures 11 and 14 report a spurious
2 to 3 pt run; with hatching suppressed Figure 11 passes. Rotated axis labels are measured
across the baseline rather than across the cap height, which leaves Figure 14 reporting a
spurious 6.9 pt run for the y-axis label of panel (a) even with the hatching suppressed;
measured the correct way across the glyph, that label runs 7.18 to 8.43 pt of cap height,
from a nominal 11.9 pt at the printed width. And the script reports the size of a whole
text run, not of a chemical subscript inside it, so the subscript figures below are not
read off it.

Measured at the widths the manuscript calls each figure in, ordinary lettering runs 7.85
to 10.26 pt and chemical subscripts, which matplotlib sets at 0.7 of the surrounding size,
run 6.02 to 7.18 pt. Every figure also clears 7 pt at 140 mm. Figures 2, 3 and 4 carry no
subscripts at all. Those margins are what the canvas size of each script is set for: with
a tight bounding box the printed size of the lettering follows the ratio of font size to
canvas, so the drawing area, not the font size alone, is what sets it.

## Typography

Every script pins its typography rather than inheriting the machine's matplotlib defaults:

    font.family      DejaVu Sans        ships with matplotlib, so it is present everywhere
    mathtext.fontset dejavusans         subscripts in the same face as the text around them
    pdf.fonttype     42                 TrueType, not the Type 3 that Elsevier rejects
    ps.fonttype      42

Without the first two lines a machine with a different default sans face redraws the
figures in that face, and mathtext stays in DejaVu regardless, which puts two typefaces in
one label. The pin is what makes these scripts redraw the published figures rather than
something close to them.

## Reproducibility

Rendering is deterministic: two runs of `render_all.py` in separate empty directories
produce byte-identical PNGs, and the fifteen PNGs produced from a clean copy of this
repository are pixel-identical to the fifteen submitted with the manuscript. The PDFs
carry a creation timestamp, so they are not byte-identical between runs; with the
`CreationDate` and `ModDate` entries normalised they are. Figure
dimensions can still shift by a few pixels between matplotlib versions, since font metrics
differ, so a reader comparing against a different version should compare plotted values
rather than pixel counts. The versions used for the submitted artwork are recorded in
`requirements.txt`.

## superseded/

`superseded/` holds the three scripts that drew the figures of the earlier, twenty-four
figure arrangement of this manuscript: `fig_summary.py`, `fig_spectra.py` and
`fig_hvl_rpe.py`. Those panels are now combined into Figures 11, 12, 14 and 15 by the four
panel scripts in the table above, which carry the same data and the same computation. The
old scripts are kept so the earlier figures can still be regenerated, and nothing in the
current manuscript is drawn by them.

The figures are plotted output, not generated images. Every coordinate in them is computed
from the constants and datasets listed above: the schematics from the geometry constants in
the Geant4 sources, and the data figures from the deposited datasets.
