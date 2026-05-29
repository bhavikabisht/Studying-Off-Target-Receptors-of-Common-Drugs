import os
import time
import requests

# --- SETTINGS ---
INPUT_FILE = "string_db_input.txt"  # The file containing your 213 IDs
OUTPUT_FILE = "gene_names.txt"      # The new file that will contain the biological gene names

def fetch_gene_name(protein_id):
    """Queries the UniProt database to find the gene name for a PDB or UniProt ID."""
    protein_id = protein_id.strip().upper()
    
    # UniProt search query: Looks for either a direct AlphaFold/UniProt Accession OR a PDB cross-reference
    query_url = f"https://rest.uniprot.org/uniprotkb/search?query=(accession:{protein_id})+OR+(xref:pdb-{protein_id})&format=json&fields=gene_primary"
    
    try:
        response = requests.get(query_url)
        if response.status_code == 200:
            data = response.json()
            # Check if we got any results
            if data.get('results'):
                # Extract the primary gene name from the first result
                genes = data['results'][0].get('genes', [])
                if genes and 'geneName' in genes[0]:
                    return genes[0]['geneName']['value']
        return None
    except Exception as e:
        print(f"Error fetching {protein_id}: {e}")
        return None

def convert_ids_to_genes():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Could not find '{INPUT_FILE}'.")
        return

    print(f"Reading IDs from {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        # Read lines, strip whitespace, and ignore empty lines
        protein_ids = [line.strip() for line in f if line.strip()]

    print(f"Found {len(protein_ids)} IDs. Connecting to UniProt database...\n")
    
    gene_names = []
    missing_genes = []

    # Loop through each ID and fetch the gene name
    for i, p_id in enumerate(protein_ids, 1):
        print(f"[{i}/{len(protein_ids)}] Searching for {p_id}...", end=" ")
        
        gene_name = fetch_gene_name(p_id)
        
        if gene_name:
            print(f"Found: {gene_name}")
            gene_names.append(gene_name)
        else:
            print("Not found (Keeping original ID)")
            # If the database fails to find it, keep the original ID so you don't lose the data point
            gene_names.append(p_id) 
            missing_genes.append(p_id)
            
        # Add a tiny delay so we don't overwhelm and get blocked by the UniProt servers
        time.sleep(0.2) 

    # Remove duplicates (sometimes multiple PDBs map to the exact same gene)
    unique_genes = sorted(list(set(gene_names)))

    # Save to the new text file
    print(f"\nSaving {len(unique_genes)} unique gene names to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        for gene in unique_genes:
            f.write(gene + "\n")

    print("\n=== CONVERSION COMPLETE ===")
    if missing_genes:
        print(f"Note: {len(missing_genes)} IDs could not be converted and were left as-is.")

if __name__ == "__main__":
    convert_ids_to_genes()
