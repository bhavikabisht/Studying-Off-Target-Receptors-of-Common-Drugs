import pandas as pd

# ── Load data ──
pockets = pd.read_csv("all_pockets_extracted.csv")
tm      = pd.read_csv("tm_scores_results.csv",
                       names=['Folder','Protein_ID','TM_Score'])

# ── Get H1 reference pocket values ──
# Run this first to get reference values:
ref = pd.read_csv("p2rank_2.5/test_output/3RZE_clean.pdb_predictions.csv")
# OR if you ran it separately:
# ref = pd.read_csv("p2rank_reference_output/3RZE_clean.pdb_predictions.csv")
ref.columns = ref.columns.str.strip()
ref_score = float(ref[ref['rank']==1].iloc[0]['score'])
ref_surf  = float(ref[ref['rank']==1].iloc[0]['surf_atoms'])
ref_prob  = float(ref[ref['rank']==1].iloc[0]['probability'])

print(f"H1 Reference → Score:{ref_score}, SurfAtoms:{ref_surf}, Prob:{ref_prob}")

# ── Compute pocket similarity to H1 ──
pockets['Score_Sim'] = 1 - (
    abs(pockets['Top_Score'] - ref_score) / (abs(ref_score) + 1e-9)
).clip(0, 1)

pockets['Size_Sim'] = 1 - (
    abs(pockets['Surf_Atoms'] - ref_surf) / (ref_surf + 1e-9)
).clip(0, 1)

# ── Merge with TM scores ──
merged = pockets.merge(tm[['Protein_ID','TM_Score']],
                        on='Protein_ID', how='left')
merged['TM_Score'] = merged['TM_Score'].fillna(0)

# ── Final ranking score ──
merged['Rank_Score'] = (
    0.40 * merged['TM_Score'].clip(0,1) +
    0.30 * merged['Top_Probability'].fillna(0) +
    0.20 * merged['Score_Sim'].fillna(0) +
    0.10 * merged['Size_Sim'].fillna(0)
)

final = merged.sort_values('Rank_Score', ascending=False)
final.to_csv("all_proteins_ranked.csv", index=False)

print("\n🏆 TOP 30 CANDIDATES FOR DOCKING:")
print(final[['Protein_ID','Source','TM_Score',
             'Top_Probability','Num_Pockets',
             'Rank_Score']].head(30).to_string())

# Save top 50 for docking (take 50, after docking trim to 20)
top50 = final.head(50)
top50.to_csv("top50_for_docking.csv", index=False)
top50['Protein_ID'].to_csv("top50_ids.txt", index=False, header=False)
print("\nSaved: top50_for_docking.csv and top50_ids.txt")
