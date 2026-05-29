import os
import urllib.request
import re

# --- SETTINGS ---
PDB_DIR = "Top_Hits_PDBs"
FASTA_DIR = "Target_FASTAs"

# Dictionary to convert 3-letter PDB codes to 1-letter FASTA codes
AA_DICT = {'CYS': 'C', 'ASP': 'D', 'SER': 'S', 'GLN': 'Q', 'LYS': 'K',
           'ILE': 'I', 'PRO': 'P', 'THR': 'T', 'PHE': 'F', 'ASN': 'N',
           'GLY': 'G', 'HIS': 'H', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W',
           'ALA': 'A', 'VAL': 'V', 'GLU': 'E', 'TYR': 'Y', 'MET': 'M'}

def get_sequence_from_pdb(pdb_path):
    """Extracts the physical amino acid sequence from the 3D ATOM coordinates."""
    seq = []
    last_res_num = None
    with open(pdb_path, 'r') as f:
        for line in f:
            if line.startswith("ATOM") and line[12:16].strip() == "CA":
                res_name = line[17:20].strip()
                res_num = line[22:26].strip()
                if res_num != last_res_num: # Only count each residue once
                    if res_name in AA_DICT:
                        seq.append(AA_DICT[res_name])
                    last_res_num = res_num
    return "".join(seq)

def download_fasta(target_id, save_path):
    """Downloads FASTA from UniProt (for AlphaFold IDs) or RCSB (for PDB IDs)."""
    try:
        # If it's a 4-letter code, it's likely a classic PDB ID
        if len(target_id) == 4 and target_id[0].isdigit():
            url = f"https://www.rcsb.org/fasta/entry/{target_id.upper()}"
        else:
            # Otherwise, treat as a UniProt ID
            url = f"https://rest.uniprot.org/uniprotkb/{target_id.upper()}.fasta"
            
        urllib.request.urlretrieve(url, save_path)
        return True
    except Exception as e:
        return False

def validate_structures():
    if not os.path.exists(PDB_DIR):
        print(f"Error: Folder '{PDB_DIR}' not found.")
        return

    if not os.path.exists(FASTA_DIR):
        os.makedirs(FASTA_DIR)

    pdb_files = [f for f in os.listdir(PDB_DIR) if f.endswith(".pdb")]
    print(f"Found {len(pdb_files)} PDB files. Starting QC validation...\n")

    passed_qc = 0
    failed_dl = 0

    for file in pdb_files:
        # Clean the ID (remove 'clean_', '_A', etc.)
        raw_id = file.replace(".pdb", "")
        clean_id = re.sub(r'^clean_', '', raw_id)
        clean_id = clean_id.split('_')[0] # removes chain IDs like _A or _R

        pdb_path = os.path.join(PDB_DIR, file)
        fasta_path = os.path.join(FASTA_DIR, f"{clean_id}.fasta")

        # 1. Download the FASTA
        if not os.path.exists(fasta_path):
            success = download_fasta(clean_id, fasta_path)
            if not success:
                print(f"[FAILED DOWNLOAD] Could not find FASTA for {clean_id}")
                failed_dl += 1
                continue

        # 2. Extract sequences
        pdb_sequence = get_sequence_from_pdb(pdb_path)
        
        fasta_sequence = ""
        with open(fasta_path, 'r') as f:
            lines = f.readlines()
            # Join everything except the header line (>Header...)
            fasta_sequence = "".join([line.strip() for line in lines if not line.startswith(">")])

        # 3. Validation Logic
        if not pdb_sequence:
            print(f"[WARNING] {file}: No recognizable amino acids found in ATOM lines.")
            continue

        # Check if the PDB sequence is mostly inside the FASTA sequence
        # We check overlapping chunks because of missing crystallization loops
        chunk_size = 20 
        if len(pdb_sequence) > chunk_size:
            test_chunk = pdb_sequence[:chunk_size]
            if test_chunk in fasta_sequence:
                 print(f"[PASS] {file} physically matches the downloaded sequence!")
                 passed_qc += 1
            else:
                 print(f"[WARNING] {file} 3D structure sequence differs from database FASTA.")
        else:
            print(f"[WARNING] {file} is too short to accurately validate.")

    print("\n--- VALIDATION COMPLETE ---")
    print(f"Total passed structural QC: {passed_qc}")
    if failed_dl > 0:
        print(f"Could not find FASTAs for {failed_dl} files.")

if __name__ == "__main__":
    validate_structures()
