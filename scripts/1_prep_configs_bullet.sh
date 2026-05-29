#!/bin/bash
echo " BULLET SPEED: Pure AWK Box Calc + OpenBabel Timeout..."

mkdir -p configs vina_gpu_results

prep_one() {
    pdb_path="$1"
    prot_id=$(basename "$pdb_path" .pdb)
    
    # Skip if config already exists
    if [ -f "configs/config_${prot_id}.txt" ]; then return; fi
    
    # 1. Pure AWK (0.001 seconds) - No Python overhead!
    box_data=$(awk '/^ATOM/ {
        x=substr($0,31,8)+0; y=substr($0,39,8)+0; z=substr($0,47,8)+0;
        if(minx=="") {minx=maxx=x; miny=maxy=y; minz=maxz=z}
        if(x<minx) minx=x; if(x>maxx) maxx=x;
        if(y<miny) miny=y; if(y>maxy) maxy=y;
        if(z<minz) minz=z; if(z>maxz) maxz=z;
    } END {
        if(minx=="") exit 1;
        cx=(minx+maxx)/2; cy=(miny+maxy)/2; cz=(minz+maxz)/2;
        sx=maxx-minx+15; if(sx>80) sx=80;
        sy=maxy-miny+15; if(sy>80) sy=80;
        sz=maxz-minz+15; if(sz>80) sz=80;
        printf "%.3f %.3f %.3f %.3f %.3f %.3f\n", cx, cy, cz, sx, sy, sz;
    }' "$pdb_path" 2>/dev/null)

    if [ -z "$box_data" ]; then return; fi
    read cx cy cz sx sy sz <<< "$box_data"

    # 2. OpenBabel with a 5-SECOND TIMEOUT!
    # If it hangs, it gets killed automatically.
    timeout 5 obabel "$pdb_path" -O "${prot_id}.pdbqt" > /dev/null 2>&1
    
    # Check if pdbqt was actually created successfully
    if [ ! -f "${prot_id}.pdbqt" ]; then 
        echo "Skipped $prot_id (OpenBabel choked on dirty PDB)"
        return
    fi

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
    echo " Prepped: $prot_id"
}
export -f prep_one

# Push 25 files through at the exact same time
find All_prots -name "*.pdb" | xargs -P 25 -I {} bash -c 'prep_one "{}"'

echo " Bullet Config Generation Complete!"
