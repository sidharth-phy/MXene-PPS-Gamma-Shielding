"""
run_phase2.py  —  ShieldingExactTwin Phase 2 Campaign (996 runs)
================================================================
Material sweep:
  Air baseline (6 energies, no sample)
  PPS 100%                       →  5 thicknesses × 6 energies  =  30 runs
  Pure Pb (100%)                 →  5 × 6                       =  30 runs
  Pure W  (100%)                 →  5 × 6                       =  30 runs
  Ti3C2O2/PPS composites (×6)   →  6 × 5 × 6                   = 180 runs
  Pb/PPS  composites (×6)       →  6 × 5 × 6                   = 180 runs
  W/PPS   composites (×6)       →  6 × 5 × 6                   = 180 runs
  BaSO4/PPS composites (×6)     →  6 × 5 × 6                   = 180 runs
  Bi2O3/PPS composites (×6)     →  6 × 5 × 6                   = 180 runs
  ─────────────────────────────────────────────────────────────────
  Total:  6 + 990 = 996 runs  @ 10,000,000 histories each

Energies (keV):    59.5, 356, 511, 662, 1173, 1332
Thicknesses (mm):  2, 4, 6, 8, 10
"""

import subprocess
import os
import sys
import math

# ─────────────────────────────────────────────────────────────────────────────
# 1.  MASTER PARAMETERS
# ─────────────────────────────────────────────────────────────────────────────
HISTORIES      = 10_000_000
ENERGIES_KEV   = [59.5, 356, 511, 662, 1173, 1332]
THICKNESSES_MM = [2, 4, 6, 8, 10]
EXECUTABLE     = "./shielding"
MACRO_FILE     = "temp_p2.mac"
OUTPUT_DIR     = "spectra"
RESULTS_FILE   = "Phase2_Master_Dataset.txt"

# NaI(Tl) empirical resolution: FWHM(E) = NIST_A × √E_keV
# NIST_A = 2.06 keV^0.5 gives 8.0% FWHM at 662 keV (validated for 3"×3")
NIST_A  = 2.06   # keV^0.5
N_SIGMA = 2.0    # integration window half-width in sigma (captures 95.4% of peak)

# ─────────────────────────────────────────────────────────────────────────────
# 2.  MATERIAL DEFINITIONS
#     (geant4_name, display_label)
#     geant4_name must exactly match a material registered in DefineMaterials()
# ─────────────────────────────────────────────────────────────────────────────
MATERIALS = [

    # ── Pure polymer baseline ─────────────────────────────────────────────
    ("PPS_0Wt",          "Pure PPS"),

    # ── Pure heavy metal reference blocks ─────────────────────────────────
    # These answer: what does a SOLID 2–10 mm disc of pure Pb or W achieve?
    # Provides the theoretical upper bound for shielding performance.
    ("G4_Pb",            "Pure Pb (100%)"),
    ("G4_W",             "Pure W  (100%)"),

    # ── Ti3C2O2 (MXene) / PPS composites ─────────────────────────────────
    ("Ti3C2O2_5Wt",      "MXene  5Wt%"),
    ("Ti3C2O2_10Wt",     "MXene 10Wt%"),
    ("Ti3C2O2_15Wt",     "MXene 15Wt%"),
    ("Ti3C2O2_20Wt",     "MXene 20Wt%"),
    ("Ti3C2O2_25Wt",     "MXene 25Wt%"),
    ("Ti3C2O2_30Wt",     "MXene 30Wt%"),

    # ── Pb / PPS composites ───────────────────────────────────────────────
    ("Pb_5Wt",           "Pb  5Wt%"),
    ("Pb_10Wt",          "Pb 10Wt%"),
    ("Pb_15Wt",          "Pb 15Wt%"),
    ("Pb_20Wt",          "Pb 20Wt%"),
    ("Pb_25Wt",          "Pb 25Wt%"),
    ("Pb_30Wt",          "Pb 30Wt%"),

    # ── W / PPS composites ────────────────────────────────────────────────
    ("W_5Wt",            "W   5Wt%"),
    ("W_10Wt",           "W  10Wt%"),
    ("W_15Wt",           "W  15Wt%"),
    ("W_20Wt",           "W  20Wt%"),
    ("W_25Wt",           "W  25Wt%"),
    ("W_30Wt",           "W  30Wt%"),

    # ── BaSO4 / PPS composites ────────────────────────────────────────────
    # BaSO4: ρ=4.50 g/cm³, high Ba content (Z=56) provides good mid-Z shielding
    # Also used medically as X-ray contrast agent — non-toxic, of research interest
    ("BaSO4_5Wt",        "BaSO4  5Wt%"),
    ("BaSO4_10Wt",       "BaSO4 10Wt%"),
    ("BaSO4_15Wt",       "BaSO4 15Wt%"),
    ("BaSO4_20Wt",       "BaSO4 20Wt%"),
    ("BaSO4_25Wt",       "BaSO4 25Wt%"),
    ("BaSO4_30Wt",       "BaSO4 30Wt%"),

    # ── Bi2O3 / PPS composites ────────────────────────────────────────────
    # Bi2O3: ρ=8.90 g/cm³, Bi (Z=83) has very high photoelectric cross-section
    # near-equivalent to Pb (Z=82) but non-toxic — strong radiation shielding candidate
    ("Bi2O3_5Wt",        "Bi2O3  5Wt%"),
    ("Bi2O3_10Wt",       "Bi2O3 10Wt%"),
    ("Bi2O3_15Wt",       "Bi2O3 15Wt%"),
    ("Bi2O3_20Wt",       "Bi2O3 20Wt%"),
    ("Bi2O3_25Wt",       "Bi2O3 25Wt%"),
    ("Bi2O3_30Wt",       "Bi2O3 30Wt%"),
]

