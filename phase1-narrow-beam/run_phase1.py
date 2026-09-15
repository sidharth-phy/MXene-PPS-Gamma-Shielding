import subprocess
import re
import os
import math
import sys

# The Master Parameters
energies_keV = [59.5, 356, 511, 662, 1173, 1332]
materials = [
    "PPS_0Wt", 
    "Pb_5Wt", "Pb_10Wt", "Pb_15Wt", "Pb_20Wt", "Pb_25Wt", "Pb_30Wt",
    "BaSO4_5Wt", "BaSO4_10Wt", "BaSO4_15Wt", "BaSO4_20Wt", "BaSO4_25Wt", "BaSO4_30Wt",
    "W_5Wt", "W_10Wt", "W_15Wt", "W_20Wt", "W_25Wt", "W_30Wt",
    "Bi2O3_5Wt", "Bi2O3_10Wt", "Bi2O3_15Wt", "Bi2O3_20Wt", "Bi2O3_25Wt", "Bi2O3_30Wt",
    "Ti3C2O2_5Wt", "Ti3C2O2_10Wt", "Ti3C2O2_15Wt", "Ti3C2O2_20Wt", "Ti3C2O2_25Wt", "Ti3C2O2_30Wt"
]

# 10^7 histories for statistical precision
photons_to_fire = 10000000 

txt_filename = "Phase1_Master_Dataset.txt"

# Set up the TXT file with a clean, readable header
with open(txt_filename, mode='w') as file:
    file.write("Phase 1: Comprehensive Shielding Master Data\n")
    file.write(f"Photons Fired per run: {photons_to_fire} | Total Runs: 930\n")
    file.write("=" * 115 + "\n")
    file.write(f"{'Energy (keV)':<15} | {'Material':<15} | {'Thickness (mm)':<15} | {'I_0':<10} | {'I':<10} | {'Ratio (I/I_0)':<15} | {'Abs. Poisson Error'}\n")
    file.write("-" * 115 + "\n")

print(f"Starting Phase 1 Runs with {photons_to_fire} histories per run...")

for energy in energies_keV:
    print(f"\n--- INITIATING {energy} keV SPECTRUM ---")
    
    thicknesses_mm = [2, 4, 6, 8, 10]
    
    for mat in materials:
        for thick in thicknesses_mm:
            print(f"Running {mat} at {thick} mm ({energy} keV)...")

            with open("temp.mac", "w") as f:
                # FIX: Set the parameters FIRST, then initialize!
                f.write(f"/shielding/setMaterial {mat}\n")
                f.write(f"/shielding/setThickness {thick} mm\n")
                f.write("/run/initialize\n")
                f.write(f"/gun/energy {energy} keV\n")
                f.write(f"/run/beamOn {photons_to_fire}\n")

            # Capture both standard output AND standard error (crash logs)
            result = subprocess.run(["./shielding", "temp.mac"], capture_output=True, text=True)
            output = result.stdout
            error_log = result.stderr

            i_0_match = re.search(r"Primary Photons Fired \(I_0\):\s+(\d+)", output)
            i_match = re.search(r"Surviving Photons \(I\):\s+(\d+)", output)
            ratio_match = re.search(r"Transmission Ratio \(I/I_0\):\s+([\d.]+)", output)

            if ratio_match and i_match and i_0_match:
                i_val = int(i_match.group(1))
                i_0_val = int(i_0_match.group(1))
                ratio_val = float(ratio_match.group(1))

                poisson_error = (math.sqrt(i_val) / i_0_val) if i_val > 0 else 0.0

                with open(txt_filename, mode='a') as file:
                    file.write(f"{str(energy):<15} | {mat:<15} | {str(thick):<15} | {str(i_0_val):<10} | {str(i_val):<10} | {str(ratio_val):<15} | {poisson_error:.8f}\n")
            else:
                # DEBUG MODE: Expose the Geant4 Crash
                print(f"\n[!] CRITICAL ERROR: Geant4 failed to run {mat} at {thick}mm.")
                print("--- GEANT4 CRASH LOG ---")
                print(error_log)
                if not error_log.strip():
                    print(output) # Print standard output if error_log is empty
                print("------------------------")
                print("Stopping simulation so you can copy the error above.")
                sys.exit(1) # Stop the script immediately

# Clean up
if os.path.exists("temp.mac"):
    os.remove("temp.mac")

print(f"\nALL RUNS COMPLETE! Data secured in {txt_filename}")
