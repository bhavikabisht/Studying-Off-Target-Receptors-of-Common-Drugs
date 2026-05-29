import os
import time
import requests

# --- SETTINGS ---
INPUT_FILE = "string_db_input.txt"   # Your raw list of 213 PDB/AlphaFold IDs
OUTPUT_FILE = "final_gene_list.txt"  # The final, clean list for STRING-db

def get_gene_from_pdbe(pdb_id):
    """Maps a 4-letter PDB code to its Gene Name via EBI."""
    url = f"https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/{pdb_id.lower()}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            pdb_key = pdb_id.lower()
            if pdb_key in data and 'UniProt' in data[pdb_key]:
                uniprot_data = data[pdb_key]['UniProt']
                for acc, details in uniprot_data.items():
                    raw_gene = details.get('gene') or details.get('name')
                    if isinstance(raw_gene, list) and len(raw_gene) > 0:
                        return raw_gene[0]
                    elif isinstance(raw_gene, str):
                        return raw_gene
    except Exception:
        pass
    return None

def get_gene_from_uniprot(uniprot_id):
    """Maps a UniProt/AlphaFold ID to its Gene Name."""
    url = f"https://rest.uniprot.org/uniprotkb/search?query=(accession:{uniprot_id})&format=json&fields=gene_primary"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                genes = data['results'][0].get('genes', [])
                if genes and 'geneName' in genes[0]:
                    return genes[0]['geneName']['value']
    except Exception:
        pass
    return None

def run_unified_extraction():
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] Could not find '{INPUT_FILE}'.")
        return

    print(f"Reading targets from {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        raw_ids = [line.strip().upper() for line in f if line.strip()]

    print(f"Loaded {len(raw_ids)} IDs. Routing to biological databases...\n")
    
    final_genes = set()
    failed_ids = []

    for i, target_id in enumerate(raw_ids, 1):
        print(f"[{i}/{len(raw_ids)}] Translating {target_id}...", end=" ")
        
        gene_name = None
        
        # Routing Logic: If it's exactly 4 alphanumeric characters, it's a PDB code
        if len(target_id) == 4 and target_id.isalnum():
            gene_name = get_gene_from_pdbe(target_id)
        else:
            # Otherwise, treat it as a UniProt/AlphaFold accession code
            gene_name = get_gene_from_uniprot(target_id)
            
        # Add to our set if successful
        if gene_name:
            print(f"Found -> {gene_name}")
            final_genes.add(gene_name)
        else:
            print("Failed (Keeping original ID)")
            final_genes.add(target_id)
            failed_ids.append(target_id)
            
        time.sleep(0.2) # API rate-limiting buffer

    # Save the consolidated list
    print(f"\nSaving {len(final_genes)} unique biological genes to '{OUTPUT_FILE}'...")
    with open(OUTPUT_FILE, 'w') as f:
        for gene in sorted(final_genes):
            f.write(gene + "\n")

    print("\n=== EXTRACTION COMPLETE ===")
    if failed_ids:
        print(f"Note: {len(failed_ids)} IDs could not be mapped and were kept in their original format.")
    print(f"Your system biology list is ready. Open {OUTPUT_FILE} and paste it into STRING-db!")

if __name__ == "__main__":
    run_unified_extraction()
