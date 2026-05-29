# save as: run_docking_v125.sh
#!/bin/bash

cd ~/Docking_pipeline/autodock_top50

LIGAND="diphenhydramine.pdbqt"
RECEPTOR_DIR="prepared_receptors_mgl"
CENTERS="pocket_centers.csv"
OUT_DIR="vina_results"
SCORE_FILE="docking_scores.csv"

mkdir -p $OUT_DIR
echo "Protein_ID,Vina_Score_kcal,Pose_File" > $SCORE_FILE

echo "Receptors: $RECEPTOR_DIR"
echo "Ligand: $LIGAND ($(wc -l < $LIGAND) lines)"
echo ""

while IFS=',' read -r PID CX CY CZ; do
    [ "$PID" = "Protein_ID" ] && continue
    [ -z "$PID" ] && continue

    RECEPTOR="$RECEPTOR_DIR/${PID}.pdbqt"
    POSE="$OUT_DIR/${PID}_poses.pdbqt"
    LOGF="$OUT_DIR/${PID}_log.txt"

    echo "━━━ $PID ━━━"

    if [ ! -f "$RECEPTOR" ]; then
        echo "  ❌ Receptor missing"
        echo "$PID,NO_RECEPTOR,NA" >> $SCORE_FILE
        continue
    fi

    # Verify 0 torsions
    torsions=$(grep "active torsions" "$RECEPTOR" | \
               head -1 | awk '{print $2}')
    lines=$(wc -l < "$RECEPTOR")
    echo "  Receptor: $lines lines, $torsions torsions"
    echo "  Center: ($CX, $CY, $CZ)"

    if [ "$torsions" != "0" ]; then
        echo "  ⚠️  WARNING: receptor has torsions - may be incorrectly prepared"
    fi

    # Run Vina v1.2.5 (no --log flag - redirect output)
    vina \
        --receptor "$RECEPTOR" \
        --ligand "$LIGAND" \
        --center_x "$CX" \
        --center_y "$CY" \
        --center_z "$CZ" \
        --size_x 25 \
        --size_y 25 \
        --size_z 25 \
        --exhaustiveness 16 \
        --num_modes 9 \
        --out "$POSE" \
        2>&1 | tee "$LOGF"

    # Parse score from output
    # Vina 1.2.5 format: "   1    -8.3    0.000    0.000"
    BEST=$(grep -E "^\s+1\s+[-]" "$LOGF" 2>/dev/null | \
           awk '{print $2}' | head -1)

    if [ -n "$BEST" ]; then
        echo "  ✅ Best score: $BEST kcal/mol"
        echo "$PID,$BEST,$POSE" >> $SCORE_FILE
    else
        echo "  ⚠️  No score obtained"
        echo "$PID,NA,NA" >> $SCORE_FILE
    fi
    echo ""

done < $CENTERS

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All docking complete!"
echo ""
echo "Top hits:"
tail -n +2 $SCORE_FILE | \
    grep -v "NA\|NO_" | \
    sort -t',' -k2 -n | \
    head -20
