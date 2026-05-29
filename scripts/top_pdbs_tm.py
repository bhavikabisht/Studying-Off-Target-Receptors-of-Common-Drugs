import os
import shutil

# --- SETTINGS ---
# Put the exact name of your text file here
TXT_FILE = "top_hits.txt"  
SOURCE_DIR = "All_prots"            
DEST_DIR = "Top_Hits_PDBs"          

def extract_and_copy_files():
    # 1. Check if your text file exists
    if not os.path.exists(TXT_FILE):
        print(f"Error: Could not find the file '{TXT_FILE}'.")
        return

    # 2. Read your text file and clean up the names
    requested_ids = set()
    with open(TXT_FILE, 'r') as f:
        for line in f:
            # Strip whitespace and remove .pdb if it's there
            clean_id = line.strip().replace(".pdb", "")
            if clean_id:
                requested_ids.add(clean_id)
                
    print(f"Loaded {len(requested_ids)} unique protein IDs from your text file.")

    # 3. Create the new destination folder
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    # 4. Map all files in the 8 subfolders so we can find them instantly
    print(f"Scanning '{SOURCE_DIR}' to locate all available PDB files...")
    file_map = {}
    for root, dirs, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.endswith(".pdb"):
                base_name = file.replace(".pdb", "")
                file_map[base_name] = os.path.join(root, file)

    # 5. The Copy and Rescue Mission
    copied_count = 0
    missing_count = 0
    already_copied = set() 

    print("\nCopying files...")
    for target_id in requested_ids:
        match_id = target_id
        
        # Rescue logic: If Foldseek/Alphafold added a chain ID (like _A), remove it to find the parent file
        if target_id not in file_map and "_" in target_id:
            base_name = target_id.rsplit('_', 1)[0]
            if base_name in file_map:
                match_id = base_name

        # Copy the file if we found a match
        if match_id in file_map:
            if match_id not in already_copied:
                source_path = file_map[match_id]
                dest_path = os.path.join(DEST_DIR, f"{match_id}.pdb")
                shutil.copy2(source_path, dest_path)
                copied_count += 1
                already_copied.add(match_id)
        else:
            print(f"Warning: Could not physically find -> {target_id}")
            missing_count += 1

    print("\n--- EXTRACTION COMPLETE ---")
    print(f"Successfully copied {copied_count} unique files into '{DEST_DIR}/'")
    if missing_count > 0:
        print(f"Missing files: {missing_count} (These were not found in your {SOURCE_DIR} folder)")

if __name__ == "__main__":
    extract_and_copy_files()
