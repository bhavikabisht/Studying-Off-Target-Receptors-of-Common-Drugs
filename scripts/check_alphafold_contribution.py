import os
import requests
import time
from collections import defaultdict

# ===================== CONFIGURATION ===================== #
# 1. Path to your FINAL AlphaFold folder (PDB IDs: 1abc.pdb)
FINAL_FOLDER = "alphafold_pdbs(cleaned)"

# 2. List of your 5 SOURCE AlphaFold folders (UniProt IDs: P12345.pdb)
SOURCE_FOLDERS = {
    "GIT": "/home/ibab/project/unique_structures_for_docking_GIT",
    "Immune": "/home/ibab/project/unique_structures_for_docking_immune",
    "Respiratory": "/home/ibab/project/unique_structures_for_docking_respiratory",
    "Vascular": "/home/ibab/project/unique_structures_for_docking_vascular",
    "Sensory": "/home/ibab/project/unique_structures_for_docking_sensory"
}
# ========================================================= #

def get_uniprot_from_pdb(pdb_id):
    """
    Asks UniProt: "What is the UniProt Accession for this PDB ID?"
    """
    pdb_id = pdb_id.lower()
    url = f"https://rest.uniprot.org/uniprotkb/search?query=xref:pdb-{pdb_id}&fields=accession&size=1"
    try:
        res = requests.get(url).json()
        if res.get('results'):
            return res['results'][0]['primaryAccession']
    except:
        pass
    return None

def main():
    print(f"Loading files from {len(SOURCE_FOLDERS)} source folders (UniProt IDs)...")
    
    # 1. Index the Source Folders by UniProt ID
    # Map: 'P12345' -> ['GIT', 'Immune']
    uniprot_ownership = defaultdict(list)

    for folder_name, folder_path in SOURCE_FOLDERS.items():
        if os.path.exists(folder_path):
            files = [f for f in os.listdir(folder_path) if f.endswith('.pdb')]
            print(f"  - {folder_name}: {len(files)} files")
            
            for filename in files:
                # Remove .pdb to get UniProt ID (e.g., P12345)
                uid = filename.replace(".pdb", "").strip()
                uniprot_ownership[uid].append(folder_name)
        else:
            print(f"  ⚠️ Warning: Folder not found: {folder_path}")

    # 2. Process Final Folder (PDB IDs)
    if not os.path.exists(FINAL_FOLDER):
        print(f"❌ Error: Final folder '{FINAL_FOLDER}' not found.")
        return

    final_files = [f for f in os.listdir(FINAL_FOLDER) if f.endswith('.pdb')]
    total_final = len(final_files)
    
    print("-" * 60)
    print(f"Translating and checking {total_final} PDB files against sources...")
    print("This may take a moment (contacting UniProt)...")

    # Statistics
    exclusive_counts = defaultdict(int)
    shared_count = 0
    not_found_count = 0
    translation_failed = 0

    for i, filename in enumerate(final_files):
        # 1. Get PDB ID from filename (1abc.pdb -> 1abc)
        pdb_id = filename.replace(".pdb", "").strip()
        
        # 2. Translate PDB -> UniProt
        uniprot_id = get_uniprot_from_pdb(pdb_id)
        
        if uniprot_id:
            # 3. Check ownership using the Translated ID
            owners = uniprot_ownership.get(uniprot_id, [])
            
            if len(owners) == 1:
                source = owners[0]
                exclusive_counts[source] += 1
            elif len(owners) > 1:
                shared_count += 1
            else:
                not_found_count += 1
                # print(f"  Warning: {pdb_id} (UniProt: {uniprot_id}) not found in sources.")
        else:
            translation_failed += 1
            # print(f"  Warning: Could not translate PDB ID {pdb_id}")
        
        # Progress bar every 20 files
        if (i+1) % 20 == 0:
            print(f"  Processed {i+1}/{total_final}...")
        
        time.sleep(0.2) # Be polite to the API

    # 3. Print Final Report
    print("=" * 60)
    print(f"ALPHAFOLD CONTRIBUTION REPORT (Total: {total_final} files)")
    print("=" * 60)
    
    print(f"{'Folder Name':<15} | {'Unique Contribution':<20} | {'(Files found ONLY here)'}")
    print("-" * 60)
    
    total_unique = 0
    for name in SOURCE_FOLDERS.keys():
        count = exclusive_counts[name]
        total_unique += count
        print(f"{name:<15} | {count:<20} |")
    
    print("-" * 60)
    print(f"{'SHARED':<15} | {shared_count:<20} | (Found in 2+ folders)")
    
    if not_found_count > 0:
        print(f"{'UNKNOWN':<15} | {not_found_count:<20} | (Translated ID not in sources)")
    if translation_failed > 0:
        print(f"{'ERROR':<15} | {translation_failed:<20} | (Could not translate ID)")

    print("-" * 60)
    print(f"TOTAL CHECK: {total_unique + shared_count + not_found_count + translation_failed} / {total_final}")

if __name__ == "__main__":
    main()
