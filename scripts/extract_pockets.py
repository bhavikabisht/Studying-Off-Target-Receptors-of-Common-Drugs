# extract_pockets.py
import os
import glob
import pandas as pd

def extract_pockets(output_dir, source_label):
    results = []
    pred_files = glob.glob(f"{output_dir}/*_predictions.csv")
    print(f"Found {len(pred_files)} prediction files in {output_dir}")

    for pred_file in pred_files:
        # Get protein ID from filename
        basename = os.path.basename(pred_file)
        protein_id = basename.replace(".pdb_predictions.csv", "")

        try:
            df = pd.read_csv(pred_file)
            df.columns = df.columns.str.strip()

            if df.empty:
                results.append({
                    "Protein_ID": protein_id,
                    "Source": source_label,
                    "Num_Pockets": 0,
                    "Top_Score": None,
                    "Top_Probability": None,
                    "Center_X": None,
                    "Center_Y": None,
                    "Center_Z": None,
                    "Surf_Atoms": None
                })
                continue

            top = df[df['rank'] == 1].iloc[0]
            results.append({
                "Protein_ID":      protein_id,
                "Source":          source_label,
                "Num_Pockets":     len(df),           # multiple binding sites!
                "Top_Score":       round(float(top['score']), 4),
                "Top_Probability": round(float(top['probability']), 4),
                "Center_X":        round(float(top['center_x']), 3),
                "Center_Y":        round(float(top['center_y']), 3),
                "Center_Z":        round(float(top['center_z']), 3),
                "Surf_Atoms":      int(top['surf_atoms'])
            })

        except Exception as e:
            print(f"  Error in {protein_id}: {e}")

    return pd.DataFrame(results)

# Extract from both runs
print("Extracting AlphaFold pockets...")
af_df  = extract_pockets("p2rank_output_alphafold", "alphafold")

print("Extracting PDB pockets...")
pdb_df = extract_pockets("p2rank_output_pdb", "pdb")

# Combine both
all_pockets = pd.concat([af_df, pdb_df], ignore_index=True)
print(f"\nTotal proteins processed: {len(all_pockets)}")
print(f"Proteins with 0 pockets:  {(all_pockets['Num_Pockets']==0).sum()}")
print(f"Proteins with 1 pocket:   {(all_pockets['Num_Pockets']==1).sum()}")
print(f"Proteins with 2+ pockets: {(all_pockets['Num_Pockets']>1).sum()}")

# Save
all_pockets.to_csv("all_pockets_extracted.csv", index=False)
print("\nSaved: all_pockets_extracted.csv")
print(all_pockets.head(10))
