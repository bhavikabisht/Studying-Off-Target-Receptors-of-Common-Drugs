#!/bin/bash

PROT_DIR="/home/ibab/Docking_pipeline/Top50_for_docking"
OUT_DIR="prepared_receptors"
mkdir -p $OUT_DIR

echo "Preparing receptors..."
success=0
failed=0

for pdb in $PROT_DIR/*.pdb; do
    pid=$(basename "$pdb" .pdb)
    out="$OUT_DIR/${pid}.pdbqt"
    
    # Try prepare_receptor first (from MGLTools/AutoDockTools)
    python3 -c "
import subprocess, sys
r = subprocess.run([
    'prepare_receptor',
    '-r', '$pdb',
    '-o', '$out',
    '-A', 'hydrogens',
    '-U', 'nphs_lps'
], capture_output=True)
sys.exit(r.returncode)
" 2>/dev/null

    # If that failed, use obabel as fallback
    if [ ! -f "$out" ] || [ ! -s "$out" ]; then
        obabel "$pdb" -O "$out" \
            -p 7.4 \
            --partialcharge gasteiger 2>/dev/null
    fi

    if [ -f "$out" ] && [ -s "$out" ]; then
        echo "  ✅ $pid"
        ((success++))
    else
        echo "  ❌ FAILED: $pid"
        ((failed++))
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Prepared: $success"
echo "Failed:   $failed"
echo "Files in prepared_receptors/: $(ls $OUT_DIR/*.pdbqt 2>/dev/null | wc -l)"
