import os

def inventory_folders(folder_exp, folder_af):
    """
    Scans two folders and compares their contents based on filenames.
    """
    
    # 1. Get list of files (ignoring hidden files like .DS_Store)
    def get_clean_filenames(path):
        try:
            files = [f for f in os.listdir(path) if not f.startswith('.')]
            # Store as dictionary: {'filename_without_ext': 'full_filename'}
            # This helps us match "protein1.pdb" with "protein1.cif" if needed
            return {os.path.splitext(f)[0]: f for f in files}
        except FileNotFoundError:
            print(f"Error: The folder '{path}' was not found.")
            return {}

    print("--- Scanning Folders ---")
    files_exp = get_clean_filenames(folder_exp)
    files_af = get_clean_filenames(folder_af)

    print(f"Folder 1 (Experimental): Found {len(files_exp)} files")
    print(f"Folder 2 (AlphaFold/Colab): Found {len(files_af)} files")
    print("-" * 30)

    # 2. Compare the sets of filenames (without extensions)
    set_exp = set(files_exp.keys())
    set_af = set(files_af.keys())

    common = set_exp.intersection(set_af)
    unique_exp = set_exp - set_af
    unique_af = set_af - set_exp

    # 3. Print the Report
    print(f"\n### SUMMARY ###")
    print(f"1. OVERLAPS (In both folders): {len(common)}")
    if len(common) > 0:
        print("   (These files exist in both. Usually, you prioritize Folder 1 here.)")
        # Optional: Print first 5 matches
        print(f"   Examples: {list(common)[:5]}")

    print(f"\n2. UNIQUE to Folder 1 (Experimental): {len(unique_exp)}")
    
    print(f"\n3. UNIQUE to Folder 2 (AlphaFold/Colab): {len(unique_af)}")

    return common, unique_exp, unique_af

# ==========================================
# USER SETTINGS (EDIT THESE PATHS)
# ==========================================
# Example: r"C:\Users\Name\Documents\Experimental"
folder_1_path = r"docking_ready_pdbs" 
folder_2_path = r"cleaned_alphafold_pdbs"

# Run the function
if __name__ == "__main__":
    inventory_folders(folder_1_path, folder_2_path)
