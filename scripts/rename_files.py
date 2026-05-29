import os
import requests
import shutil
import time

# --- CONFIGURATION ---
# List all your text files here
INPUT_FILES = [
    "missing_pdbs_GIT.txt",
    "missing_pdbs_immune.txt",
    "missing_pdbs_respiratory.txt",
    "missing_pdbs_vascular.txt",
    "missing_pdbs_sensory.txt"
]

SOURCE_FOLDER = "unique_pdbs"        # Folder with UniProt named files (e.g. P12345.pdb)
OUTPUT_FOLDER = "PDB_STR"            # Target folder
# ---------------------

def get_uniprot_from_pdb(pdb_id):
    """Maps PDB ID to UniProt Accession."""
    pdb_id = pdb_id.strip().upper()
    url = f"https://rest.uniprot.org/uniprotkb/search?query=xref:pdb-{pdb_id}&fields=accession&size=1"
    try:
        res = requests.get(url).json()
        if res.get('results'):
            return res['results'][0]['primaryAccession']
    except:
        pass
    return None

def main():
    # 1. Validation
    if not os.path.exists(SOURCE_FOLDER):
        print(f"❌ Error: Source folder '{SOURCE_FOLDER}' not found.")
        return
    
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    print(f"Processing {len(INPUT_FILES)} input files...")
    print("-" * 60)
    
    # Global set to ensure uniqueness across ALL files
    processed_uniprots = set()
    total_renamed = 0
    
    # 2. Loop through each text file
    for txt_file in INPUT_FILES:
        if not os.path.exists(txt_file):
            print(f"⚠️ Warning: '{txt_file}' not found. Skipping.")
            continue
            
        print(f"📂 Reading {txt_file}...")
        
        with open(txt_file, 'r') as f:
            pdb_ids = [line.strip() for line in f if line.strip()]

        for pdb_id in pdb_ids:
            # Map PDB -> UniProt
            uniprot_id = get_uniprot_from_pdb(pdb_id)
            
            if uniprot_id:
                # Check if we have the source file
                source_file = os.path.join(SOURCE_FOLDER, f"{uniprot_id}.pdb")
                
                if os.path.exists(source_file):
                    # CHECK: Have we used this protein already?
                    if uniprot_id in processed_uniprots:
                        # print(f"  Skipping {pdb_id} (Protein {uniprot_id} already saved)")
                        pass
                    else:
                        # Copy and rename
                        dest_file = os.path.join(OUTPUT_FOLDER, f"{pdb_id}.pdb")
                        shutil.copy(source_file, dest_file)
                        
                        # Mark as done
                        processed_uniprots.add(uniprot_id)
                        total_renamed += 1
                        print(f"  ✅ {txt_file}: {uniprot_id} -> {pdb_id}.pdb")
                else:
                    # print(f"  Warning: Structure for {uniprot_id} missing in source folder.")
                    pass
            
            # Be polite to API
            time.sleep(0.2)

    # 3. Zip and Finish
    print("-" * 60)
    print(f"Process Complete. Created {total_renamed} PDB-named files in '{OUTPUT_FOLDER}'.")
    
    shutil.make_archive(OUTPUT_FOLDER, 'zip', OUTPUT_FOLDER)
    print(f"🎉 Download '{OUTPUT_FOLDER}.zip' from the Files tab.")

if __name__ == "__main__":
    main()
