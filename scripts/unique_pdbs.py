import os
import shutil

# --- CONFIGURATION ---
# List the exact names of your 5 source folders here
SOURCE_FOLDERS = [
    "unique_structures_for_docking_GIT",               # Folder 1
    "unique_structures_for_docking_immune",     # Folder 2
    "unique_structures_for_docking_respiratory",# Folder 3
    "unique_structures_for_docking_sensory",# Folder 4
    "unique_structures_for_docking_vascular"    # Folder 5
]

DESTINATION_FOLDER = "unique_pdbs"
# ---------------------

def main():
    # 1. Create the destination folder
    if not os.path.exists(DESTINATION_FOLDER):
        os.makedirs(DESTINATION_FOLDER)
        print(f"Created folder: {DESTINATION_FOLDER}")
    else:
        print(f"Using existing folder: {DESTINATION_FOLDER}")

    copied_count = 0
    skipped_count = 0
    unique_files = set()

    print("-" * 60)

    # 2. Iterate through each source folder
    for folder in SOURCE_FOLDERS:
        if not os.path.exists(folder):
            print(f"⚠️ Warning: Source folder '{folder}' does not exist. Skipping.")
            continue
        
        print(f"Scanning '{folder}'...")
        files = os.listdir(folder)

        for filename in files:
            # Skip hidden files (like .ipynb_checkpoints)
            if filename.startswith('.'):
                continue

            source_path = os.path.join(folder, filename)
            dest_path = os.path.join(DESTINATION_FOLDER, filename)

            # 3. Check for uniqueness
            # We check if the filename is already in our 'unique_files' set OR exists in the folder
            if filename not in unique_files and not os.path.exists(dest_path):
                try:
                    shutil.copy(source_path, dest_path)
                    unique_files.add(filename)
                    copied_count += 1
                    # Optional: Print every copy (can be noisy if many files)
                    # print(f"  + Copied: {filename}")
                except Exception as e:
                    print(f"  ❌ Error copying {filename}: {e}")
            else:
                skipped_count += 1
                # print(f"  - Skipped duplicate: {filename}")

    # 4. Final Report
    print("-" * 60)
    print("CONSOLIDATION COMPLETE")
    print(f"Total Unique Files in '{DESTINATION_FOLDER}': {len(unique_files)}")
    print(f"New files copied: {copied_count}")
    print(f"Duplicates skipped: {skipped_count}")
    
    # 5. Zip for download
    print("\nZipping for download...")
    shutil.make_archive(DESTINATION_FOLDER, 'zip', DESTINATION_FOLDER)
    print(f"Done! Download '{DESTINATION_FOLDER}.zip' from the Files tab.")

if __name__ == "__main__":
    main()
