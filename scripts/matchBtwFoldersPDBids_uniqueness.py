import os
import pandas as pd
from Bio import PDB
import gzip
import warnings

# Suppress Biopython warnings about discontinuous chains
warnings.filterwarnings("ignore")

def map_folders(folder_exp, folder_af):
    data = []
    
    # Setup PDB Parser
    parser_pdb = PDB.PDBParser(QUIET=True)
    parser_cif = PDB.MMCIFParser(QUIET=True)

    print("--- 1. Analyzing Folder 2 (AlphaFold) ---")
    # In Folder 2, we assume Filename = UniProtID
    af_ids = set()
    for f in os.listdir(folder_af):
        if f.endswith('.pdb'):
            uid = os.path.splitext(f)[0]
            af_ids.add(uid)
            data.append({'Filename': f, 'Folder': 'AlphaFold', 'Format': 'PDB', 'UniProt_ID': uid, 'PDB_ID': 'N/A'})
    
    print(f"Index built for {len(af_ids)} AlphaFold structures.")

    print("\n--- 2. Analyzing Folder 1 (Experimental) ---")
    print("Reading headers to extract UniProt IDs (this might take a minute)...")
    
    count = 0
    for f in os.listdir(folder_exp):
        file_path = os.path.join(folder_exp, f)
        
        # Skip hidden files
        if f.startswith('.'): continue

        # Determine format
        structure = None
        current_uid = "Unknown"
        pdb_id = os.path.splitext(f)[0] # Assume filename is PDB ID
        
        try:
            if f.endswith('.pdb'):
                # Quick text parse for DBREF (Faster than parsing structure)
                with open(file_path, 'r', errors='ignore') as handle:
                    for line in handle:
                        if line.startswith('DBREF'):
                            # Standard PDB format: DBREF  1ABC A    1   230  UNP    P12345
                            parts = line.split()
                            if 'UNP' in parts:
                                idx = parts.index('UNP')
                                if idx + 1 < len(parts):
                                    current_uid = parts[idx+1]
                                    break
                
                # If text parse failed, use parser (slower but robust)
                if current_uid == "Unknown":
                    structure = parser_pdb.get_structure('X', file_path)

            elif f.endswith('.cif'):
                # CIF parsing is complex, try to load structure
                structure = parser_cif.get_structure('X', file_path)
            
            # If we loaded a structure object (mostly for CIF or failed PDB text parse)
            if structure:
                # Try to extract from header
                header = structure.header
                if 'dbref' in header:
                    for ref in header['dbref']:
                        if 'database' in ref and 'unp' in ref['database'].lower():
                            current_uid = ref['db_code']
                            break
                            
            # Record Data
            data.append({
                'Filename': f, 
                'Folder': 'Experimental', 
                'Format': 'CIF' if f.endswith('.cif') else 'PDB',
                'UniProt_ID': current_uid,
                'PDB_ID': pdb_id
            })
            
            count += 1
            if count % 1000 == 0:
                print(f"Processed {count} files...")

        except Exception as e:
            print(f"Error reading {f}: {e}")

    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Check for biological overlaps
    # Create a column "Is_Duplicate"
    # A duplicate exists if a UniProt ID in Exp is also found in AF
    af_id_set = set(df[df['Folder'] == 'AlphaFold']['UniProt_ID'])
    
    def check_overlap(row):
        if row['Folder'] == 'Experimental' and row['UniProt_ID'] in af_id_set:
            return True
        return False

    df['Has_Match_In_Other_Folder'] = df.apply(check_overlap, axis=1)

    # Save
    output_csv = "structure_inventory.csv"
    df.to_csv(output_csv, index=False)
    
    print("-" * 30)
    print(f"Done! Saved report to {output_csv}")
    print(f"Total entries: {len(df)}")
    print(f"Experimental files matched to an AlphaFold structure: {df['Has_Match_In_Other_Folder'].sum()}")

# ==========================
# EDIT PATHS HERE
# ==========================
folder_1_path = r"docking_ready_pdbs" 
folder_2_path = r"cleaned_alphafold_pdbs"

if __name__ == "__main__":
    map_folders(folder_1_path, folder_2_path)
