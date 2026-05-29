# save as: select_top20.py
import pandas as pd

# Load scores
scores = pd.read_csv("docking_scores.csv")
scores.columns = ['Protein_ID','Vina_Score','Pose_File']

# Remove failed
scores = scores[~scores['Vina_Score'].isin(['NA','NO_RECEPTOR'])].copy()
scores['Vina_Score'] = pd.to_numeric(scores['Vina_Score'])

# Sort by score (most negative = best binding)
scores_sorted = scores.sort_values('Vina_Score', ascending=True)

print("ALL 46 DOCKED PROTEINS RANKED:")
print(scores_sorted[['Protein_ID','Vina_Score']].to_string(index=False))

# Top 20
top20 = scores_sorted.head(20).reset_index(drop=True)
top20.index += 1

print("\n🏆 TOP 20 HITS:")
print(top20[['Protein_ID','Vina_Score']].to_string())

# Also load ranking info and merge
ranking = pd.read_csv("top50_for_docking.csv")
top20_full = top20.merge(
    ranking[['Protein_ID','TM_Score','Top_Probability','Num_Pockets']],
    on='Protein_ID', how='left'
)

print("\n🏆 TOP 20 WITH FULL INFO:")
print(top20_full.to_string(index=False))

# Save
top20_full.to_csv("TOP_20_FINAL.csv", index=False)
top20['Protein_ID'].to_csv("top20_ids.txt", index=False, header=False)
print("\nSaved → TOP_20_FINAL.csv")
print("Saved → top20_ids.txt")
