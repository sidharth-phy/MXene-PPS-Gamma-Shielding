"""Check data/phase2/Phase2_Data_Validated.txt against the counts it was derived
from and against the NIST/XCOM reference file.

Run from the repository root:

    python3 analysis/verify_phase2_derived.py

Phase2_Data_Validated.txt is a derived file. It repeats the eight columns of
Phase2_Master_Dataset.txt unchanged and adds eight more: the per-thickness
linear and mass attenuation coefficients, the five-thickness averages, the
NIST/XCOM reference values, and the signed deviations from them. Figures 11,
13, 14 and 15, and the merit tables, are drawn from those added columns, so
this script recomputes every one of them from the counts and the reference
file and reports the largest disagreement.

    LinAttCoeff  = -ln(I/I0) / x          x in cm
    MassAttCoeff = LinAttCoeff / rho
    Avg*         = mean over the five thicknesses of one material and energy
    *_%err       = (simulated - NIST) / NIST * 100

Rows where complete attenuation left no transmitted count carry N/A and are
counted separately. Nothing is written: the script only reports.
"""

import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MASTER = os.path.join(ROOT, "data", "phase2", "Phase2_Master_Dataset.txt")
VALID = os.path.join(ROOT, "data", "phase2", "Phase2_Data_Validated.txt")
NIST = os.path.join(ROOT, "data", "reference", "NIST_XCOM_values.txt")

# Composite densities, as produced by analysis/composite_density.py. The two
# controls are carried at 30 wt% only, which is how Phase 2 ran them.
DENS = {
    "PPS_0Wt": 1.3500,
    "Pb": {5: 1.4122, 10: 1.4804, 15: 1.5556, 20: 1.6387, 25: 1.7313, 30: 1.8350},
    "BaSO4": {5: 1.3990, 10: 1.4516, 15: 1.5084, 20: 1.5698, 25: 1.6364, 30: 1.7089},
    "W": {5: 1.4158, 10: 1.4884, 15: 1.5688, 20: 1.6584, 25: 1.7589, 30: 1.8723},
    "Bi2O3": {5: 1.4098, 10: 1.4751, 15: 1.5468, 20: 1.6258, 25: 1.7134, 30: 1.8109},
    "Ti3C2O2": {5: 1.4027, 10: 1.4597, 15: 1.5216, 20: 1.5889, 25: 1.6625, 30: 1.7432},
}
# The two bulk references Phase 2 ran beside the composites, at the Geant4 NIST
# material densities.
BULK = {"G4_Pb": 11.3500, "G4_W": 19.3000}

HEADER_RE = re.compile(r"^(\d+)\s+(Pb|W|BaSO4|Bi2O3|Ti3C2O2|TiC|TiO2)(\s+\(control\))?$")
ANY_BLOCK_RE = re.compile(r"^\d+\s+\S")
TOTAL_WITH_COHERENT = 6


def density(mat):
    if mat == "PPS_0Wt":
        return DENS["PPS_0Wt"]
    if mat in BULK:
        return BULK[mat]
    filler, wt = mat.split("_")
    return DENS[filler][int(wt.replace("Wt", ""))]


def read_table(path):
    """Return (header_cells, [row_cells]) for a pipe-delimited table."""
    head, rows = None, []
    for raw in open(path):
        if "|" not in raw:
            continue
        cells = [c.strip() for c in raw.split("|")]
        if head is None:
            head = cells
            continue
        if not re.match(r"^[\d.]+$", cells[0]):
            continue
        rows.append(cells)
    return head, rows


def read_nist(path):
    out, current = {}, None
    for raw in open(path):
        line = raw.strip()
        if not line:
            continue
        if line == "100% PPS":
            current = "PPS_0Wt"
            continue
        m = HEADER_RE.match(line)
        if m:
            current = "{}_{}Wt".format(m.group(2), m.group(1))
            continue
        if ANY_BLOCK_RE.match(line) and "\t" not in line:
            current = None
            continue
        cols = line.split("\t")
        if len(cols) != 8 or current is None:
            continue
        try:
            vals = [float(c) for c in cols]
        except ValueError:
            continue
        out[(current, round(vals[0] * 1000.0, 1))] = vals[TOTAL_WITH_COHERENT]
    return out


