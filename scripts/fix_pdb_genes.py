import os
import time
import requests

# --- SETTINGS ---
INPUT_FILE = "gene_names.txt"          # The partially completed file
OUTPUT_FILE = "final_string_genes.txt" # Your final, perfectly mapped list

def get_gene_from_ebi(pdb_id):
    """Uses the EBI PDBe API to map a 4-letter PDB code to its Gene Name."""
    url = f"https://www.ebi.ac.uk/pdbe/api/mappings/uniprot/{pdb_id.lower()}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            pdb_key = pdb_id.lower()
            if pdb_key in data and 'UniProt' in data[pdb_key]:
                uniprot_data = data[pdb_key]['UniProt']
                
                # Extract the gene name from the first matched UniProt accession
                for acc, details in uniprot_data.items():
                    # Prioritize 'gene' (short symbol like CHRM2) over 'name' (long description)
                    raw_gene = details.get('gene')
                    if not raw_gene:
                        raw_gene = details.get('name')
                    
                    # EBI sometimes returns a list, sometimes a string. We handle both perfectly now.
                    if isinstance(raw_gene, list) and len(raw_gene) > 0:
                        return raw_gene[0]
                    elif isinstance(raw_gene, str):
                        return raw_gene
    except Exception as e:
        pass
    return None

def rescue_pdb_genes():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Could not find '{INPUT_FILE}'")
        return

    print("Loading current list...")
    with open(INPUT_FILE, 'r') as f:
        current_list = [line.strip() for line in f if line.strip()]

    final_genes = set()
    print("\nConnecting to EBI PDBe database to rescue 4-letter PDB codes...\n")

    for i, item in enumerate(current_list, 1):
        # If it's a 4-letter code, we fetch it
        if len(item) == 4 and item.isalnum():
            print(f"[{i}/{len(current_list)}] Rescuing {item}...", end=" ")
            gene = get_gene_from_ebi(item)
            
            if gene:
                print(f"Found -> {gene}")
                final_genes.add(gene)
            else:
                print("Failed (Keeping original)")
                final_genes.add(item)
            time.sleep(0.3) # Be polite to the EBI servers
        else:
            # It's already a full gene name (like FZD9), just add it directly
            final_genes.add(item)

    print(f"\nSaving {len(final_genes)} unique identifiers to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        for gene in sorted(final_genes):
            f.write(gene + "\n")

    print("\n=== RESCUE COMPLETE ===")
    print(f"Open {OUTPUT_FILE}, copy everything, and paste it into STRING-db!")

if __name__ == "__main__":
    rescue_pdb_genes()
