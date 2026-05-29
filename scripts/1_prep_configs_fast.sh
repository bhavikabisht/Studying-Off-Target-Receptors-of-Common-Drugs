#!/bin/bash
echo "⚡ Bypassing P2Rank. Using Whole-Protein Blind Docking..."

mkdir -p configs vina_gpu_results

prep_one() {
    pdb_path="$1"
    prot_id=$(basename "$pdb_path" .pdb)
    
    # Skip if config already exists
    if [ -f "configs/config_${prot_id}.txt" ]; then return; fi
    
    # 1. Calculate Whole Protein Box instantly
    box_data=$(python3 get_box.py "$pdb_path")
    if [ -z "$box_data" ]; then return; fi
    read cx cy cz sx sy sz <<< "$box_data"

    # 2. Convert to PDBQT
    obabel "$pdb_path" -O "${prot_id}.pdbqt" > /dev/null 2>&1

    # 3. Write Config File
    cat << INI > "configs/config_${prot_id}.txt"
receptor = ${prot_id}.pdbqt
ligand = diphenhydramine.pdbqt
center_x = $cx
center_y = $cy
center_z = $cz
size_x = $sx
size_y = $sy
size_z = $sz
num_modes = 9
energy_range = 5
thread = 8192
INI
    echo "✅ Prepped: $prot_id"
}
export -f prep_one

# Run 20 at a time safely since we removed heavy Java tools!
find All_prots -name "*.pdb" | xargs -P 20 -I {} bash -c 'prep_one "{}"'

echo "🏁 Lightning Config Generation Complete!"
