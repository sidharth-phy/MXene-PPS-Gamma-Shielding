# Gamma-ray shielding of Ti3C2O2 MXene / PPS composites

Geant4 source code, run automation and datasets for the two-phase Monte Carlo study of
oxygen-terminated Ti3C2O2 MXene in a polyphenylene sulphide (PPS) matrix, benchmarked
against Pb, W, BaSO4 and Bi2O3 fillers.

Everything needed to reproduce the linear and mass attenuation coefficients reported in
the manuscript is in this repository.

## What was simulated

Thirty-one composite formulations (pure PPS plus five fillers at 5, 10, 15, 20, 25 and
30 wt %), five specimen thicknesses (2, 4, 6, 8 and 10 mm) and six photon energies
(59.5, 356, 511, 662, 1173 and 1332 keV), at 10^7 primary photon histories per run.

| | Phase 1 | Phase 2 |
|---|---|---|
| Geometry | vacuum, zero-divergence pencil beam | lab replica: lead collimators, 3" x 3" NaI(Tl), graded-Z castle |
| Scoring | transmitted primary count | total energy deposited in the crystal, Gaussian-broadened |
| Production runs | 930 | 930 |
| Calibration runs (G4_Pb, G4_W) | 60 | 60 |
| Air baselines | not required | 6 |
| Total | 990 | 996 |

Grand total 1,986 runs.

## Layout

```
phase1-narrow-beam/     Geant4 application for the ideal narrow-beam geometry
phase2-digital-twin/    Geant4 application for the laboratory digital twin
analysis/               Material property and comparison scripts
data/                   Reference cross-sections and simulation output
```

### phase1-narrow-beam

`shielding.cc` with `src/` and `include/`, a `CMakeLists.txt`, visualisation macros under
`macros/`, and `run_phase1.py` which drives the 930-run production campaign by writing a
temporary macro per run and parsing the transmitted count from stdout.

Scoring is in `src/SteppingAction.cc`. All secondaries are killed at creation, and a
primary is counted only if it reaches the detector plane having lost under 0.1 keV and
with a momentum z-component above 0.999999, which enforces the narrow-beam condition
assumed by the Beer-Lambert law and by the NIST/XCOM tabulations.

### phase2-digital-twin

The same absorber set inside a modelled laboratory. `src/DetectorConstruction.cc` builds
the lead primary collimator (10 x 10 x 5 cm, 3 mm bore), the sample disc, the secondary
collimator downstream of the sample (10 x 10 x 3 cm, 5 mm bore), a 0.5 mm aluminium
entrance window, a 76.2 x 76.2 mm NaI crystal and the Al / Cu / Sn / Pb lateral shells.

`src/EventAction.cc` accumulates energy deposited in the crystal and applies Gaussian
broadening with FWHM = 2.06 sqrt(E) keV. `src/RunAction.cc` writes a 1 keV-per-bin
spectrum from 0 to 1499 keV. `run_phase2.py` integrates each spectrum over a +/- 2 sigma
window about the photopeak and divides by the air-baseline count for that energy.

Note that the primary is a zero-divergence pencil beam fired along the collimator bore
axis, adopted for computational economy. No primary strikes the collimator body.

### analysis

| Script | Produces |
|---|---|
| `composite_density.py` | Composite densities from the inverse rule of mixtures |
| `elemental_fractions.py` | Elemental mass fractions for the Geant4 `AddElement` calls |
| `effective_atomic_number.py` | Z_eff by Mayneord's power law, m = 2.94 |
| `lab_mass_recipe.py` | Masses of filler and matrix for a 50 mm x 2 mm disc |
| `nist_comparison.py` | Regenerates `data/phase1/Phase1_Validation_Dataset.csv` from the master dataset and the NIST/XCOM reference |

`composite_density.py` takes filler densities of Pb 11.34, BaSO4 4.50, W 19.25,
Bi2O3 8.90 and Ti3C2O2 5.44 g/cm3, with PPS at 1.35 g/cm3. These are the values that
produced the composite densities hard-coded in both `DetectorConstruction.cc` files.

