"""
quick_check_phase2.py  —  Phase 2 sanity check before full campaign
====================================================================
Runs four cases, including a 59.5 keV air baseline:

  1. Baseline at 662 keV   (I0 for Cs-137 check)
  2. Baseline at 59.5 keV  (I0 for the Am-241 check)
  3. PPS_0Wt 2 mm at 662 keV  (lightest attenuator — expect ~97% ratio)
  4. Pb_30Wt 2 mm at 59.5 keV (heaviest attenuator — significant attenuation)

Run this from the BUILD directory (where ./shielding lives):
    cd build   # the directory holding the compiled ./shielding executable
    python3 quick_check_phase2.py

If all four look physically sensible, run run_phase2.py for the full campaign.
"""

import subprocess, os, math, sys

EXECUTABLE = "./shielding"
HISTORIES  = 500_000    # lighter for quick check
NIST_A     = 2.06       # keV^0.5  — NaI(Tl) empirical resolution constant
N_SIGMA    = 2.0

def fwhm(e):
    return NIST_A * math.sqrt(e)

def window(e):
    s = fwhm(e) / 2.355
    return max(0, int(e - N_SIGMA*s)), min(1499, int(e + N_SIGMA*s))

def read_csv(path):
    sp = [0] * 1500
    if not os.path.exists(path):
        return sp
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            p = line.strip().split(",")
            if len(p) == 2:
                try:
                    sp[int(p[0])] = int(p[1])
                except:
                    pass
    return sp

def run(mat, thick, energy, outfile):
    macro = (
        f"/output/setFile {outfile}\n"
        f"/shielding/setMaterial {mat}\n"
        f"/shielding/setThickness {thick} mm\n"
        f"/run/initialize\n"
        f"/gun/energy {energy} keV\n"
        f"/run/beamOn {HISTORIES}\n"
    )
    with open("qc.mac", "w") as f:
        f.write(macro)
    r = subprocess.run([EXECUTABLE, "qc.mac"], capture_output=True, text=True)
    if r.returncode != 0:
        print("ERROR:", r.stderr[-500:] or r.stdout[-500:])
        return False
    return True

os.makedirs("qc_spectra", exist_ok=True)

# ── 4-case check — BOTH energies have their own baselines ──────────────────
cases = [
    ("G4_AIR",  2, 662,  "qc_spectra/baseline_662.csv"),
    ("G4_AIR",  2, 59.5, "qc_spectra/baseline_59p5.csv"),
    ("PPS_0Wt", 2, 662,  "qc_spectra/PPS_2mm_662.csv"),
    ("Pb_30Wt", 2, 59.5, "qc_spectra/Pb30_2mm_59p5.csv"),
]

print("=" * 60)
print("  Phase 2 Quick Check  (500k histories each case)")
print("=" * 60)

spectra = {}
for mat, t, e, fp in cases:
    label = f"{mat} {t}mm {e}keV"
    print(f"\nRunning {label} ...", end=" ", flush=True)
    if not run(mat, t, e, fp):
        sys.exit(1)
    sp   = read_csv(fp)
    lo, hi = window(e)
    peak = sum(sp[lo:hi+1])
    peak_bin = sp.index(max(sp[lo:hi+1]), lo, hi+1) if peak > 0 else 0
    spectra[(mat, e)] = peak
    fw = fwhm(e)
    print(f"OK  |  window [{lo}-{hi}] keV  |  FWHM={fw:.1f} keV  "
          f"|  counts={peak:,}  |  peak_bin={peak_bin}")

print("\n" + "=" * 60)
print("  RESULTS SUMMARY")
print("=" * 60)

I0_662  = spectra.get(("G4_AIR",  662),  1)
I0_59p5 = spectra.get(("G4_AIR",  59.5), 1)   # its own measured baseline
I_PPS   = spectra.get(("PPS_0Wt", 662),  0)
I_Pb30  = spectra.get(("Pb_30Wt", 59.5), 0)

print(f"  Baseline I0 (662 keV):       {I0_662:>10,}")
print(f"  Baseline I0 (59.5 keV):      {I0_59p5:>10,}")  # now meaningful
print(f"  PPS_0Wt I  (662 keV, 2mm):  {I_PPS:>10,}  →  ratio = {I_PPS/I0_662:.4f}"
      f"  (expect ~0.96-0.98)")
print(f"  Pb_30Wt I  (59.5keV, 2mm):  {I_Pb30:>10,}  →  ratio = {I_Pb30/I0_59p5:.4f}"
      f"  (expect significant attenuation)")

print("\n  Physical expectation checks:")

# PPS at 662 keV (Beer-Lambert, μ from Phase 1 validated)
mu_pps_662 = 0.1081  # cm⁻¹
T_theory   = math.exp(-mu_pps_662 * 0.2)
ratio_pps  = I_PPS / I0_662 if I0_662 > 0 else 0
diff_pps   = abs(ratio_pps - T_theory) / T_theory * 100 if I0_662 > 0 else 999
print(f"  PPS 2mm at 662 keV — Beer-Lambert T: {T_theory:.4f}  "
      f"Observed: {ratio_pps:.4f}  Deviation: {diff_pps:.1f}%  "
      f"{'✓ OK' if diff_pps < 15 else '✗ CHECK GEOMETRY'}")

# Pb_30Wt at 59.5 keV — high attenuation expected
# μ(Pb at 59.5 keV) ≈ 22.5 cm⁻¹, Pb_30Wt effectively: ~0.30×22.5×(1.835/11.35) = 1.09 cm⁻¹
# For 0.2 cm: T ≈ exp(-1.09×0.2) ≈ 0.805  (rough estimate including PPS matrix)
ratio_pb30 = I_Pb30 / I0_59p5 if I0_59p5 > 0 else 0
print(f"  Pb_30Wt 2mm at 59.5 keV — Observed: {ratio_pb30:.4f}  "
      f"(T < 0.90 expected — Pb strongly attenuates at 59.5 keV)")

print()
print("  NOTE: Phase 2 values differ from Phase 1 because:")
print("   - Air attenuation (about 0.3 % over the 15.05 cm path at 59.5 keV)")
print("   - Collimator geometry filters some small-angle scatter")
print("   - Detector response (Gaussian broadening) affects peak integration")
print("  This is expected — Phase 2 simulates real lab conditions.")

if os.path.exists("qc.mac"):
    os.remove("qc.mac")

print("\nQuick check complete. If ratios are physically reasonable, run:")
print("  python3 run_phase2.py")
