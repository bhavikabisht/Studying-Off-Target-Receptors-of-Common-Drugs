import os
import sys
import subprocess

# --- SETTINGS ---
DRUG_FILE = "diphenhydramine.sdf"
DOGSITE_CMD = "/home/ibab/Downloads/dogsitescorer-2.0.0-Linux-x64/dogsitescorer-2.0.0/dogsite"
FLEXX_CMD = "flexx"
HYDE_CMD = "hydescorer"

def process_protein(pdb_path):
    protein_id = os.path.basename(pdb_path).replace(".pdb", "")
    out_dir = f"tmp_{protein_id}"
    
    try:
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        
        # 1. RUN DOGSITESCORER
        subprocess.run([DOGSITE_CMD, "-i", pdb_path, "-o", out_dir], check=True, capture_output=True)
        
        # 2. PARSE DESCRIPTORS FOR THE BEST POCKET (P_0)
        desc_file = os.path.join(out_dir, f"{protein_id}_descriptors.txt")
        best_pocket_coords = None
        
        if os.path.exists(desc_file):
            with open(desc_file, 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    header = [h.lower() for h in lines[0].strip().split()]
                    try:
                        # Find where X, Y, Z coordinates are stored in the file
                        x_idx = header.index("center_x")
                        y_idx = header.index("center_y")
                        z_idx = header.index("center_z")
                        
                        for line in lines[1:]:
                            # P_0 is always ranked as the most 'druggable' primary pocket
                            if line.startswith("P_0"):
                                parts = line.strip().split()
                                best_pocket_coords = f"{parts[x_idx]},{parts[y_idx]},{parts[z_idx]},15.0"
                                break
                    except ValueError:
                        return f"{protein_id},Error: Descriptor format mismatch,Error\n"

        if not best_pocket_coords:
            return f"{protein_id},Error: No Pockets Found,Error\n"

        # 3. DOCK & SCORE IN POCKET 0
        dock_out = os.path.join(out_dir, "dock.sdf")
        hyde_out = os.path.join(out_dir, "scored.sdf")
        
        subprocess.run([FLEXX_CMD, "-i", DRUG_FILE, "-p", pdb_path, "-c", best_pocket_coords, "-o", dock_out], check=True, capture_output=True)
        subprocess.run([HYDE_CMD, "-i", dock_out, "-p", pdb_path, "-o", hyde_out], check=True, capture_output=True)

        # 4. EXTRACT nM RESULT AND CATEGORIZE
        affinity = "N/A"
        category = "Error"
        if os.path.exists(hyde_out):
            with open(hyde_out, 'r') as f:
                content = f.read()
                if "HYDE_ESTIMATED_AFFINITY_LOWER_BOUNDARY" in content:
                    val_str = content.split("HYDE_ESTIMATED_AFFINITY_LOWER_BOUNDARY")[1].split("\n")[1].strip()
                    affinity_val = float(val_str)
                    affinity = str(affinity_val)
                    
                    # Categorize based on your H1 baseline (77,000 nM)
                    if affinity_val < 5000:
                        category = "Strong Off-Target Hit"
                    elif affinity_val <= 100000:
                        category = "Moderate Binder (H1-like)"
                    else:
                        category = "Non-Binder"

        # 5. CLEAN UP
        subprocess.run(["rm", "-rf", out_dir])
        return f"{protein_id},{affinity},{category}\n"

    except Exception as e:
        subprocess.run(["rm", "-rf", out_dir])
        return f"{protein_id},Error: {str(e)},Error\n"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(process_protein(sys.argv[1]), end="")
