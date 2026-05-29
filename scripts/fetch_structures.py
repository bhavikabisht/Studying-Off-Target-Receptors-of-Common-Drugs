import os
import requests
import time

# --- CONFIGURATION ---
INPUT_FILE = "unique_uniprotIds.txt"  # Your list of IDs
OUTPUT_FOLDER = "./protein_structures(not_cleaned)"
# ---------------------

def get_sequence_from_uniprot(uniprot_id):
    """
    Fetches the amino acid sequence from UniProt if we need to generate it.
    """
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"
    response = requests.get(url)
    
    if response.status_code == 200:
        # Parse FASTA format to get just the sequence string
        lines = response.text.splitlines()
        # Join all lines after the header (lines[1:])
        sequence = "".join(lines[1:])
        return sequence
    return None

def download_alphafold(uniprot_id, output_path):
    """
    Attempts to download from AlphaFold Database (EBI).
    Returns True if successful, False if not found.
    """
    # Try the latest version (v4). 
    url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(output_path, "w") as f:
                f.write(response.text)
            print(f"[AlphaFold] Downloaded: {uniprot_id}")
            return True
        elif response.status_code == 404:
            return False
    except Exception as e:
        print(f"Error checking AlphaFold for {uniprot_id}: {e}")
        return False

def generate_esmfold(uniprot_id, output_path):
    """
    Falls back to ESMFold API to GENERATE the structure on the fly.
    """
    print(f"[ESMFold] Generating structure for {uniprot_id}...")
    
    # 1. Get Sequence
    sequence = get_sequence_from_uniprot(uniprot_id)
    if not sequence:
        print(f"  -> Failed: Could not find sequence for {uniprot_id} on UniProt.")
        return False
        
    if len(sequence) > 400:
        print("  -> Warning: Sequence is long. ESMFold API might timeout.")

    # 2. Call ESMFold API
    # Meta AI provides this fast API for prediction
    url = "https://api.esmatlas.com/foldSequence/v1/pdb/"
    
    try:
        response = requests.post(url, data=sequence, verify=False) # verify=False fixes some SSL cert issues
        
        if response.status_code == 200:
            with open(output_path, "w") as f:
                f.write(response.text)
            print(f"  -> Success: Generated via ESMFold.")
            return True
        else:
            print(f"  -> Failed: ESMFold API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  -> Error calling ESMFold: {e}")
        return False

def main():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # Read IDs
    with open(INPUT_FILE, "r") as f:
        # Read lines and strip whitespace/newlines
        ids = [line.strip() for line in f if line.strip()]

    print(f"Processing {len(ids)} IDs...")

    for uniprot_id in ids:
        filename = f"{uniprot_id}.pdb"
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        
        # Skip if we already have the file locally
        if os.path.exists(output_path):
            print(f"Skipping {uniprot_id} (File exists)")
            continue

        # Step 1: Try AlphaFold Database (Pre-computed)
        success = download_alphafold(uniprot_id, output_path)
        
        # Step 2: If AlphaFold fails, Generate with ESMFold
        if not success:
            print(f"AlphaFold not found for {uniprot_id}. Attempting generation...")
            gen_success = generate_esmfold(uniprot_id, output_path)
            
            if not gen_success:
                # Log failure to a file so you can handle manually later
                with open("failed_ids.txt", "a") as err_log:
                    err_log.write(f"{uniprot_id}\n")

        # Be polite to the servers
        time.sleep(1) 

if __name__ == "__main__":
    # Suppress SSL warnings for ESMFold
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    main()
