#!/bin/bash
export BIOSOLVEIT_LICENSE="/home/ibab/Downloads/flexx-6.4.1-Linux-x64/license.lic"

FLEXX="/home/ibab/Downloads/flexx-6.4.1-Linux-x64/flexx"
HYDE="/home/ibab/Downloads/hydescorer-2.4.1-Linux-x64/hydescorer"
LIGAND="/home/ibab/Seesar_docking/diphenhydramine.sdf"

PROT_BASE="/home/ibab/Docking_pipeline/All_prots"
REF_DIR="/home/ibab/Seesar_docking/reflig_sdfs_final"

OUT_DIR="/home/ibab/Seesar_docking/results_2000"
SCORE_FILE="/home/ibab/Seesar_docking/SCORES_2000.csv"
LOG="/home/ibab/Seesar_docking/RUN_2000.log"
TOP2000="/home/ibab/Seesar_docking/top_2000_results.csv"

mkdir -p "$OUT_DIR"

if [ ! -f "$SCORE_FILE" ]; then
    echo "Protein_ID,Vina_Score,FlexX_Score,HYDE_Lower_nM,HYDE_Upper_nM,FlexX_Poses" > "$SCORE_FILE"
fi

echo "🚀 Resumed with Dynamic Proteins: $(date)" | tee -a "$LOG"
ok=0; fail=0; skip=0; count=0
total=$(wc -l < "$TOP2000")

while IFS=',' read -r PID VINA; do
    [ -z "$PID" ] && continue
    ((count++))

    DOCKED="$OUT_DIR/${PID}_docked.sdf"
    SCORED="$OUT_DIR/${PID}_scored.sdf"

    if [ -f "$SCORED" ] && [ -s "$SCORED" ]; then
        ((skip++))
        echo "[$count/$total] $PID ⏭️" | tee -a "$LOG"
        continue
    fi

    # 1. FIND THE SPECIFIC PROTEIN AND SITE FOR THIS PID
    RECEPTOR=$(find "$PROT_BASE" -maxdepth 3 -name "${PID}.pdb" 2>/dev/null | head -n 1)
    REF_LIGAND="${REF_DIR}/${PID}.sdf"

    if [ -z "$RECEPTOR" ] || [ ! -f "$REF_LIGAND" ]; then
        echo "❌ [$count/$total] $PID ... Missing PDB or SDF!" | tee -a "$LOG"
        echo "$PID,$VINA,NA,NA,NA,0" >> "$SCORE_FILE"
        ((fail++)); continue
    fi

    echo -n "[$count/$total] $PID ... " | tee -a "$LOG"

    # 2. FLEXX (Using -p and -r instead of the static .flexx file)
    while true; do
        "$FLEXX" \
            -p "$RECEPTOR" \
            -r "$REF_LIGAND" \
            -i "$LIGAND" \
            -o "$DOCKED" \
            --max-nof-conf 10 \
            --thread-count 8 \
            -v 0 \
            > flexx_temp.log 2>&1

        if grep -qiE "License checkout.*failed|users already reached|FlexNet Licensing error" flexx_temp.log; then
            echo -n " 🕒 Busy... " | tee -a "$LOG"
            sleep 10
        else
            cat flexx_temp.log >> "$LOG"
            break 
        fi
    done

    if [ ! -f "$DOCKED" ] || [ ! -s "$DOCKED" ]; then
        echo "❌ FlexX failed" | tee -a "$LOG"
        echo "$PID,$VINA,NA,NA,NA,0" >> "$SCORE_FILE"
        ((fail++)); continue
    fi

    POSES=$(grep -c '^\$\$\$\$' "$DOCKED" 2>/dev/null || echo 0)
    if [ "${POSES:-0}" -eq 0 ]; then
        echo "⚠️ 0 poses" | tee -a "$LOG"
        echo "$PID,$VINA,NA,NA,NA,0" >> "$SCORE_FILE"
        ((fail++)); continue
    fi

    # 3. HYDE SCORER (Using the specific protein again)
    "$HYDE" \
        -p "$RECEPTOR" \
        -r "$DOCKED" \
        -i "$DOCKED" \
        -o "$SCORED" \
        --keep-input-sd-tags \
        -v 0 \
        2>> "$LOG"

    if [ ! -f "$SCORED" ] || [ ! -s "$SCORED" ]; then
        echo "✅ FlexX:$POSES ❌ HYDE failed" | tee -a "$LOG"
        echo "$PID,$VINA,NA,NA,NA,$POSES" >> "$SCORE_FILE"
        ((ok++)); continue
    fi

    # 4. EXTRACTION
    DOCK_SCORE=$(grep -A1 'BIOSOLVEIT\.DOCKING_SCORE>' "$SCORED" 2>/dev/null | grep -v "^>" | head -1 | tr -d ' \r\n')
    HYDE_LOWER=$(grep -A1 'BIOSOLVEIT\.HYDE_ESTIMATED_AFFINITY_LOWER_BOUNDARY' "$SCORED" 2>/dev/null | grep -v "^>" | head -1 | tr -d ' \r\n')
    HYDE_UPPER=$(grep -A1 'BIOSOLVEIT\.HYDE_ESTIMATED_AFFINITY_UPPER_BOUNDARY' "$SCORED" 2>/dev/null | grep -v "^>" | head -1 | tr -d ' \r\n')

    echo "✅ $POSES poses | FlexX:${DOCK_SCORE:-NA} | HYDE:${HYDE_LOWER:-NA}-${HYDE_UPPER:-NA} nM" | tee -a "$LOG"
    echo "$PID,$VINA,${DOCK_SCORE:-NA},${HYDE_LOWER:-NA},${HYDE_UPPER:-NA},$POSES" >> "$SCORE_FILE"
    ((ok++))

done < "$TOP2000"

rm -f flexx_temp.log
echo "DONE: $(date)" | tee -a "$LOG"
