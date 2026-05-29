#!/bin/bash

# --- CONFIGURATION ---
FLEXX_PATH="/home/ibab/Downloads/flexx-6.4.1-Linux-x64/flexx"
HYDE_PATH="/home/ibab/Downloads/hydescorer-2.4.1-Linux-x64/hydescorer"
LIGAND="diphenhydramine.sdf"
RESULTS_DIR="flexx_strict_results"

mkdir -p $RESULTS_DIR

echo "🚀 Starting BioSolveIT Pipeline for 50 Proteins..."

# Loop through all .pdbqt files in the current folder
for prot_pdbqt in *.pdbqt; do
    # Skip if it's a ligand/pose file
    [[ "$prot_pdbqt" == *"_poses"* ]] && continue
    
    prot_id=$(basename "$prot_pdbqt" .pdbqt)
    echo "--------------------------------------------------"
    echo "🧬 Processing Protein: $prot_id"

    # 1. Convert PDBQT to PDB
    echo "   [1/4] Converting to PDB..."
    obabel "$prot_pdbqt" -O "$RESULTS_DIR/${prot_id}_raw.pdb" -h

    # 2. Fix Clashes (Crucial for BioSolveIT)
    echo "   [2/4] Fixing coordinates (PDBFixer)..."
    pdbfixer "$RESULTS_DIR/${prot_id}_raw.pdb" --output="$RESULTS_DIR/${prot_id}_clean.pdb" --add-atoms=heavy --add-residues

    # 3. Find Reference Ligand (Vina result)
    # We use your Vina pose as the 'beacon' to tell FlexX where the pocket is
    vina_pose="vina_results/${prot_id}_poses.pdbqt"
    if [ -f "$vina_pose" ]; then
        obabel "$vina_pose" -O "$RESULTS_DIR/${prot_id}_beacon.sdf"
    else
        echo "   ⚠️ Warning: No Vina pose found for $prot_id. Skipping."
        continue
    fi

    # 4. FlexX Docking
    echo "   [3/4] Running FlexX Docking..."
    $FLEXX_PATH \
        -p "$RESULTS_DIR/${prot_id}_clean.pdb" \
        -r "$RESULTS_DIR/${prot_id}_beacon.sdf" \
        -i "$LIGAND" \
        -o "$RESULTS_DIR/${prot_id}_docked.sdf"

    # 5. HYDE Scoring
    if [ -f "$RESULTS_DIR/${prot_id}_docked.sdf" ]; then
        echo "   [4/4] Scoring with HYDE..."
        $HYDE_PATH \
            -p "$RESULTS_DIR/${prot_id}_clean.pdb" \
            -r "$RESULTS_DIR/${prot_id}_docked.sdf" \
            -i "$RESULTS_DIR/${prot_id}_docked.sdf" \
            -o "$RESULTS_DIR/${prot_id}_scored.sdf"
    else
        echo "   ❌ Error: FlexX failed to generate docking for $prot_id"
    fi
done

echo "--------------------------------------------------"
echo "🏁 Pipeline Complete. Check $RESULTS_DIR for results."
