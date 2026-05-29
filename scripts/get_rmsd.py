import os
import subprocess
import csv

# --- SETTINGS ---
TARGET_PDB = "H1.pdb" 
PROTEOME_DIR = "All_prots" # Point to main folder
HITS_FILE = "top_hits.txt"
OUTPUT_CSV = "top_hits_rmsd.csv"
TM_ALIGN_CMD = "./TMalign"

def find_pdb_path(filename, search_dir):
    """Recursively finds the exact path of a specific PDB file."""
    for root, dirs, files in os.walk(search_dir):
        if filename in files:
            return os.path.join(root, filename)
    return None

if __name__ == "__main__":
    with open(HITS_FILE, 'r') as f:
        hit_files = [line.strip() for line in f if line.strip()]

    print(f"Found {len(hit_files)} top hits to process for RMSD...")

    with open(OUTPUT_CSV, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Protein_ID", "TM_Score", "RMSD"])
        
        for pdb_name in hit_files:
            full_path = find_pdb_path(pdb_name, PROTEOME_DIR)
            protein_id = pdb_name.replace(".pdb", "")
            
            if not full_path:
                writer.writerow([protein_id, "Error: File not found", "N/A"])
                continue

            # Run TM-align
            result = subprocess.run(
                [TM_ALIGN_CMD, TARGET_PDB, full_path], 
                capture_output=True, text=True, check=True
            )
            
            tm_score, rmsd = "N/A", "N/A"
            
            # Parse output for BOTH variables
            for line in result.stdout.split('\n'):
                if "Aligned length=" in line and "RMSD=" in line:
                    # Extracts the RMSD value from the text string
                    rmsd = line.split("RMSD=")[1].split(",")[0].strip()
                if "TM-score=" in line and "Chain_1" in line:
                    tm_score = line.split()[1]
                    
            writer.writerow([protein_id, tm_score, rmsd])
            print(f"Processed: {protein_id} | TM: {tm_score} | RMSD: {rmsd}")

    print(f"\nDone! Saved detailed metrics to {OUTPUT_CSV}")
