import math
import csv
import os

# --- 1. PRE-LOADED DENSITIES (From your Parameters.tex) ---
densities = {
    "PPS_0Wt": 1.3500,
    "Pb": { 5: 1.4122, 10: 1.4804, 15: 1.5556, 20: 1.6387, 25: 1.7313, 30: 1.8350 },
    "BaSO4": { 5: 1.3990, 10: 1.4516, 15: 1.5084, 20: 1.5698, 25: 1.6364, 30: 1.7089 },
    "W": { 5: 1.4158, 10: 1.4884, 15: 1.5688, 20: 1.6584, 25: 1.7589, 30: 1.8723 },
    "Bi2O3": { 5: 1.4098, 10: 1.4751, 15: 1.5468, 20: 1.6258, 25: 1.7134, 30: 1.8109 },
    "Ti3C2O2": { 5: 1.4027, 10: 1.4597, 15: 1.5216, 20: 1.5889, 25: 1.6625, 30: 1.7432 }
}

def get_density(mat_name):
    if mat_name == "PPS_0Wt": return densities["PPS_0Wt"]
    parts = mat_name.split("_")
    filler = parts[0]
    wt = int(parts[1].replace("Wt", ""))
    return densities[filler][wt]

# --- 2. PARSE THE PERFECT NIST TEXT FILE ---
def load_nist_data(filepath):
    nist_dict = {} # Key: (Material, Energy_keV), Value: Target Mu (cm-1)
    current_mat = None
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            
            # Detect Material Header (e.g., Pb_30Wt)
            if "_" in line and "Wt" in line and len(line.split()) == 1:
                current_mat = line
                continue
                
            # Parse Data Rows
            cols = line.split()
            if len(cols) == 8 and current_mat:
                try:
                    energy_mev = float(cols[0])
                    energy_kev = round(energy_mev * 1000, 1) # Convert back to keV
                    mu_rho = float(cols[7]) # 8th column is Total Attenuation w/ Coherent
                    
                    # Calculate Theoretical Mu (LAC)
                    density = get_density(current_mat)
                    target_mu = mu_rho * density
                    
                    nist_dict[(current_mat, energy_kev)] = target_mu
                except ValueError:
                    continue
    return nist_dict

# --- 3. COMPARE GEANT4 VS NIST ---
def analyze_results(geant4_file, nist_dict, output_csv):
    results = []
    
    if not os.path.exists(geant4_file):
        print(f"[!] Simulation file {geant4_file} not found yet. Run this after Geant4 finishes!")
        return

    with open(geant4_file, 'r') as f:
        for line in f:
            if "|" not in line or "Energy" in line or "---" in line: continue
                
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 6:
                try:
                    energy = float(parts[0])
                    mat = parts[1]
                    thick_mm = float(parts[2])
                    i_0 = int(parts[3])
                    i_sim = int(parts[4])
                    
                    # 1. Geant4 Simulated Mu
                    thick_cm = thick_mm / 10.0
                    sim_mu = -math.log(i_sim / i_0) / thick_cm if i_sim > 0 else float('inf')
                    
                    # 2. NIST Theoretical Data
                    nist_mu = nist_dict.get((mat, energy), "N/A")
                    nist_i = "N/A"
                    error = "N/A"
                    
                    if nist_mu != "N/A":
                        # Calculate theoretical NIST I using Beer-Lambert
                        nist_i = int(i_0 * math.exp(-nist_mu * thick_cm))
                        
                        # Calculate Percentage Error between Sim Mu and NIST Mu
                        if sim_mu != float('inf'):
                            error = abs(sim_mu - nist_mu) / nist_mu * 100
                            error = round(error, 4)
                        
                    results.append({
                        "Energy (keV)": energy,
                        "Material": mat,
                        "Thickness (mm)": thick_mm,
                        "I_0 (Fired)": i_0,
                        "Simulated I": i_sim,
                        "Theoretical NIST I": nist_i,
                        "Simulated LAC (cm-1)": round(sim_mu, 5) if sim_mu != float('inf') else "Infinite",
                        "NIST LAC (cm-1)": round(nist_mu, 5) if nist_mu != "N/A" else "N/A",
                        "Error (%)": error
                    })
                except ValueError:
                    continue

    # --- 4. EXPORT TO CSV ---
    headers = ["Energy (keV)", "Material", "Thickness (mm)", "I_0 (Fired)", "Simulated I", "Theoretical NIST I", "Simulated LAC (cm-1)", "NIST LAC (cm-1)", "Error (%)"]
    with open(output_csv, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"\n✅ Analysis complete! 📊 Results saved to: {output_csv}")

# --- RUN DIRECTORY ---
if __name__ == "__main__":
    nist_data = load_nist_data("NIST Updated Values.txt")
    analyze_results("Phase1_Master_Dataset.txt", nist_data, "Final_Publication_Data.csv")