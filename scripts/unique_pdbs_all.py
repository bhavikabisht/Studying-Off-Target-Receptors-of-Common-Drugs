import os
import shutil

# --- CONFIGURATION ---
# Replace these names with your ACTUAL 5 folder names
SOURCE_FOLDERS = [
    "/home/ibab/projects/docking_ready_pdbs",
    "/home/ibab/project/PDB_STR",
    "/home/ibab/project/Final_docking_pdbs(all_other_tissues)", 
]

OUTPUT_FOLDER = "/home/ibab/project/All_docking_ready_pdbs(exp)"
# ---------------------

def main():
    # 1. Create Output Folder
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Created folder: {OUTPUT_FOLDER}")

    # Set to track filenames we have already saved
    seen_files = set()
    
    print("-" * 60)
    print(f"Consolidating files from {len(SOURCE_FOLDERS)} folders...")

    stats = {'copied': 0, 'duplicates': 0}

    # 2. Iterate through each source folder
    for folder in SOURCE_FOLDERS:
        if not os.path.exists(folder):
            print(f" Warning: Folder '{folder}' not found. Skipping.")
            continue
        
        print(f" Scanning '{folder}'...")
        files = [f for f in os.listdir(folder) if f.endswith('.pdb')]

        for filename in files:
            # Check if we have already collected this PDB ID
            if filename not in seen_files:
                src_path = os.path.join(folder, filename)
                dst_path = os.path.join(OUTPUT_FOLDER, filename)
                
                try:
                    shutil.copy(src_path, dst_path)
                    seen_files.add(filename)
                    stats['copied'] += 1
                except Exception as e:
                    print(f"   Error copying {filename}: {e}")
            else:
                stats['duplicates'] += 1

    # 3. Final Report
    print("-" * 60)
    print("CONSOLIDATION COMPLETE")
    print(f"  - Total Unique Files: {len(seen_files)}")
    print(f"  - Duplicates Skipped: {stats['duplicates']}")
    print(f"  - Final Folder:       '{OUTPUT_FOLDER}'")

    # 4. Zip for download
    print("\nZipping for download...")
    shutil.make_archive(OUTPUT_FOLDER, 'zip', OUTPUT_FOLDER)
    print(f" Download '{OUTPUT_FOLDER}.zip' from the Files tab.")

if __name__ == "__main__":
    main()
