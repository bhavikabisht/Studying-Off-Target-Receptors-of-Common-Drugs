import pandas as pd
import os

# Load your top 50 ranking
top50 = pd.read_csv("top50_for_docking.csv")

# Load P2Rank predictions for each protein
# Centers are already in top50_for_docking.csv (Center_X, Center_Y, Center_Z)
print("Checking pocket centers in top50_for_docking.csv...")
print(top50[['Protein_ID','Center_X','Center_Y','Center_Z']].to_string())

# Check how many have valid centers
missing = top50[top50['Center_X'].isna()]
print(f"\nProteins missing pocket centers: {len(missing)}")
if len(missing) > 0:
    print(missing[['Protein_ID']].to_string())

# Save centers to a lookup file
centers = top50[['Protein_ID','Center_X','Center_Y','Center_Z']].dropna()
centers.to_csv("pocket_centers.csv", index=False)
print(f"\nSaved {len(centers)} pocket centers → pocket_centers.csv")
