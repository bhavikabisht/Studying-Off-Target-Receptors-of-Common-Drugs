# save as: fix_convert_poses.py
# Correctly extracts only MODE 1 from each Vina-GPU PDBQT

import os
import glob

GPU_DIR = "/home/ibab/Seesar_docking/SeeSAR_Final_Export"
OUT_DIR = "/home/ibab/Seesar_docking/reflig_sdfs"
os.makedirs(OUT_DIR, exist_ok=True)

def pdbqt_mode1_to_sdf(pdbqt_file, out_sdf):
    """Extract only MODE 1 from PDBQT and write minimal SDF"""
    atoms = []
    in_model1 = False
    
    with open(pdbqt_file) as f:
        for line in f:
            if line.startswith("MODEL        1") or \
               (line.startswith("REMARK") and not atoms and not in_model1):
                in_model1 = True
            if line.startswith("ENDMDL") and in_model1:
                break
            if in_model1 and line.startswith(("ATOM","HETATM")):
                try:
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    element = line[77:79].strip() or 'C'
                    atoms.append((x, y, z, element))
                except:
                    continue
    
    if not atoms:
        # No MODEL tag - take all ATOM lines
        with open(pdbqt_file) as f:
            for line in f:
                if line.startswith("ENDMDL"):
                    break
                if line.startswith(("ATOM","HETATM")):
                    try:
                        x = float(line[30:38])
                        y = float(line[38:46])
                        z = float(line[46:54])
                        element = line[77:79].strip() or 'C'
                        atoms.append((x, y, z, element))
                    except:
                        continue
    
    if not atoms:
        return False
    
    # Write SDF with just coordinates (no bonds needed for refligand)
    with open(out_sdf, 'w') as f:
        f.write("reference_ligand\n")
        f.write("  FlexX_ref\n\n")
        f.write(f"{len(atoms):3d}  0  0  0  0  0  0  0  0  0999 V2000\n")
        for x, y, z, elem in atoms:
            f.write(f"{x:10.4f}{y:10.4f}{z:10.4f} {elem:<3s} 0  0  0  0  0\n")
        f.write("M  END\n$$$$\n")
    return True

# Process all 2000
files = sorted(glob.glob(f"{GPU_DIR}/*.pdbqt"))
success = 0
failed  = 0

for pdbqt in files:
    pid = os.path.basename(pdbqt).replace("_gpu_pose.pdbqt","")
    out = f"{OUT_DIR}/{pid}_reflig.sdf"
    
    if os.path.exists(out) and os.path.getsize(out) > 50:
        success += 1
        continue
    
    if pdbqt_mode1_to_sdf(pdbqt, out):
        success += 1
    else:
        failed += 1
        print(f"  ❌ {pid}")

print(f"Done! Success: {success} | Failed: {failed}")
print(f"SDFs saved to: {OUT_DIR}")

# Quick verify on first one
first = sorted(glob.glob(f"{OUT_DIR}/*.sdf"))[0]
print(f"\nFirst SDF ({os.path.basename(first)}):")
with open(first) as f:
    print(f.read())
