#!/bin/bash
echo "🚀 Firing up QuickVina2-CUDA..."

# This guarantees it ONLY uses your specific GPU executable
VINA_GPU_PATH="/home/programs/gitw/Vina-CUDA/QuickVina2-CUDA/QuickVina2-GPU-2-1-CUDA"

mkdir -p vina_gpu_results

for config_file in configs/config_*.txt; do
    [ -e "$config_file" ] || continue
    
    # Extract the protein ID from the config filename
    filename=$(basename "$config_file")
    prot_id="${filename#config_}"
    prot_id="${prot_id%.txt}"
    
    echo "⚡ Docking $prot_id on GPU..."
    
    # Run the GPU binary!
    $VINA_GPU_PATH --config "$config_file" --out "vina_gpu_results/${prot_id}_gpu_pose.pdbqt" > /dev/null 2>&1
    
    # Delete the massive pdbqt receptor file immediately after docking to save hard drive space
    rm "${prot_id}.pdbqt" 2>/dev/null
done

echo "🏁 MASS GPU DOCKING COMPLETE!"
