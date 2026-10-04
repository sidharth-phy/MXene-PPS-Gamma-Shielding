# Figure scripts

Every schematic figure in the manuscript is produced by one of these scripts. They take no
input beyond the constants written in the manuscript and in the Geant4 geometry source, so each
figure can be regenerated and checked against the geometry it claims to show.

| Script | Figure | Source of the numbers it draws |
|---|---|---|
| `fig1.py` | Figure 1, Ti3C2O2 monolayer | in-plane constant 3.083 A and monolayer thickness 5.808 A, Section 2.5.2 of the manuscript |
| `fig2.py` | Figure 2, Phase 1 narrow-beam geometry | `phase1-narrow-beam/src/DetectorConstruction.cc` and `PrimaryGeneratorAction.cc` |
| `fig3.py` | Figure 3, Phase 2 side elevation | `phase2-digital-twin/src/DetectorConstruction.cc` |
| `fig4.py` | Figure 4, Phase 2 sections normal to the beam | `phase2-digital-twin/src/DetectorConstruction.cc` |

Run any of them with `python3 figures/figN.py`. Output is a 500 dpi PNG in the working directory.
`render_all.py` runs all four and writes a vector PDF beside each PNG, which is the form most
journals ask for at typesetting. Only `matplotlib` and `numpy` are needed.

The figures are plotted output rather than generated images: every coordinate in them
is computed from the constants listed above.
