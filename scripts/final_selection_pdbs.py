import os
import shutil
import re
from collections import defaultdict, Counter

# =========================================================
# CONFIGURATION
# =========================================================
FOLDERS = {
    "EXP_BEST": "/home/ibab/projects/docking_ready_pdbs",
    "EXP_OTHER": "/home/ibab/project/Final_docking_pdbs(all_other_tissues)",
    "AF_TRIMMED": "/home/ibab/projects/cleaned_alphafold_pdbs/Final_Trimmed_Ready_alphafold",
    "AF_RAW": "/home/ibab/project/alphafold_pdbs(cleaned)"
}

# Priority: EXP_BEST > EXP_OTHER > AF_TRIMMED > AF_RAW
PRIORITY_ORDER = ["EXP_BEST", "EXP_OTHER", "AF_TRIMMED", "AF_RAW"]

# OUTPUT
OUT_DIR = "FINAL_UNIQUE_DOCKING_SET"
KEEP_LOG = "FINAL_SELECTION_REPORT.txt"
DISCARD_LOG = "DEDUPLICATION_REPORT.txt"

# =========================================================
# MAIN SCRIPT
# =========================================================
def main():
    # 1. Setup
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
        print(f"Created output directory: {OUT_DIR}")

    # Map to store all versions of a structure: { '1ABC': [ {data}, {data} ] }
    structure_map = defaultdict(list)
    
    # 2. Index all files
    print("Indexing files from source folders...")
    
    for source_name, folder_path in FOLDERS.items():
        if not os.path.exists(folder_path):
            print(f"⚠️ Warning: Folder not found: {folder_path}")
            continue

        files = [f for f in os.listdir(folder_path) if f.endswith(".pdb")]
        print(f"  - Found {len(files)} files in {source_name}")

        for filename in files:
            # EXTRACT ID FROM FILENAME
            # Assumes filename is "1ABC.pdb" or "clean_1ABC.pdb" -> ID is "1ABC"
            # This is safer than reading headers for cleaned PDBs
            base_name = filename.replace(".pdb", "")
            
            # If you have prefixes like 'clean_', remove them to match IDs
            if base_name.startswith("clean_"):
                pdb_id = base_name.replace("clean_", "").upper()
            else:
                pdb_id = base_name.upper()

            # Store info
            structure_map[pdb_id].append({
                "source": source_name,
                "folder": folder_path,
                "filename": filename,
                "full_path": os.path.join(folder_path, filename),
                "priority_rank": PRIORITY_ORDER.index(source_name) # Store rank for sorting
            })

    # 3. Deduplicate (Select Best)
    print(f"\nProcessing {len(structure_map)} unique IDs...")
    
    final_selection = {}
    discarded_entries = []

    for pdb_id, candidates in structure_map.items():
        # Sort by Priority Rank (0 is highest/best)
        sorted_candidates = sorted(candidates, key=lambda x: x["priority_rank"])
        
        # Pick the best one
        best_choice = sorted_candidates[0]
        final_selection[pdb_id] = best_choice
        
        # Record the rest as discarded
        for rejected in sorted_candidates[1:]:
            discarded_entries.append((pdb_id, rejected))

    # 4. Copy Files
    print("Copying final files...")
    for pdb_id, info in final_selection.items():
        # Rename to clean ID (e.g., 1ABC.pdb)
        dest_path = os.path.join(OUT_DIR, f"{pdb_id}.pdb")
        shutil.copy(info["full_path"], dest_path)

    # 5. Generate Reports
    generate_reports(final_selection, discarded_entries)
    print("\n✅ DONE! Check the output folder and report files.")

def generate_reports(selection, discards):
    # Report 1: What we KEPT
    source_counts = Counter([info["source"] for info in selection.values()])
    
    with open(KEEP_LOG, "w") as f:
        f.write("FINAL SELECTION REPORT\n")
        f.write("========================================\n")
        f.write(f"Total Unique Structures: {len(selection)}\n")
        f.write("Breakdown by Source:\n")
        for source in PRIORITY_ORDER:
            f.write(f"  - {source}: {source_counts[source]}\n")
        f.write("\nDetailed List:\n")
        f.write("PDB_ID\tSource\tOriginal_File\n")
        for pid, info in selection.items():
            f.write(f"{pid}\t{info['source']}\t{info['filename']}\n")

    # Report 2: What we DISCARDED
    discard_counts = Counter([info["source"] for _, info in discards])
    
    with open(DISCARD_LOG, "w") as f:
        f.write("DEDUPLICATION REPORT (DISCARDED FILES)\n")
        f.write("========================================\n")
        f.write(f"Total Files Discarded: {len(discards)}\n")
        f.write("Breakdown by Source:\n")
        for source in PRIORITY_ORDER:
            f.write(f"  - {source}: {discard_counts[source]}\n")
        f.write("\nDetailed List:\n")
        f.write("PDB_ID\tSource\tFolder\n")
        for pid, info in discards:
            f.write(f"{pid}\t{info['source']}\t{info['folder']}\n")

if __name__ == "__main__":
    main()