# Verify count matches expectation (33 materials × 5 thicknesses × 6 energies + 6 baselines)
assert len(MATERIALS) == 33, f"Expected 33 materials, got {len(MATERIALS)}"

# ─────────────────────────────────────────────────────────────────────────────
# 3.  HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def fwhm_keV(energy_keV: float) -> float:
    """Empirical NaI(Tl) FWHM in keV — valid for 3"×3" Saint-Gobain detector."""
    return NIST_A * math.sqrt(energy_keV)


def peak_window(energy_keV: float) -> tuple:
    """Return (lo, hi) bin indices for photopeak integration (±N_SIGMA sigma)."""
    sigma = fwhm_keV(energy_keV) / 2.355
    lo = max(0,    int(energy_keV - N_SIGMA * sigma))
    hi = min(1499, int(energy_keV + N_SIGMA * sigma))
    return lo, hi


def read_spectrum(csv_path: str) -> list:
    """Read Geant4 spectrum CSV → list of 1500 integer counts (1 keV/bin)."""
    spectrum = [0] * 1500
    if not os.path.exists(csv_path):
        return spectrum
    with open(csv_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) == 2:
                try:
                    bin_idx = int(parts[0])
                    counts  = int(parts[1])
                    if 0 <= bin_idx < 1500:
                        spectrum[bin_idx] = counts
                except ValueError:
                    continue
    return spectrum


def integrate_peak(spectrum: list, energy_keV: float) -> int:
    """Sum counts inside the photopeak window."""
    lo, hi = peak_window(energy_keV)
    return sum(spectrum[lo:hi+1])


def poisson_rel_err(counts: int) -> float:
    """Relative Poisson uncertainty: 1/√N if N>0, else 0."""
    return 1.0 / math.sqrt(counts) if counts > 0 else 0.0


def csv_filename(mat_name: str, thickness_mm: int, energy_keV: float) -> str:
    """Deterministic CSV path for a given (material, thickness, energy) triple."""
    e_str = str(energy_keV).replace(".", "p")
    safe  = mat_name.replace("_", "").replace(".", "")
    return os.path.join(OUTPUT_DIR, f"spec_{safe}_{thickness_mm}mm_{e_str}keV.csv")


def baseline_filename(energy_keV: float) -> str:
    """CSV path for the air baseline at a given energy."""
    e_str = str(energy_keV).replace(".", "p")
    return os.path.join(OUTPUT_DIR, f"spec_BASELINE_{e_str}keV.csv")


