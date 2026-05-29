# rank_proteins.py
import pandas as pd
import numpy as np
import os

# ── Step 1: Load pocket data ──
print("Loading pocket data...")
pockets = pd.read_csv("all_pockets_extracted.csv")
print(f"  Total proteins in pocket file: {len(pockets)}")
print(f"  Columns: {list(pockets.columns)}")

# Force numeric columns
for col in ['Top_Score','Top_Probability','Surf_Atoms','Num_Pockets']:
    if col in pockets.columns:
        pockets[col] = pd.to_numeric(pockets[col], errors='coerce')

# ── Step 2: Load H1 reference pocket ──
ref_file = "p2rank_reference_output/3RZE_clean.pdb_predictions.csv"

if not os.path.exists(ref_file):
    print(f"ERROR: {ref_file} not found")
    exit(1)

ref = pd.read_csv(ref_file)
ref.columns = ref.columns.str.strip()

# Force numeric
for col in ['rank','score','probability','surf_atoms']:
    ref[col] = pd.to_numeric(ref[col], errors='coerce')

top_ref   = ref[ref['rank'] == 1].iloc[0]
ref_score = float(top_ref['score'])
ref_surf  = float(top_ref['surf_atoms'])
ref_prob  = float(top_ref['probability'])

print(f"\nH1 Reference Pocket:")
print(f"  Score:       {ref_score}")
print(f"  Surf Atoms:  {ref_surf}")
print(f"  Probability: {ref_prob}")

# ── Step 3: Compute pocket similarity ──
pockets['Score_Sim'] = (
    1 - (abs(pockets['Top_Score'] - ref_score) /
         (abs(ref_score) + 1e-9))
).clip(0, 1).fillna(0)

pockets['Size_Sim'] = (
    1 - (abs(pockets['Surf_Atoms'] - ref_surf) /
         (ref_surf + 1e-9))
).clip(0, 1).fillna(0)

# ── Step 4: Load TM scores ──
print("\nLoading TM scores...")
tm = pd.read_csv("tm_scores_results.csv",
                  names=['Folder','Protein_ID','TM_Score'])

# ⚡ THE FIX — force TM_Score to numeric, bad rows become NaN
tm['TM_Score'] = pd.to_numeric(tm['TM_Score'], errors='coerce')

# Drop rows where TM_Score is NaN (these were bad/header rows)
bad_rows = tm['TM_Score'].isna().sum()
print(f"  Total TM entries:    {len(tm)}")
print(f"  Bad/header rows:     {bad_rows} (dropped)")
tm = tm.dropna(subset=['TM_Score'])
print(f"  Clean TM entries:    {len(tm)}")
print(f"  TM Score range:      {tm['TM_Score'].min():.3f} – {tm['TM_Score'].max():.3f}")

# ── Step 5: Merge ──
merged = pockets.merge(
    tm[['Protein_ID','TM_Score']],
    on='Protein_ID', how='left'
)
merged['TM_Score'] = pd.to_numeric(
    merged['TM_Score'], errors='coerce').fillna(0)

# Double-check all columns are numeric before ranking
for col in ['TM_Score','Top_Probability','Score_Sim','Size_Sim']:
    merged[col] = pd.to_numeric(merged[col], errors='coerce').fillna(0)

print(f"\nMerged dataset: {len(merged)} proteins")
print(f"Proteins with TM > 0:  {(merged['TM_Score'] > 0).sum()}")
print(f"Proteins with TM > 0.5:{(merged['TM_Score'] > 0.5).sum()}")

# ── Step 6: Rank ──
merged['Rank_Score'] = (
    0.40 * merged['TM_Score'].clip(0, 1) +
    0.30 * merged['Top_Probability'] +
    0.20 * merged['Score_Sim'] +
    0.10 * merged['Size_Sim']
)

final = merged.sort_values('Rank_Score', ascending=False).drop_duplicates(subset=['Protein_ID'])

# ── Step 7: Display results ──
print("\n🏆 TOP 30 CANDIDATES:")
cols = ['Protein_ID','Source','TM_Score',
        'Top_Probability','Num_Pockets','Rank_Score']
print(final[cols].head(30).to_string(index=False))

# Multiple binding sites
multi = final[final['Num_Pockets'] > 1].head(20)
print(f"\n⚡ Proteins with MULTIPLE binding sites (top 20 of ranked):")
if len(multi) > 0:
    print(multi[['Protein_ID','Num_Pockets',
                 'TM_Score','Rank_Score']].to_string(index=False))
else:
    print("  None found")

# ── Step 8: Save ──
final.to_csv("all_proteins_ranked.csv", index=False)
print("\nSaved → all_proteins_ranked.csv")

top50 = final.head(50)
top50.to_csv("top50_for_docking.csv", index=False)
print("Saved → top50_for_docking.csv")

top50['Protein_ID'].to_csv("top50_ids.txt", index=False, header=False)
print("Saved → top50_ids.txt")

# ── Step 9: Verify ──
print(f"\n✅ Verification:")
print(f"  all_proteins_ranked.csv: {os.path.exists('all_proteins_ranked.csv')}")
print(f"  top50_for_docking.csv:   {os.path.exists('top50_for_docking.csv')}")
print(f"  top50_ids.txt:           {os.path.exists('top50_ids.txt')}")
print(f"  Lines in top50_ids.txt:  "
      f"{len(open('top50_ids.txt').readlines())}")

print("\nTop 50 IDs:")
print(open('top50_ids.txt').read())
