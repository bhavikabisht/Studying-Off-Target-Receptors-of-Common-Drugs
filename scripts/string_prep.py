import os
import zipfile
import shutil
import re

# --- SETTINGS ---
ZIP_FILE = "Top_Hits_PDBs.zip"
FINAL_DIR = "Top_Hits_PDBs"
TEMP_DIR = "temp_pdb_workspace"
OUTPUT_TXT = "string_db_input.txt"

def prep_for_string():
    # 1. Extract and Flatten the Zip (if it hasn't been unzipped yet)
    if os.path.exists(ZIP_FILE):
        print(f"1. Extracting '{ZIP_FILE}'...")
        with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
            zip_ref.extractall(TEMP_DIR)
            
        if not os.path.exists(FINAL_DIR):
            os.makedirs(FINAL_DIR)
            
        print("2. Flattening nested PDB files into a single folder...")
        for root, dirs, files in os.walk(TEMP_DIR):
            for file in files:
                if file.endswith(".pdb"):
                    source_path = os.path.join(root, file)
                    dest_path = os.path.join(FINAL_DIR, file)
                    if not os.path.exists(dest_path):
                        shutil.move(source_path, dest_path)
                        
        shutil.rmtree(TEMP_DIR)
        print(f"   Successfully rescued and flattened PDBs into '{FINAL_DIR}/'.")
    else:
        print(f"Note: '{ZIP_FILE}' not found. Looking directly in the '{FINAL_DIR}' folder...")

    # 2. Read the files and extract clean IDs
    if not os.path.exists(FINAL_DIR):
        print(f"\n[ERROR] Could not find the '{FINAL_DIR}' folder.")
        return

    print("\n3. Extracting protein IDs for STRING-db...")
    unique_ids = set()
    
    for file in os.listdir(FINAL_DIR):
        if file.endswith(".pdb"):
            # Clean up the filename to get just the core ID
            raw_id = file.replace(".pdb", "")
            clean_id = re.sub(r'^clean_', '', raw_id)  # Removes 'clean_'
            clean_id = clean_id.split('_')[0]          # Removes chain tags like '_A'
            unique_ids.add(clean_id)

    # 3. Save to a text file
    with open(OUTPUT_TXT, 'w') as f:
        for protein_id in sorted(unique_ids):
            f.write(protein_id + "\n")

    print("\n=== COMPLETE ===")
    print(f"Extracted {len(unique_ids)} unique IDs.")
    print(f"Your list is ready and saved as: {OUTPUT_TXT}")

if __name__ == "__main__":
    prep_for_string()
