import os
import subprocess
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed

# --- SETTINGS ---
# Replace with the exact name of your main target PDB file
TARGET_PDB = "H1.pdb" 

# Point this directly to the main folder containing the 8 subfolders
PROTEOME_DIR = "All_prots"
OUTPUT_CSV = "tm_scores_results.csv"
TM_ALIGN_CMD = "./TMalign"

def calculate_tm_score(proteome_pdb_path):
    # Get the protein name and the specific subfolder it came from
    protein_id = os.path.basename(proteome_pdb_path).replace(".pdb", "")
    folder_name = os.path.basename(os.path.dirname(proteome_pdb_path))
    
    try:
        # Run TM-align
        result = subprocess.run(
            [TM_ALIGN_CMD, TARGET_PDB, proteome_pdb_path], 
            capture_output=True, text=True, check=True
        )
        
        tm_score = "Error"
        # Parse the output to find the TM-score normalized by the Target (Chain_1)
        for line in result.stdout.split('\n'):
            if "TM-score=" in line and "Chain_1" in line:
                tm_score = line.split()[1]
                break
                
        return folder_name, protein_id, tm_score

    except Exception as e:
        return folder_name, protein_id, f"Error: {str(e)}"

if __name__ == "__main__":
    if not os.path.exists(TARGET_PDB):
        print(f"Error: Could not find '{TARGET_PDB}'. Please check the filename.")
        exit(1)

    # RECURSIVE SEARCH: Walk through all 8 subfolders to find every .pdb file
    proteome_files = []
    for root, dirs, files in os.walk(PROTEOME_DIR):
        for file in files:
            if file.endswith(".pdb"):
                proteome_files.append(os.path.join(root, file))
    
    if not proteome_files:
        print(f"Error: Found 0 .pdb files in {PROTEOME_DIR} or its subfolders.")
        exit(1)

    print(f"Found {len(proteome_files)} proteins across all subfolders in '{PROTEOME_DIR}'.")
    print("Starting TM-align batch processing... This might take a while!")

    # Open CSV and write header
    with open(OUTPUT_CSV, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Folder_Name", "Protein_ID", "TM_Score"])
        
        # Run the alignments in parallel using all available CPU cores
        with ProcessPoolExecutor() as executor:
            futures = {executor.submit(calculate_tm_score, pdb): pdb for pdb in proteome_files}
            
            count = 0
            for future in as_completed(futures):
                folder_name, protein_id, score = future.result()
                writer.writerow([folder_name, protein_id, score])
                
                # Print progress every 100 proteins
                count += 1
                if count % 100 == 0:
                    print(f"Processed {count}/{len(proteome_files)} proteins...")

    print(f"\nDone! All TM-scores have been saved to {OUTPUT_CSV}")
