import pandas as pd
import os
import subprocess
import re

# --- SETTINGS ---
EXCEL_FILE = "sorted_top_hits.xlsx" # The file (CSV format) you created earlier
FASTA_DIR = "Target_FASTAs"         # The flattened folder with all your FASTAs
H1_FASTA = "rcsb_pdb_3RZE.fasta"    # Your primary target sequence
TOP_N = 20                          # How many top hits to include for ESPript

COMBINED_FASTA = "espript_showcase.fasta"
OUTPUT_ALN = "espript_top20_alignment.aln"

def prepare_espript_alignment():
    # 1. Check if files exist
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: Could not find '{EXCEL_FILE}'")
        return
    if not os.path.exists(H1_FASTA):
        print(f"Error: Could not find '{H1_FASTA}'")
        return
    if not os.path.exists(FASTA_DIR):
        print(f"Error: Could not find '{FASTA_DIR}'")
        return

    # 2. Read the file (using read_csv since it's not a true Excel zip)
    print(f"Loading '{EXCEL_FILE}' and extracting the Top {TOP_N} hits...")
    
    # Try reading as tab-separated first; fallback to comma if needed
    try:
        df = pd.read_csv(EXCEL_FILE, sep='\t')
        if len(df.columns) < 2: # If tab failed to find columns, try comma
            df = pd.read_csv(EXCEL_FILE)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Automatically find the ID and Score columns
    try:
        id_col = [col for col in df.columns if 'ID' in col.upper() or 'TARGET' in col.upper()][0]
        score_col = [col for col in df.columns if 'SCORE' in col.upper() or 'TMSPLIT' in col.upper() or 'ALNTMSCORE' in col.upper()][0]
    except IndexError:
        print("Error: Could not find columns containing 'ID' or 'SCORE' in the file.")
        print(f"Available columns: {list(df.columns)}")
        return

    # Ensure it is sorted by highest score, then take the top N rows
    df[score_col] = pd.to_numeric(df[score_col], errors='coerce')
    top_hits = df.sort_values(by=score_col, ascending=False).head(TOP_N)

    # 3. Clean the IDs to find their matching FASTA files
    target_fasta_ids = []
    for raw_id in top_hits[id_col]:
        clean_id = str(raw_id).replace(".pdb", "")
        clean_id = re.sub(r'^clean_', '', clean_id)
        clean_id = clean_id.split('_')[0]
        target_fasta_ids.append(clean_id)

    # Remove duplicates
    unique_target_ids = list(dict.fromkeys(target_fasta_ids)) 
    print(f"Found {len(unique_target_ids)} unique parent proteins in the Top {TOP_N} hits.")

    # 4. Build the Master FASTA file
    print("Bundling sequences with H1 locked at the top...")
    
    with open(H1_FASTA, 'r') as f:
        h1_content = f.read().strip()
    h1_id = h1_content.split('\n')[0].replace(">", "").strip()

    added_count = 0
    
    with open(COMBINED_FASTA, 'w') as out_file:
        out_file.write(h1_content + "\n\n") # Write H1 first
        
        for target_id in unique_target_ids:
            fasta_path = os.path.join(FASTA_DIR, f"{target_id}.fasta")
            
            if os.path.exists(fasta_path):
                with open(fasta_path, 'r') as f:
                    content = f.read().strip()
                    file_id = content.split('\n')[0].replace(">", "").strip()
                    
                    if file_id != h1_id: # Prevent duplicating H1
                        out_file.write(content + "\n\n")
                        added_count += 1
            else:
                print(f"  [Warning] Missing FASTA file for: {target_id}")

    print(f"Successfully bundled {added_count + 1} sequences.")

    # 5. Run Clustal Omega
    print(f"\nStarting Clustal Omega to generate {OUTPUT_ALN}...")
    cmd = [
        "clustalo",
        "-i", COMBINED_FASTA,
        "-o", OUTPUT_ALN,
        "--outfmt=clustal",
        "--output-order=input-order", # Locks H1 at the top
        "--force"
    ]

    try:
        subprocess.run(cmd, check=True)
        print("\n=== SUCCESS ===")
        print(f"Your Showcase Alignment is ready: {OUTPUT_ALN}")
    except subprocess.CalledProcessError as e:
        print("\n[ERROR] Clustal Omega encountered an issue. Is it installed?")
        print(e)

if __name__ == "__main__":
    prepare_espript_alignment()

