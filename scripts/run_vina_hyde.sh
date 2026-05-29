#!/bin/bash

echo "🚀 Starting Vina-HYDE Consensus Scoring..."
mkdir -p hyde_consensus_results
echo "Protein_ID,HYDE_Score" > final_consensus_scores.csv

# Loop through the exact Vina pose files from your screenshot
for vina_pose in vina_results/*_poses.pdbqt; do
    [ -e "$vina_pose" ] || continue
    
    # Extract the protein ID (e.g., 'clean_3V2Y')
    prot_id=$(basename "$vina_pose" _poses.pdbqt)
    echo "🧬 Scoring $prot_id..."

    # 1. Convert Vina pose to SDF for HYDE
    obabel "$vina_pose" -O "hyde_consensus_results/${prot_id}_vina.sdf" 2>/dev/null
    
    # 2. Convert original receptor to PDB for HYDE
    obabel "prepared_receptors_mgl/${prot_id}.pdbqt" -O "hyde_consensus_results/${prot_id}_rec.pdb" 2>/dev/null

    # 3. Score using HYDE! (Using the absolute path we found earlier)
    /home/ibab/Downloads/hydescorer-2.4.1-Linux-x64/hydescorer -p "hyde_consensus_results/${prot_id}_rec.pdb" -i "hyde_consensus_results/${prot_id}_vina.sdf" -r "hyde_consensus_results/${prot_id}_vina.sdf" -o "hyde_consensus_results/${prot_id}_scored.sdf" > "hyde_consensus_results/${prot_id}_hyde.log" 2>&1

    # 4. Extract the HYDE score
    if [ -f "hyde_consensus_results/${prot_id}_hyde.log" ]; then
        score=$(grep -i "HYDE affinity" "hyde_consensus_results/${prot_id}_hyde.log" | awk '{print $3}')
        echo "${prot_id},${score}" >> final_consensus_scores.csv
    fi
    
    # Cleanup the temp PDB so your folder doesn't get cluttered
    rm "hyde_consensus_results/${prot_id}_rec.pdb"
done
echo "🎉 Consensus Scoring Complete!"