def main():
    _, master = read_table(MASTER)
    _, valid = read_table(VALID)
    nist = read_nist(NIST)

    if len(master) != len(valid):
        sys.exit("row counts differ: master %d, validated %d" % (len(master), len(valid)))

    # 1. the first eight columns must be the master file, unchanged
    def same(a, b):
        # the two files print the energy column differently, 356 against 356.0
        for x, y in zip(a, b):
            if x == y:
                continue
            try:
                if float(x) == float(y):
                    continue
            except ValueError:
                pass
            return False
        return True

    carried = 0
    for m, v in zip(master, valid):
        if not same(m[:8], v[:8]):
            sys.exit("row does not match the master dataset:\n  %s\n  %s" % (m, v))
        carried += 1

    # 2. per-row coefficients
    worst = {k: (0.0, None) for k in ("LAC", "MAC", "LAC_%err", "MAC_%err")}
    na = 0
    groups = {}
    for v in valid:
        energy, mat, thick = float(v[0]), v[1], float(v[2])
        i0, i = float(v[3]), float(v[4])
        if v[8] == "N/A" or i <= 0:
            na += 1
            continue
        lac = -math.log(i / i0) / (thick / 10.0)
        mac = lac / density(mat)
        for key, got, want in (("LAC", float(v[8]), lac), ("MAC", float(v[9]), mac)):
            d = abs(got - want) / abs(want)
            if d > worst[key][0]:
                worst[key] = (d, "%s %g keV %g mm" % (mat, energy, thick))
        groups.setdefault((mat, energy), []).append(lac)

    # 3. five-thickness averages and the deviations from NIST
    worst_avg = (0.0, None)
    worst_nist = (0.0, None)
    worst_err = (0.0, None)
    checked_groups = 0
    no_ref = set()
    for v in valid:
        energy, mat = float(v[0]), v[1]
        key = (mat, energy)
        if key not in groups:
            continue
        avg_lac = sum(groups[key]) / len(groups[key])
        avg_mac = avg_lac / density(mat)
        for got, want in ((float(v[10]), avg_lac), (float(v[11]), avg_mac)):
            d = abs(got - want) / abs(want)
            if d > worst_avg[0]:
                worst_avg = (d, "%s %g keV" % (mat, energy))
        ref_mac = nist.get((mat, energy))
        if ref_mac is None:
            # the two bulk metals are not in the composite XCOM file
            no_ref.add(mat)
            continue
        ref_lac = ref_mac * density(mat)
        # The NIST columns are stored rounded, the linear one to four decimals,
        # so they are checked in absolute terms against the product of the XCOM
        # mass coefficient and the composite density.
        for got, want in ((float(v[12]), ref_lac), (float(v[13]), ref_mac)):
            d = abs(got - want)
            if d > worst_nist[0]:
                worst_nist = (d, "%s %g keV" % (mat, energy))
        err_pairs = []
        if v[14] != "N/A":
            # The deviation columns are per row, against that row's own
            # coefficient, not against the five-point average, and against the
            # rounded reference as printed beside them.
            file_lac, file_mac = float(v[12]), float(v[13])
            err_pairs = [(float(v[14]), (float(v[8]) - file_lac) / file_lac * 100.0),
                         (float(v[15]), (float(v[9]) - file_mac) / file_mac * 100.0)]
        # the deviation columns are a difference of two rounded numbers and sit
        # near zero, so they are judged in percentage points, not relatively
        for got, want in err_pairs:
            d = abs(got - want)
            if d > worst_err[0]:
                worst_err = (d, "%s %g keV" % (mat, energy))
        checked_groups += 1

    print("rows carried unchanged from the master dataset : %d" % carried)
    print("rows with N/A (complete attenuation)           : %d" % na)
    print("material-energy groups checked                 : %d" % len(groups))
    if no_ref:
        print("no XCOM block, NIST columns not checked        : %s"
              % ", ".join(sorted(no_ref)))
    print()
    print("largest relative disagreement, recomputed against deposited")
    print("  per-row LinAttCoeff   %.3e   %s" % worst["LAC"])
    print("  per-row MassAttCoeff  %.3e   %s" % worst["MAC"])
    print("  five-point averages   %.3e   %s" % worst_avg)
    print("  NIST reference columns %.3e   %s  (absolute)" % worst_nist)
    print("  deviation columns     %.3e pp %s" % worst_err)
    tol = 5e-5
    if (max(worst["LAC"][0], worst["MAC"][0], worst_avg[0]) > tol
            or worst_nist[0] > 5e-5 or worst_err[0] > 0.01):
        sys.exit("\nFAIL: a derived column does not follow from the counts "
                 "within %.0e relative." % tol)
    print("\nPASS: every derived column follows from the deposited counts and "
          "the XCOM reference, to within the rounding of the printed columns.")


if __name__ == "__main__":
    main()
