# save as: prepare_receptors_mgl.sh
#!/bin/bash

PYTHONSH="/home/ibab/mgltools_x86_64Linux2_1.5.7/bin/pythonsh"
PREP="/home/ibab/mgltools_x86_64Linux2_1.5.7/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_receptor4.py"
PROT_DIR="Top50_for_docking"
OUT_DIR="prepared_receptors_mgl"

mkdir -p $OUT_DIR

success=0
failed=0

for pdb in $PROT_DIR/*.pdb; do
    pid=$(basename "$pdb" .pdb)
    out="$OUT_DIR/${pid}.pdbqt"

    echo -n "Preparing $pid ... "

    $PYTHONSH $PREP \
        -r "$pdb" \
        -o "$out" \
        -A hydrogens \
        -U nphs_lps \
        2>/dev/null

    if [ -f "$out" ] && [ $(wc -l < "$out") -gt 10 ]; then
        echo "✅ $(wc -l < $out) lines"
        ((success++))
    else
        echo "❌ FAILED"
        ((failed++))
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Success: $success | Failed: $failed"
echo ""
echo "File sizes:"
ls -lh $OUT_DIR/*.pdbqt | awk '{print $5, $9}' | sort -k1 -h
