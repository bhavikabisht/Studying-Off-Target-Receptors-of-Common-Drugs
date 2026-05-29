#!/bin/bash
echo "⚙️ Preparing PDBQTs and Config files in parallel..."

export P2RANK_PATH="./p2rank_2.5/prank"
mkdir -p configs
mkdir -p vina_gpu_results
mkdir -p p2rank_output

# Function to process one protein
prep_one() {
    pdb_path="$1"
    prot_id=$(basename "$pdb_path" .pdb)
    
    # 1. Predict Pocket
    $P2RANK_PATH predict -f "$pdb_path" -o "p2rank_output/${prot_id}" > /dev/null 2>&1
    
    # Extract coords
    coords=$(awk -F, 'NR==2 {print $6, $7, $8}' "p2rank_output/${prot_id}/${prot_id}.pdb_predictions.csv" 2>/dev/null | tr -d ' ')
    center_x=$(echo $coords | awk '{print $1}')
    center_y=$(echo $coords | awk '{print $2}')
    center_z=$(echo $coords | awk '{print $3}')

    if [ -z "$center_x" ]; then
        return
    fi

    # 2. Convert to PDBQT
    obabel "$pdb_path" -O "${prot_id}.pdbqt" 2>/dev/null

    # 3. Generate the Vina-GPU Config File
    cat << EOF > "configs/config_${prot_id}.txt"
receptor = ${prot_id}.pdbqt
ligand = diphenhydramine.pdbqt

center_x = $center_x
center_y = $center_y
center_z = $center_z

size_x = 25
size_y = 25
size_z = 25

num_modes = 9
energy_range = 5
thread = 8192
EOF
}
export -f prep_one

# Run 15 prep jobs at the exact same time
find All_prots -name "*.pdb" | xargs -P 15 -I {} bash -c 'prep_one "{}"'

echo "✅ All configs generated successfully!"
