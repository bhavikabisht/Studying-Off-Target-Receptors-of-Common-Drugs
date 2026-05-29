import os
import sys
import subprocess
import numpy as np

# --- SETTINGS & PATHS ---
DRUG_FILE = "diphenhydramine.sdf"
FLEXX_CMD = "/home/ibab/Downloads/flexx-6.4.1-Linux-x64/flexx"
HYDE_CMD = "/home/ibab/Downloads/hydescorer-2.4.1-Linux-x64/hydescorer"

# --- THE MASTER LICENSE FIX ---
my_env = os.environ.copy()
my_env["BIOSOLVE_LICENSE_FILE"] = "61822@192.168.4.184"
my_env["BIOSOLVEIT_LICENSE_FILE"] = "61822@192.168.4.184"
my_env["LM_LICENSE_FILE"] = "61822@192.168.4.184"  # The variable that finally worked!

def get_pdb_center(file_path):
    """Calculates the geometric center of an fpocket output file."""
    coords = []
    if not os.path.exists(file_path): return None
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith("ATOM  ") or line.startswith("HETATM"):
                try:
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    coords.append([x, y, z])
                except ValueError:
                    continue
    return np.mean(coords, axis=0) if coords else None

def process_protein(pdb_path):
    protein_id = os.path.basename(pdb_path).replace(".pdb", "")
    out_dir = f"tmp_{protein_id}"
    fpocket_out_dir = pdb_path.replace(".pdb", "_out")
    
    try:
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        
        # 1. RUN FPOCKET
        subprocess.run(["fpocket", "-f", pdb_path], check=True, capture_output=True)
        
        # 2. GET BEST POCKET
        best_pocket_file = os.path.join(fpocket_out_dir, "pockets", "pocket1_atm.pdb")
        p_center = get_pdb_center(best_pocket_file)
        
        if p_center is None:
            subprocess.run(["rm", "-rf", out_dir, fpocket_out_dir])
            return f"{protein_id},Error: No Pockets Found,Error\n"
            
        best_pocket_coords = f"{p_center[0]:.3f},{p_center[1]:.3f},{p_center[2]:.3f},15.0"

        # 3. DOCK & SCORE
        dock_out = os.path.join(out_dir, "dock.sdf")
        hyde_out = os.path.join(out_dir, "scored.sdf")
        
        # Pass the master license environment to FlexX and HYDE
        subprocess.run([FLEXX_CMD, "-i", DRUG_FILE, "-p", pdb_path, "-c", best_pocket_coords, "-o", dock_out], env=my_env, check=True, capture_output=True)
        subprocess.run([HYDE_CMD, "-i", dock_out, "-p", pdb_path, "-o", hyde_out], env=my_env, check=True, capture_output=True)

        # 4. EXTRACT RESULTS
        affinity = "N/A"
        category = "Error"
        if os.path.exists(hyde_out):
            with open(hyde_out, 'r') as f:
                content = f.read()
                if "HYDE_ESTIMATED_AFFINITY_LOWER_BOUNDARY" in content:
                    val_str = content.split("HYDE_ESTIMATED_AFFINITY_LOWER_BOUNDARY")[1].split("\n")[1].strip()
                    affinity_val = float(val_str)
                    affinity = str(affinity_val)
                    
                    if affinity_val < 5000:
                        category = "Strong Off-Target Hit"
                    elif affinity_val <= 100000:
                        category = "Moderate Binder (H1-like)"
                    else:
                        category = "Non-Binder"

        # 5. CLEAN UP
        subprocess.run(["rm", "-rf", out_dir, fpocket_out_dir])
        return f"{protein_id},{affinity},{category}\n"

    except subprocess.CalledProcessError as e:
        subprocess.run(["rm", "-rf", out_dir, fpocket_out_dir])
        return f"{protein_id},Error: FlexX/HYDE Failed (Exit Status {e.returncode}),Error\n"
    except Exception as e:
        subprocess.run(["rm", "-rf", out_dir, fpocket_out_dir])
        return f"{protein_id},Error: {str(e)},Error\n"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(process_protein(sys.argv[1]), end="")