# ─────────────────────────────────────────────────────────────────────────────
# 4.  GEANT4 RUN FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def run_geant4(mat_name: str, thickness_mm: int,
               energy_keV: float, out_csv: str) -> bool:
    """
    Write macro, execute Geant4, return True on success.

    MACRO ORDER — critical:
      /output/setFile          (set output CSV filename)
      /shielding/setMaterial   (store material name as string)
      /shielding/setThickness  (store thickness value)
      /run/initialize          (calls Construct() → DefineMaterials() → ConstructVolumes())
                               Material pointer is resolved INSIDE ConstructVolumes(),
                               after the material table is fully populated. This is the
                               fix for the silent material lookup failure.
      /gun/energy              (set source energy for this run)
      /run/beamOn              (fire HISTORIES events)
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    macro = (
        f"/output/setFile        {out_csv}\n"
        f"/shielding/setMaterial  {mat_name}\n"
        f"/shielding/setThickness {thickness_mm} mm\n"
        f"/run/initialize\n"
        f"/gun/energy             {energy_keV} keV\n"
        f"/run/beamOn             {HISTORIES}\n"
    )

    with open(MACRO_FILE, "w") as f:
        f.write(macro)

    result = subprocess.run(
        [EXECUTABLE, MACRO_FILE],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"\n[!] GEANT4 ERROR: {mat_name} {thickness_mm}mm {energy_keV}keV")
        print(result.stderr[-2000:] if result.stderr else result.stdout[-2000:])
        return False

    if not os.path.exists(out_csv):
        print(f"\n[!] OUTPUT MISSING: {out_csv}")
        print("    Geant4 ran but no CSV was written. Check RunAction::EndOfRunAction.")
        return False

    return True


# ─────────────────────────────────────────────────────────────────────────────
# 5.  MAIN CAMPAIGN LOOP
# ─────────────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    n_baselines   = len(ENERGIES_KEV)
    n_sample_runs = len(MATERIALS) * len(THICKNESSES_MM) * len(ENERGIES_KEV)
    total_runs    = n_baselines + n_sample_runs
    run_idx       = 0

    print(f"\n{'='*70}")
    print(f"  Phase 2 Campaign: {total_runs} total runs "
          f"({n_baselines} baseline + {n_sample_runs} sample)")
    print(f"  {len(MATERIALS)} materials × {len(THICKNESSES_MM)} thicknesses "
          f"× {len(ENERGIES_KEV)} energies  =  {n_sample_runs} sample runs")
    print(f"  Histories per run: {HISTORIES:,}")
    print(f"{'='*70}")

    # ── STEP A: Baseline runs (G4_AIR disc — effectively no absorber) ──────
    baseline_peaks = {}   # {energy_keV: I0_counts}
    print(f"\n{'='*70}")
    print(f"  PHASE 2 — Baseline runs (I0 for each energy)")
    print(f"{'='*70}")

    for energy in ENERGIES_KEV:
        run_idx += 1
        csv_path = baseline_filename(energy)
        lo, hi   = peak_window(energy)
        print(f"  [{run_idx}/{total_runs}] Baseline @ {energy:7.1f} keV "
              f"(window [{lo}–{hi}] keV) ...", end=" ", flush=True)

        if run_geant4("G4_AIR", 2, energy, csv_path):
            I0 = integrate_peak(read_spectrum(csv_path), energy)
            baseline_peaks[energy] = I0
            print(f"I0 = {I0:,}")
        else:
            print("FAILED — stopping.")
            sys.exit(1)

    # ── STEP B: Sample runs ────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  PHASE 2 — Sample runs")
    print(f"{'='*70}")

    # Initialise results file
    COL = [15, 22, 14, 12, 12, 13, 14, 14]
    header = (f"{'Energy(keV)':<{COL[0]}} | "
              f"{'Material':<{COL[1]}} | "
              f"{'Thickness(mm)':<{COL[2]}} | "
              f"{'I0':<{COL[3]}} | "
              f"{'I':<{COL[4]}} | "
              f"{'I/I0':<{COL[5]}} | "
              f"{'RelErr(I0)':<{COL[6]}} | "
              f"{'RelErr(I)':<{COL[7]}}")
    SEP = "=" * sum(COL + [len(COL)*3])

    with open(RESULTS_FILE, "w") as f:
        f.write("Phase 2: ShieldingExactTwin — NaI(Tl) Photopeak Master Dataset\n")
        f.write(f"Total runs: {total_runs}  |  "
                f"Histories/run: {HISTORIES:,}  |  "
                f"Materials: {len(MATERIALS)}\n")
        f.write(f"Peak integration: ±{N_SIGMA}σ  |  "
                f"NaI resolution: FWHM = {NIST_A}×√E_keV keV\n")
        f.write(f"RelErr = 1/√N (relative Poisson uncertainty)\n")
        f.write(SEP + "\n")
        f.write(header + "\n")
        f.write("-" * len(SEP) + "\n")

    # ── Sample loop ────────────────────────────────────────────────────────
    for energy in ENERGIES_KEV:
        I0      = baseline_peaks[energy]
        lo, hi  = peak_window(energy)
        sigma   = fwhm_keV(energy) / 2.355

        print(f"\n  ── {energy} keV  |  window [{lo}–{hi}] keV  |  "
              f"σ={sigma:.1f} keV  |  I0={I0:,} ──")

        for mat_name, label in MATERIALS:
            for thick in THICKNESSES_MM:
                run_idx  += 1
                csv_path  = csv_filename(mat_name, thick, energy)

                print(f"  [{run_idx}/{total_runs}] {mat_name:<22} "
                      f"{thick:>2}mm {energy:>7}keV ...",
                      end=" ", flush=True)

                if not run_geant4(mat_name, thick, energy, csv_path):
                    print("FAILED — stopping.")
                    sys.exit(1)

                I        = integrate_peak(read_spectrum(csv_path), energy)
                ratio    = I / I0 if I0 > 0 else 0.0
                err_I0   = poisson_rel_err(I0)
                err_I    = poisson_rel_err(I)

                print(f"I={I:>9,}  I/I0={ratio:.5f}")

                row = (f"{str(energy):<{COL[0]}} | "
                       f"{mat_name:<{COL[1]}} | "
                       f"{str(thick):<{COL[2]}} | "
                       f"{str(I0):<{COL[3]}} | "
                       f"{str(I):<{COL[4]}} | "
                       f"{ratio:<{COL[5]}.6f} | "
                       f"{err_I0:<{COL[6]}.8f} | "
                       f"{err_I:<{COL[7]}.8f}\n")

                with open(RESULTS_FILE, "a") as f:
                    f.write(row)

    # ── Cleanup ────────────────────────────────────────────────────────────
    if os.path.exists(MACRO_FILE):
        os.remove(MACRO_FILE)

    print(f"\n{'='*70}")
    print(f"  ALL {run_idx} RUNS COMPLETE")
    print(f"  Results  → {RESULTS_FILE}")
    print(f"  Spectra  → {OUTPUT_DIR}/  ({n_sample_runs + n_baselines} CSV files)")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
    
