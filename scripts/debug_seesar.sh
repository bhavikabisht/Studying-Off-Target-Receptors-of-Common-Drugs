#!/bin/bash
echo "🚀 Starting DEBUG BioSolveIT FlexX Docking..."
mkdir -p flexx_strict_results

# Check if the input directory exists
if [ ! -d "vina_results" ]; then
    echo "❌ Error: Folder 'vina_results' not found!"
    exit 1
fi

# Check for the ligand file
if [ ! -f "diphenhydramine.sdf" ]; then
    echo "❌ Error: 'diphenhydramine.sdf' is missing from the current folder!"
    exit 1
fi

for vina_pose in vina_results/*_poses.pdbqt; do
    # Handle case where no files match the pattern
    [ -e "$vina_pose" ] || { echo "❌ No matching .pdbqt files found in vina_results/"; break; }
    
    prot_id=$(basename "$vina_pose" _poses.pdbqt)
    echo "🧬 Attempting FlexX Docking for: $prot_id"

    # Step 1: Prep
    obabel "$vina_pose" -O "flexx_strict_results/${prot_id}_beacon.sdf"
obabel "${prot_id}.pdbqt" -O "flexx_strict_results/${prot_id}.pdb"

    # Step 2: Docking (Errors will now show in your terminal)
    /home/ibab/Downloads/flexx-6.4.1-Linux-x64/flexx \
        -p "flexx_strict_results/${prot_id}.pdb" \
        -r "flexx_strict_results/${prot_id}_beacon.sdf" \
        -i diphenhydramine.sdf \
        -o "flexx_strict_results/${prot_id}_docked.sdf"

    # Step 3: Scoring
    /home/ibab/Downloads/hydescorer-2.4.1-Linux-x64/hydescorer \
        -p "flexx_strict_results/${prot_id}.pdb" \
        -r "flexx_strict_results/${prot_id}_docked.sdf" \
        -i "flexx_strict_results/${prot_id}_docked.sdf" \
        -o "flexx_strict_results/${prot_id}_scored.sdf"
done

echo "🏁 Debug Script Finished."
