"""Phase 1 control runs: TiC and rutile TiO2 at 30 wt %.

These two compounds sit outside the 31-material design matrix. They were run to
separate the contribution of titanium content from any contribution of the
two-dimensional carbide itself, and are reported in Table 7 of the manuscript.

Run from the build directory, beside the compiled ./shielding executable:

    python3 run_controls.py       # 60 runs, 2 materials x 6 energies x 5 thicknesses

Writes Controls_Master_Dataset.txt and nothing else. The script refuses to start
if that file already exists, and aborts on the first run whose material name is
not found in the Geant4 material table, so a silent fallback to the PPS baseline
cannot be written to disk.
"""
import subprocess, re, os, math, sys

energies_keV = [59.5, 356, 511, 662, 1173, 1332]
materials = ["TiC_30Wt", "TiO2_30Wt"]
thicknesses_mm = [2, 4, 6, 8, 10]
photons_to_fire = 10000000

txt_filename = "Controls_Master_Dataset.txt"
if os.path.exists(txt_filename):
    sys.exit("%s already exists, move it aside first" % txt_filename)

total_runs = len(materials) * len(energies_keV) * len(thicknesses_mm)
with open(txt_filename, "w") as f:
    f.write("Phase 1 Controls: Titanium Compounds at 30 wt %\n")
    f.write(f"Photons Fired per run: {photons_to_fire} | Total Runs: {total_runs}\n")
    f.write("=" * 115 + "\n")
    f.write(f"{'Energy (keV)':<15} | {'Material':<15} | {'Thickness (mm)':<15} | {'I_0':<10} | {'I':<10} | {'Ratio (I/I_0)':<15} | {'Abs. Poisson Error'}\n")
    f.write("-" * 115 + "\n")

print(f"Starting {total_runs} control runs with {photons_to_fire} histories each...")
done = 0
for energy in energies_keV:
    print(f"\n--- {energy} keV ---")
    for mat in materials:
        for thick in thicknesses_mm:
            done += 1
            print(f"[{done}/{total_runs}] {mat} at {thick} mm ({energy} keV)...")
            with open("temp_controls.mac", "w") as f:
                f.write(f"/shielding/setMaterial {mat}\n")
                f.write(f"/shielding/setThickness {thick} mm\n")
                f.write("/run/initialize\n")
                f.write(f"/gun/energy {energy} keV\n")
                f.write(f"/run/beamOn {photons_to_fire}\n")

            result = subprocess.run(["./shielding", "temp_controls.mac"],
                                    capture_output=True, text=True)
            out, err = result.stdout, result.stderr

            if "not found" in out or "does not exist in the table" in out:
                print("\n[!] MATERIAL NOT FOUND for %s. Aborting." % mat)
                sys.exit(1)

            i0 = re.search(r"Primary Photons Fired \(I_0\):\s+(\d+)", out)
            iv = re.search(r"Surviving Photons \(I\):\s+(\d+)", out)
            if not (i0 and iv):
                print("\n[!] Geant4 failed on %s at %d mm, %s keV" % (mat, thick, energy))
                print(err or out)
                sys.exit(1)

            i_0_val, i_val = int(i0.group(1)), int(iv.group(1))
            ratio_val = i_val / i_0_val if i_0_val else 0.0
            poisson = (math.sqrt(i_val) / i_0_val) if i_val > 0 else 0.0
            ratio_str = f"{ratio_val:.6f}" if ratio_val >= 1e-4 else f"{ratio_val:.3e}"
            with open(txt_filename, "a") as f:
                f.write(f"{str(energy):<15} | {mat:<15} | {str(thick):<15} | {str(i_0_val):<10} | {str(i_val):<10} | {ratio_str:<15} | {poisson:.8f}\n")

if os.path.exists("temp_controls.mac"):
    os.remove("temp_controls.mac")
print(f"\nDONE. {total_runs} runs written to {txt_filename}")
