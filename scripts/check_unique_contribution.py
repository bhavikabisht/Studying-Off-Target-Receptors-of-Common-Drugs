import os
from collections import defaultdict

# ===================== CONFIGURATION ===================== #
# 1. Path to your FINAL folder (The 16,367 files)
FINAL_FOLDER = "Final_docking_pdbs(all_other_tissues)"

# 2. List of your 5 SOURCE folders
SOURCE_FOLDERS = {
    "GIT": "/home/ibab/project/GIT/docking_ready_pdbs_GIT(final)",
    "Immune": "/home/ibab/project/immune/docking_ready_pdbs_immune(final)",
    "Respiratory": "/home/ibab/project/respiratory/docking_ready_pdbs_respiratory(final)",
    "Vascular": "/home/ibab/project/vascular/docking_ready_pdbs_vascular(final)",
    "Sensory": "/home/ibab/project/sensory/docking_ready_pdbs_sensory(final)"
}
# ========================================================= #

def main():
    print(f"Analyzing contribution for {len(SOURCE_FOLDERS)} folders...")
    print("-" * 60)

    # 1. Load file lists from source folders
    # Map: '1abc.pdb' -> ['GIT', 'Immune']
    file_ownership = defaultdict(list)

    for name, path in SOURCE_FOLDERS.items():
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.endswith('.pdb')]
            print(f"  - {name}: {len(files)} files found")
            for f in files:
                file_ownership[f].append(name)
        else:
            print(f"  ⚠️ Warning: Folder not found: {path}")

    # 2. Analyze the FINAL folder contents
    if not os.path.exists(FINAL_FOLDER):
        print(f"❌ Error: Final folder '{FINAL_FOLDER}' not found.")
        return

    final_files = [f for f in os.listdir(FINAL_FOLDER) if f.endswith('.pdb')]
    total_final = len(final_files)
    
    # Statistics containers
    exclusive_counts = defaultdict(int)
    shared_count = 0
    
    print("-" * 60)
    print(f"Checking {total_final} files in Final Folder against sources...")

    for f in final_files:
        owners = file_ownership.get(f, [])
        
        if len(owners) == 1:
            # It only exists in ONE folder -> Exclusive Contribution
            source = owners[0]
            exclusive_counts[source] += 1
        elif len(owners) > 1:
            # It exists in MULTIPLE folders -> Shared
            shared_count += 1
        else:
            # Should not happen if Final folder came from sources
            print(f"  ⚠️ Warning: {f} found in Final but NOT in any source folder!")

    # 3. Print Report
    print("=" * 60)
    print(f"FINAL CONTRIBUTION REPORT (Total: {total_final} files)")
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
    print("-" * 60)
    print(f"TOTAL CHECK: {total_unique + shared_count} / {total_final}")

if __name__ == "__main__":
    main()
