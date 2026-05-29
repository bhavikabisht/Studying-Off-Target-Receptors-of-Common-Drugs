# save as: remake_receptors_fixed.sh
#!/bin/bash

PYTHONSH="/home/ibab/mgltools_x86_64Linux2_1.5.7/bin/pythonsh"
PREP="/home/ibab/mgltools_x86_64Linux2_1.5.7/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_receptor4.py"
PROT_DIR="../Top50_for_docking"
OUT_DIR="prepared_receptors_mgl"

mkdir -p $OUT_DIR
success=0
failed=0

echo "Remaking all 50 receptors with MGLTools..."
echo "PDB source: $PROT_DIR"
echo ""

for pdb in $PROT_DIR/*.pdb; do
    pid=$(basename "$pdb" .pdb)
    out="$OUT_DIR/${pid}.pdbqt"

    echo -n "  $pid ... "

    $PYTHONSH $PREP \
        -r "$pdb" \
        -o "$out" \
        -A hydrogens \
        -U nphs_lps \
        2>/dev/null

    if [ -f "$out" ] && [ -s "$out" ]; then
        torsions=$(grep "active torsions" "$out" | \
                   head -1 | awk '{print $2}')
        lines=$(wc -l < "$out")
        echo "✅ ($lines lines, $torsions torsions)"
        ((success++))
    else
        echo "❌ FAILED"
        ((failed++))
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Success: $success | Failed: $failed"
