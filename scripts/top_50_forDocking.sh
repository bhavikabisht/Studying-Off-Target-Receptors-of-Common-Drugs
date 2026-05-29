# save as: copy_top50.sh
#!/bin/bash

echo "Creating Top50_for_docking folder..."
mkdir -p Top50_for_docking

if [ ! -f "top50_ids.txt" ]; then
    echo "ERROR: top50_ids.txt not found!"
    echo "Run rank_proteins.py first"
    exit 1
fi

echo "Copying PDB files..."
found=0
missing=0

while IFS= read -r pid; do
    [ -z "$pid" ] && continue   # skip empty lines

    pdb_path=$(find All_prots/ -name "${pid}.pdb" 2>/dev/null | head -1)

    if [ -n "$pdb_path" ]; then
        cp "$pdb_path" Top50_for_docking/
        echo "  ✅ $pid"
        ((found++))
    else
        echo "  ❌ NOT FOUND: $pid"
        ((missing++))
    fi

done < top50_ids.txt

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Found & copied: $found"
echo "Not found:      $missing"
echo "Total in folder: $(ls Top50_for_docking/*.pdb 2>/dev/null | wc -l)"
