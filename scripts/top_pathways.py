import requests
import pandas as pd
import re

# --- CONFIGURATION ---
FILE_NAME = "TOP_100_TARGETS.csv"
DRUG_NAME = "Diphenhydramine"
KNOWN_GENES = ['HRH1', 'CHRM1', 'CHRM2', 'CHRM3', 'CHRM4', 'CHRM5', 'SCN5A', 'KCNH2', 'SLC6A4', 'SLC6A3']

def extract_id(target_string):
    """Extracts PDB ID or UniProt ID from AlphaFold strings."""
    clean_str = str(target_string).replace("clean_", "").replace("_docked", "").replace(".pdb", "")
    
    pdb_match = re.search(r'([0-9][a-zA-Z0-9]{3})', clean_str)
    af_match = re.search(r'AF-([A-Z0-9]+)-F\d+', clean_str)
    
    if af_match: return af_match.group(1).upper() # Gets UniProt ID directly
    if pdb_match: return pdb_match.group(1).upper() # Gets PDB ID
    return clean_str[:10].upper()

def map_ids_to_genes(ids):
    print("Step 1: Mapping Target IDs to Gene Symbols using MyGene.info...")
    unique_ids = list(set([str(i).upper() for i in ids if i]))
    print(f" -> Searching for {len(unique_ids)} unique IDs...")
    
    mapping = {}
    try:
        # MyGene perfectly translates PDB and UniProt IDs directly to Gene Symbols
        res = requests.post('https://mygene.info/v3/query', 
                            data={'q': ",".join(unique_ids), 'scopes': 'pdb,uniprot', 'fields': 'symbol', 'species': 'human'}).json()
        
        for entry in res:
            if 'symbol' in entry:
                mapping[entry['query'].upper()] = entry['symbol']
        
        print(f" -> Successfully mapped {len(mapping)} Gene Symbols!")
        return mapping
    except Exception as e:
        print(f"❌ Mapping failed: {e}")
        return {}

def run_enrichr(genes):
    print("\nStep 2: Finding Pathways via Enrichr...")
    if not genes:
        print("❌ ERROR: Gene list is empty! Cannot run pathway analysis.")
        return pd.DataFrame()

    print(f" -> Sending {len(genes)} properly formatted genes to Enrichr...")
    ENRICHR_URL = 'https://maayanlab.cloud/Enrichr/addList'
    payload = {'list': (None, '\n'.join(genes)), 'description': (None, 'Seesar Results')}
    
    try:
        response = requests.post(ENRICHR_URL, files=payload)
        if not response.ok:
            print(f"❌ Enrichr Server Error: {response.status_code}")
            return pd.DataFrame()
            
        data = response.json()
        user_list_id = data['userListId']
        
        pathways = []
        for db in ['KEGG_2021_Human', 'Reactome_2022']:
            res = requests.get(f"https://maayanlab.cloud/Enrichr/enrich?userListId={user_list_id}&backgroundType={db}").json()
            for entry in res[db][:20]:
                pathways.append({
                    'Database': db,
                    'Pathway_Name': entry[1],
                    'P_value': entry[2],
                    'Overlapping_Genes': entry[5]
                })
        return pd.DataFrame(pathways)
    except Exception as e:
        print(f"❌ Enrichr request failed: {e}")
        return pd.DataFrame()

# --- EXECUTION FLOW ---
try:
    df = pd.read_csv(FILE_NAME)
    
    hyde_cols = [c for c in df.columns if 'hyde' in c.lower() or 'affinity' in c.lower()]
    flexx_cols = [c for c in df.columns if 'flexx' in c.lower() or 'score' in c.lower()]
    
    hyde_col = hyde_cols[0] if hyde_cols else df.columns[2]
    flexx_col = flexx_cols[0] if flexx_cols else df.columns[1]
    target_col = df.columns[0]
    
    df[hyde_col] = pd.to_numeric(df[hyde_col], errors='coerce')
    df[flexx_col] = pd.to_numeric(df[flexx_col], errors='coerce')
    df = df.sort_values(by=[hyde_col, flexx_col], ascending=True)
    top_100 = df.head(100).copy()

    # Process IDs and MAP
    top_100['Extracted_ID'] = top_100[target_col].apply(extract_id)
    mapping_dict = map_ids_to_genes(top_100['Extracted_ID'].tolist())
    top_100['Gene_Symbol'] = top_100['Extracted_ID'].str.upper().map(mapping_dict)

    # Label Targets
    top_100['Target_Type'] = top_100['Gene_Symbol'].apply(
        lambda x: 'Known Off-target' if str(x).upper() in KNOWN_GENES else 'Novel Off-target'
    )

    # Pathway Analysis
    genes_for_analysis = top_100['Gene_Symbol'].dropna().unique().tolist()
    
    pathway_df = run_enrichr(genes_for_analysis)

    # Save Results
    top_100.to_csv("Analyzed_Targets.csv", index=False)
    
    if not pathway_df.empty:
        novel_pathway_mask = ~pathway_df['Pathway_Name'].str.contains('Histamine|Cholinergic|Neurotransmitter|Autonomic', case=False, na=False)
        novel_pathways = pathway_df[novel_pathway_mask].head(10)
        novel_pathways.to_csv("Top_10_Novel_Pathways.csv", index=False)
        print(f"\n✅ SUCCESS: Top 10 Novel Pathways saved to Top_10_Novel_Pathways.csv")
    else:
        print("\n⚠️ Pathway analysis yielded no results.")

    print(f"✅ SUCCESS: Top 100 Targets mapped. Results saved to Analyzed_Targets.csv")

except FileNotFoundError:
    print(f"❌ ERROR: Could not find {FILE_NAME}.")
