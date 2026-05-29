import pandas as pd

def rank_hyde_results(file_path, output_path):
    # 1. Load the CSV file
    # We specify 'NA' as a value to be treated as a missing number (NaN)
    df = pd.read_csv(file_path, sep=None, engine='python', na_values='NA')

    # 2. Convert affinity columns to numeric just in case
    df['HYDE_Lower_nM'] = pd.to_numeric(df['HYDE_Lower_nM'], errors='coerce')
    df['Vina_Score'] = pd.to_numeric(df['Vina_Score'], errors='coerce')

    # 3. Filter out rows where HYDE score is missing
    # This ensures your final list only contains validated SeeSAR hits
    df_valid = df.dropna(subset=['HYDE_Lower_nM']).copy()

    # 4. Rank by HYDE_Lower_nM (Ascending)
    # Smaller value = Higher Affinity = Top Rank
    df_ranked = df_valid.sort_values(by='HYDE_Lower_nM', ascending=True)

    # 5. Save the final ranked list
    df_ranked.to_csv(output_path, index=False)

    print("--- Ranking Summary ---")
    print(f"Original Proteins: {len(df)}")
    print(f"Proteins with HYDE Scores: {len(df_valid)}")
    print(f"\nTop 10 High-Affinity Hits:")
    print(df_ranked[['Protein_ID', 'HYDE_Lower_nM', 'Vina_Score']].head(10))

# Execute the script
rank_hyde_results('SCORES_2000.csv', 'Final_Ranked_OffTargets.csv')
