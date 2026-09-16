"""
Compare the Phase 1 simulated attenuation coefficients against the NIST/XCOM
mixture-rule benchmark and regenerate data/phase1/Phase1_Validation_Dataset.csv.

Run from the repository root:

    python3 analysis/nist_comparison.py

Optional arguments:

    python3 analysis/nist_comparison.py <nist_file> <phase1_master_file> <output_csv>

Notes on the benchmark column. The XCOM block for each material carries eight
columns: photon energy, coherent scattering, incoherent scattering,
photoelectric absorption, pair production in the nuclear field, pair production
in the electron field, total attenuation WITH coherent scattering, and total
attenuation WITHOUT coherent scattering. Column 7 (index 6) is the one used
throughout this study, because the Phase 1 counter rejects coherently scattered
photons along with every other interaction, so the simulated quantity is the
total interaction coefficient including coherent scattering.
"""

import csv
import math
import os
import re
import sys

# --- 1. Composite densities, as produced by analysis/composite_density.py ---
densities = {
    "PPS_0Wt": 1.3500,
    "Pb": {5: 1.4122, 10: 1.4804, 15: 1.5556, 20: 1.6387, 25: 1.7313, 30: 1.8350},
    "BaSO4": {5: 1.3990, 10: 1.4516, 15: 1.5084, 20: 1.5698, 25: 1.6364, 30: 1.7089},
    "W": {5: 1.4158, 10: 1.4884, 15: 1.5688, 20: 1.6584, 25: 1.7589, 30: 1.8723},
    "Bi2O3": {5: 1.4098, 10: 1.4751, 15: 1.5468, 20: 1.6258, 25: 1.7134, 30: 1.8109},
    "Ti3C2O2": {5: 1.4027, 10: 1.4597, 15: 1.5216, 20: 1.5889, 25: 1.6625, 30: 1.7432},
}

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_NIST = os.path.join(ROOT, "data", "reference", "NIST_XCOM_values.txt")
DEFAULT_MASTER = os.path.join(ROOT, "data", "phase1", "Phase1_Master_Dataset.txt")
DEFAULT_OUT = os.path.join(ROOT, "data", "phase1", "Phase1_Validation_Dataset.csv")

# Column 7 of the XCOM block, zero-indexed, is total attenuation with coherent
# scattering. Column 8 (index 7) excludes coherent scattering and is not used.
TOTAL_WITH_COHERENT = 6

HEADER_RE = re.compile(r"^(\d+)\s+(Pb|W|BaSO4|Bi2O3|Ti3C2O2)$")


def get_density(mat_name):
    if mat_name == "PPS_0Wt":
        return densities["PPS_0Wt"]
    filler, wt = mat_name.split("_")
    return densities[filler][int(wt.replace("Wt", ""))]


def load_nist_data(filepath):
    """Return {(material, energy_keV): (mass_coeff_cm2_per_g, linear_coeff_cm-1)}."""
    nist = {}
    current = None
    with open(filepath, "r") as f:
        for raw in f:
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
            cols = line.split("\t")
            if len(cols) != 8 or current is None:
                continue
            try:
                vals = [float(c) for c in cols]
            except ValueError:
                continue
            energy_kev = round(vals[0] * 1000.0, 1)
            mass_coeff = vals[TOTAL_WITH_COHERENT]
            nist[(current, energy_kev)] = (mass_coeff, mass_coeff * get_density(current))
    expected = 31 * 6
    if len(nist) != expected:
        raise RuntimeError(
            "parsed {} NIST entries, expected {}. Check the reference file format.".format(
                len(nist), expected))
    return nist


def load_master(filepath):
    """Return {(material, energy_keV): {thickness_mm: (I0, I)}} from the Phase 1 master file."""
    runs = {}
    with open(filepath, "r") as f:
        for raw in f:
            if "|" not in raw:
                continue
            parts = [p.strip() for p in raw.split("|")]
            if len(parts) < 7 or not re.match(r"^[\d.]+$", parts[0]):
                continue
            energy = float(parts[0])
            mat = parts[1]
            thick = float(parts[2])
            i0 = int(parts[3])
            i = int(parts[4])
            runs.setdefault((mat, energy), {})[thick] = (i0, i)
    return runs


def analyse(nist, runs, output_csv):
    headers = [
        "Energy (keV)", "Material", "Thickness (mm)", "I_0", "I", "Ratio (I/I_0)",
        "Abs. sigma(T)", "LAC_sim (cm-1)", "MAC_sim (cm2/g)", "Avg LAC_sim (cm-1)",
        "LAC_NIST (cm-1)", "% Error LAC", "Avg MAC_sim (cm2/g)", "MAC_NIST (cm2/g)",
        "% Error MAC",
    ]
    rows = []
    for (mat, energy) in sorted(runs, key=lambda k: (k[1], k[0])):
        series = runs[(mat, energy)]
        if (mat, energy) not in nist:
            continue
        mac_nist, lac_nist = nist[(mat, energy)]
        density = get_density(mat)
        per_thickness = {}
        for thick, (i0, i) in series.items():
            if i <= 0:
                continue
            per_thickness[thick] = -math.log(i / i0) / (thick / 10.0)
        if not per_thickness:
            continue
        avg_lac = sum(per_thickness.values()) / len(per_thickness)
        avg_mac = avg_lac / density
        err_lac = (avg_lac - lac_nist) / lac_nist * 100.0
        err_mac = (avg_mac - mac_nist) / mac_nist * 100.0
        for thick in sorted(series):
            i0, i = series[thick]
            ratio = i / i0
            rows.append({
                "Energy (keV)": energy,
                "Material": mat,
                "Thickness (mm)": thick,
                "I_0": i0,
                "I": i,
                "Ratio (I/I_0)": "{:.6f}".format(ratio),
                "Abs. sigma(T)": "{:.8f}".format(math.sqrt(i) / i0 if i > 0 else 0.0),
                "LAC_sim (cm-1)": "{:.8f}".format(per_thickness.get(thick, float("nan"))),
                "MAC_sim (cm2/g)": "{:.8f}".format(per_thickness.get(thick, float("nan")) / density),
                "Avg LAC_sim (cm-1)": "{:.8f}".format(avg_lac),
                "LAC_NIST (cm-1)": "{:.4f}".format(lac_nist),
                "% Error LAC": "{:.4f}".format(err_lac),
                "Avg MAC_sim (cm2/g)": "{:.8f}".format(avg_mac),
                "MAC_NIST (cm2/g)": "{:.5f}".format(mac_nist),
                "% Error MAC": "{:.4f}".format(err_mac),
            })

    with open(output_csv, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    deviations = sorted({(r["Material"], r["Energy (keV)"]): abs(float(r["% Error LAC"]))
                         for r in rows}.items(), key=lambda kv: kv[1])
    mean_dev = sum(v for _, v in deviations) / len(deviations)
    worst_key, worst = deviations[-1]
    print("Wrote {} rows to {}".format(len(rows), output_csv))
    print("Material-energy combinations: {}".format(len(deviations)))
    print("Mean absolute deviation from NIST/XCOM: {:.4f} %".format(mean_dev))
    print("Largest deviation: {:.4f} % for {} at {} keV".format(worst, worst_key[0], worst_key[1]))


if __name__ == "__main__":
    nist_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_NIST
    master_file = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MASTER
    out_file = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_OUT
    nist_data = load_nist_data(nist_file)
    master = load_master(master_file)
    analyse(nist_data, master, out_file)
