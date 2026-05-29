import os
from collections import defaultdict

# ===================== CONFIGURATION ===================== #

# 1. List your 5 specific source folders here
SOURCE_FOLDERS_LIST = [
    "/home/ibab/project/GIT/docking_ready_pdbs_GIT(final)",
    "/home/ibab/project/immune/docking_ready_pdbs_immune(final)",
    "/home/ibab/project/respiratory/docking_ready_pdbs_respiratory(final)", 
    "/home/ibab/project/vascular/docking_ready_pdbs_vascular(final)",
    "/home/ibab/project/sensory/docking_ready_pdbs_sensory(final)"
]

# 2. Path to the final deduplicated folder
FINAL_UNIQUE_DIR = "Final_docking_pdbs(all_other_tissues)"

# 3. Output directory for reports
OUTPUT_DIR = "reverse_provenance_reports_exp"

# ========================================================= #

def main():
    # Setup output directory
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output folder: {OUTPUT_DIR}")

    # Check if Final Folder exists
    if not os.path.exists(FINAL_UNIQUE_DIR):
        print(f"❌ Error: Final folder '{FINAL_UNIQUE_DIR}' does not exist.")
        return

    print("Reading final unique PDB filenames...")
    # Get set of final PDBs (lowercase for comparison)
    final_pdbs = {
        f.lower() for f in os.listdir(FINAL_UNIQUE_DIR)
        if f.lower().endswith(".pdb")
    }
    print(f"  - Found {len(final_pdbs)} unique PDBs.")

    # Read PDBs from each source folder
    print("Reading source folders...")
    tissue_pdb_sets = {}
    
    for folder_name in SOURCE_FOLDERS_LIST:
        if os.path.exists(folder_name):
            files = {
                f.lower() for f in os.listdir(folder_name) 
                if f.lower().endswith(".pdb")
            }
            tissue_pdb_sets[folder_name] = files
            print(f"  - {folder_name}: {len(files)} files")
        else:
            print(f"  ⚠️ Warning: Source folder '{folder_name}' not found. Skipping.")

    # Track provenance
    print("Mapping provenance...")
    folder_contribution_counts = defaultdict(int)
    pdb_to_folders = defaultdict(list)

    # Reverse mapping logic
    for pdb in final_pdbs:
        found_in_any = False
        for tissue, pdb_set in tissue_pdb_sets.items():
            if pdb in pdb_set:
                folder_contribution_counts[tissue] += 1
                pdb_to_folders[pdb].append(tissue)
                found_in_any = True
        
        if not found_in_any:
            pdb_to_folders[pdb].append("UNKNOWN_SOURCE")

    # ===================== OUTPUT FILES ===================== #

    # 1. Summary counts per folder
    summary_file = os.path.join(OUTPUT_DIR, "folder_contribution_summary.txt")
    with open(summary_file, "w") as f:
        f.write("REVERSE PROVENANCE SUMMARY\n")
        f.write("=============================================\n")
        f.write(f"Total Unique PDBs in Final Set: {len(final_pdbs)}\n")
        f.write("Note: Counts sum to > Total because of overlaps.\n\n")
        
        # Sort by count descending
        sorted_counts = sorted(folder_contribution_counts.items(), key=lambda x: x[1], reverse=True)
        
        for tissue, count in sorted_counts:
            f.write(f"{tissue}: {count} files present\n")

    # 2. Detailed provenance file
    detail_file = os.path.join(OUTPUT_DIR, "pdb_provenance_details.txt")
    with open(detail_file, "w") as f:
        f.write("DETAILED PROVENANCE (Where did this file exist?)\n")
        f.write("=============================================\n")
        for pdb, tissues in sorted(pdb_to_folders.items()):
            f.write(f"{pdb} : {', '.join(tissues)}\n")

    # 3. Overlap report
    overlap_file = os.path.join(OUTPUT_DIR, "overlapping_pdbs.txt")
    with open(overlap_file, "w") as f:
        f.write("OVERLAP REPORT (Files found in multiple source folders)\n")
        f.write("=============================================\n")
        overlap_count = 0
        for pdb, tissues in sorted(pdb_to_folders.items()):
            if len(tissues) > 1:
                f.write(f"{pdb} : {', '.join(tissues)}\n")
                overlap_count += 1
        f.write(f"\nTotal Overlapping PDBs: {overlap_count}\n")

    print("✔ Reverse provenance analysis completed.")
    print(f"Reports saved in: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
