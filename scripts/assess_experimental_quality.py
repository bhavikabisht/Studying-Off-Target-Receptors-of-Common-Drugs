import os
import pandas as pd
from Bio import PDB
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

def get_resolution(header):
    """Tries to extract resolution from the PDB header dict."""
    if 'resolution' in header and header['resolution']:
        return header['resolution']
    return None

def assess_experimental(folder_path):
    parser = PDB.PDBParser(QUIET=True)
    results = []

    print(f"--- Analyzing Experimental Quality in: {folder_path} ---")
    
    files = [f for f in os.listdir(folder_path) if f.endswith('.pdb')]
    total_files = len(files)

    for i, f in enumerate(files):
        file_path = os.path.join(folder_path, f)
        
        try:
            # 1. Parse Structure for B-factors
            structure = parser.get_structure('X', file_path)
            b_factors = []
            
            for model in structure:
                for chain in model:
                    for residue in chain:
                        for atom in residue:
                            if atom.name == 'CA': # Check Alpha Carbon
                                b_factors.append(atom.bfactor)
            
            # Calculate Average B-factor (Lower is better for Exp)
            if b_factors:
                avg_b = sum(b_factors) / len(b_factors)
            else:
                avg_b = 999.0 # Placeholder for empty/error

            # 2. Parse Header for Resolution (Resolution is usually in the header)
            # We re-parse just the header to be safe, or rely on BioPython structure.header
            resolution = get_resolution(structure.header)
            
            # 3. Determine Status
            # Good: Res < 2.5 AND Avg B-factor < 50
            # Warning: Res > 3.0 OR Avg B-factor > 60
            status = "GOOD"
            if resolution and resolution > 3.0:
                status = "WARNING (Low Res)"
            if avg_b > 60:
                status = "WARNING (Unstable)"
            
            results.append({
                'Filename': f,
                'Resolution_Angstrom': resolution if resolution else "N/A (NMR/Unknown)",
                'Avg_B_Factor': round(avg_b, 2),
                'Quality_Status': status
            })

        except Exception as e:
            # Catch corrupted files
            print(f"Skipping {f}: {e}")

        if i % 100 == 0:
            print(f"Processed {i}/{total_files}...", end='\r')

    # Save Report
    df = pd.DataFrame(results)
    
    # Sort: Put the bad ones (High B-factor) on top to check
    df = df.sort_values(by='Avg_B_Factor', ascending=False)
    
    output_csv = "experimental_quality_report.csv"
    df.to_csv(output_csv, index=False)
    
    print(f"\n\nDone! Saved to '{output_csv}'")
    
    # Summary stats
    print(f"Total files checked: {len(df)}")
    print(f"Average B-factor across dataset: {df['Avg_B_Factor'].mean():.2f}")

# ==========================
# EDIT PATH HERE
# ==========================
folder_to_check = r"/home/ibab/projects/docking_ready_pdbs"

if __name__ == "__main__":
    assess_experimental(folder_to_check)
