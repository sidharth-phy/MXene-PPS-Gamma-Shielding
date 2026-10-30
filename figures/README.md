# Figure scripts

Every figure in the manuscript is produced by one of these scripts. The four schematic
figures take no input beyond the constants written in the manuscript and in the Geant4
geometry source, apart from one drawing constant in `fig1.py`, the separation between the
titanium and oxygen planes. The rest read the deposited datasets, so each figure can be
regenerated and checked against the data it claims to show.

| Script | Figures | Output file names | Reads |
|---|---|---|---|
| `fig1.py` | 1, Ti3C2O2 monolayer | `Figure1_Ti3C2O2_structure` | in-plane constant 3.083 A and monolayer thickness 5.808 A, Section 2.5.2 of the manuscript |
| `fig2.py` | 2, Phase 1 narrow-beam geometry | `Figure2_Phase1_schematic` | `phase1-narrow-beam/src/DetectorConstruction.cc` and `PrimaryGeneratorAction.cc` |
| `fig3.py` | 3, Phase 2 side elevation | `Figure3_Phase2_schematic` | `phase2-digital-twin/src/DetectorConstruction.cc` |
| `fig4.py` | 4, Phase 2 sections normal to the beam | `Figure4_Phase2_sections` | `phase2-digital-twin/src/DetectorConstruction.cc` |
| `fig_series.py` | 5 to 10, Beer-Lambert series | `Figure5_series_59.5keV` to `Figure10_series_1332keV` | `data/phase2/Phase2_Master_Dataset.txt` |
| `fig_summary.py` | 11, 12, 23 and 24 | `NIST_Overlay_Plot`, `Validation_Error_BarChart`, `Z_eff_vs_Weight`, `MXene_Enhancement_Factor` | `data/phase2/Phase2_Data_Validated.txt`, except Figure 23 which is computed in the script |
| `fig_spectra.py` | 13 to 18, transmitted spectra | `Final_Plot_59p5keV` to `Final_Plot_1332keV` | `data/phase2/spectra/` |
| `fig_lac_loading.py` | 19, LAC against filler loading | `Efficiency_Curves_Canvas` | `data/phase2/Phase2_Data_Validated.txt` |
| `fig_hvl_rpe.py` | 20, 21 and 22 | `MAC_vs_Energy`, `HVL_vs_Energy`, `RPE_at_10mm` | `data/phase2/Phase2_Data_Validated.txt` |

Run any of them with `python3 figures/<script>.py`. Each takes an optional input path and an
optional output directory, in that order, and falls back to the deposited dataset and the
working directory when neither is given. Output is a PNG at the resolution the script sets.

`render_all.py` runs all nine scripts and writes a vector PDF beside each PNG, which is the
form most journals ask for at typesetting. From a clean clone, with no arguments anywhere,
it writes all 24 figures of the manuscript. Only `matplotlib`, `numpy` and `pandas` are
needed.

## Two things worth stating plainly

The scripts for Figures 11 to 24 were written during the analysis and used hard-coded
absolute paths on the author's machine. For this deposit the input file and the output
directory come from the command line instead, with the deposited data as the default.

Three further changes were made, all of them to presentation, none to a computed quantity.
`fig_hvl_rpe.py` applied a `ScalarFormatter` to the x axis of Figures 20 and 21 after the
tick labels had already been set, which discarded them and regenerated them from the tick
positions, so the first energy printed as 60 rather than 59.5. Those two lines are removed,
and the axis now prints the energies it was given. `fig_spectra.py` drew its legend inside
the axes; it is now below them in three columns, which is where the published Figures 13 to
18 carry it. Nothing else in any script has been altered: every plotted value, colour,
scale, limit and label text is as it was.

`fig_summary.py` is a reconstruction. The revision of it that rendered the published
Figures 11 and 12 was lost, and the surviving earlier copy drew those two panels with an
older title and legend. The reconstruction restores them, and running it regenerates both
figures with the same title, axis labels, tick labels, legend text and layout, colours and
plotted values as the published versions. It is not claimed to be byte-identical: the
deposited version leaves slightly more whitespace between the x-axis label and the legend,
which makes the saved canvas a few per cent taller. Figures 23 and 24, drawn by the same
script, reproduce the published versions exactly. Figure dimensions also shift by a few
pixels between matplotlib versions, since font metrics differ, so a reader comparing against
the published images should compare the plotted values and not the pixel count.

The scripts were written with the assistance of Claude (Anthropic), as recorded in the
manuscript's declaration of generative AI use. The figures themselves are plotted output, not
generated images: every coordinate in them is computed from the constants and datasets listed
above.