The elemental mass fractions in the two applications were entered independently and agree
to four decimals, with a difference of one unit in the fourth decimal for nine of the
thirty composites, which comes from rounding. A few sets sum to 1.0000 +/- 0.0001 rather
than exactly to unity, which Geant4 renormalises and reports as a warning. The induced
difference in attenuation is of order one part in ten thousand. The files are left as they
were run, so that the deposited code is the code that produced the deposited data.

### data

`reference/NIST_XCOM_values.txt` holds NIST/XCOM mass attenuation coefficients for all
31 composites at the six energies. The eight columns are photon energy, coherent
scattering, incoherent scattering, photoelectric absorption, pair production in the
nuclear field, pair production in the electron field, total attenuation with coherent
scattering and total attenuation without coherent scattering. Column 7, the total with
coherent scattering, is the column used throughout, because the Phase 1 counter rejects
coherently scattered photons along with every other interaction.

`phase1/` holds the 930-row production dataset, the 60-row calibration dataset and the
derived validation CSV carrying per-thickness and averaged coefficients alongside the
NIST values. `phase2/` holds the 990-row photopeak dataset.

`Phase1_Validation_Dataset.csv` is regenerated by `analysis/nist_comparison.py`, which
recomputes every coefficient from the integer counts in the master dataset and compares
it against the full-precision mixture-rule benchmark. Column definitions: `Ratio (I/I_0)`
is the transmitted fraction, `Abs. sigma(T)` is sqrt(I)/I_0, `LAC_sim` and `MAC_sim` are
the per-thickness coefficients, `Avg LAC_sim` and `Avg MAC_sim` are the five-point means
that the manuscript reports, and the two `% Error` columns are signed deviations of those
means from the NIST/XCOM values. `Abs. Poisson Error` in the master datasets is the same
quantity as `Abs. sigma(T)`.

The 996 individual Phase 2 spectrum CSVs are about 11 MB and are not in this repository.
They can be regenerated by running `run_phase2.py`, or requested from the corresponding
author.

## Building

```bash
source /path/to/geant4-install/bin/geant4.sh
cd phase1-narrow-beam
mkdir build && cd build
cmake .. && make -j$(nproc)
```

Then run the campaign from the build directory:

```bash
python3 run_phase1.py                 # 930 production runs
python3 run_phase1.py --calibration   # 60 calibration runs on G4_Pb and G4_W
```

The build copies `run_phase1.py` and the visualisation macros next to the executable, so
no manual copying is needed.

Phase 2 builds the same way. Run `quick_check_phase2.py` first, which executes four short
cases and reports the photopeak windows, before committing to the full campaign.

## Environment

Geant4 11.3.2, physics list FTFP_BERT with the electromagnetic component replaced by
G4EmLivermorePhysics, which in Geant4 11.x drives the Livermore photon models from the
G4EMLOW data library derived from the EPICS2017 evaluation. Default production cuts
throughout, which for the FTFP_BERT reference list is a range cut of 0.7 mm. Runs were
executed single-threaded.

No random number seed is set anywhere in this code, so every run starts the default
Geant4 engine from the same state and the campaign is exactly repeatable. One consequence
is that the five thickness runs for a given material and energy replay the same primary
photon sequence, so they are not independent samples.

## How the coefficients were extracted

A coefficient was computed at each of the five thicknesses as mu = ln(I0/I)/x, and the
five values were averaged. Each per-thickness value is anchored at the origin by
construction, since I equals I0 at zero thickness. The reported coefficient is that mean,
not a fitted regression slope.

In Phase 1, I0 is the number of primaries fired and carries no counting uncertainty. In
Phase 2, I0 is the photopeak integral from an air-disc baseline run at the same energy:
8,271,445 at 59.5 keV, 8,392,067 at 356 keV, 6,913,935 at 511 keV, 5,828,808 at 662 keV,
3,835,531 at 1173 keV and 3,487,416 at 1332 keV.

## Citation

If you use this code or these datasets, please cite the associated manuscript. See
`CITATION.cff`.

## Licence

MIT. See `LICENSE`.
