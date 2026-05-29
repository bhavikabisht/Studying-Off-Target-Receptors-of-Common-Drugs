echo "Protein_ID,Affinity_Lower_nM,Ligand_Efficiency" > strict_scores.csv

# 1. Extract the scores
for sdf_file in flexx_strict_results/*_scored.sdf; do
    [ -e "$sdf_file" ] || continue
    prot_id=$(basename "$sdf_file" _scored.sdf)
    affinity=$(awk '/HYDE_ESTIMATED_AFFINITY_LOWER_BOUNDARY/ {getline; print $1; exit}' "$sdf_file")
    efficiency=$(awk '/HYDE_LIGAND_EFFICIENCY/ {getline; print $1; exit}' "$sdf_file")
    
    if [ ! -z "$affinity" ]; then
        echo "$prot_id,$affinity,$efficiency" >> strict_scores.csv
    fi
done

# 2. Sort, Rank, and Separate the Top 15
echo "🏆 Separating Top 15 Targets..."
# Sort numerically by affinity, skip the header, take top 15
tail -n +2 strict_scores.csv | sort -t, -k2 -n | head -n 15 > top_15_list.txt

# Loop through that top 15 list and copy the raw protein files to the Winners folder
while IFS=, read -r prot_id affinity eff; do
    echo "Copying $prot_id (Affinity: $affinity nM)"
    # Copy the clean receptor to the Top 15 folder
    cp "prepared_receptors_mgl/${prot_id}.pdbqt" "Final_Top_15_Hits/"
    # Copy the successfully docked FlexX pose to the Top 15 folder
    cp "flexx_strict_results/${prot_id}_scored.sdf" "Final_Top_15_Hits/"
done < top_15_list.txt

echo "✅ Done! Your absolute best hits are neatly packaged in the 'Final_Top_15_Hits' folder."
