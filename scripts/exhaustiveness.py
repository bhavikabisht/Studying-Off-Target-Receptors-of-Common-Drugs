import os
import shutil
import urllib.request
import json
import time
from pathlib import Path
import re

def get_resolution_from_api(pdb_id):
    """
    Queries the RCSB PDB API for the resolution of a given PDB ID.
    """
    url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id.upper()}"
    try:
        # A 0.1s delay prevents the RCSB server from blocking us for spamming
        time.sleep(0.1) 
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            # Extract resolution
            resolutions = data.get("rcsb_entry_info", {}).get("resolution_combined", [])
            if resolutions:
                return float(resolutions[0])
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Silently skip 404s to avoid cluttering your terminal
            pass
        else:
            print(f"  [!] HTTP Error for {pdb_id}: {e.code}")
    except Exception as e:
        print(f"  [!] Error fetching data for {pdb_id}: {e}")
        
    return None

def filter_pdb_by_api(source_directory, target_directory, min_res=1.0, max_res=3.0):
    source_dir = Path(source_directory)
    target_dir = Path(target_directory)
    target_dir.mkdir(parents=True, exist_ok=True)

    pdb_files = list(source_dir.glob("*.pdb"))
    total_files = len(pdb_files)
    
    print(f"Found {total_files} files. Starting API lookup...")

    resolution_cache = {}
    copied_count = 0

    # UPDATE: This regex specifically looks for 'clean_' followed by 4 characters
    pdb_id_pattern = re.compile(r"clean_([a-zA-Z0-9]{4})\.pdb", re.IGNORECASE)

    for i, pdb_file in enumerate(pdb_files, 1):
        match = pdb_id_pattern.search(pdb_file.name)
        
        if not match:
            # If the file isn't named 'clean_XXXX.pdb', it skips it
            continue
            
        pdb_id = match.group(1).lower()

        # Check our cache first
        if pdb_id in resolution_cache:
            resolution = resolution_cache[pdb_id]
        else:
            # If not in cache, ask the RCSB API
            resolution = get_resolution_from_api(pdb_id)
            resolution_cache[pdb_id] = resolution

        # Check criteria and copy
        if resolution is not None and min_res <= resolution <= max_res:
            shutil.copy2(pdb_file, target_dir / pdb_file.name)
            copied_count += 1

        # Print progress update
        if i % 500 == 0:
            print(f"Processed {i}/{total_files} files... (Copied {copied_count} so far)")

    print("-" * 30)
    print("Done!")
    print(f"Successfully copied {copied_count} files to '{target_dir}'.")

# ==========================================
# CONFIGURATION
# ==========================================
if __name__ == "__main__":
    SOURCE_FOLDER = r"./Final_docking_pdbs(all_other_tissues)"
    TARGET_FOLDER = r"./resol_pdbs"
    
    filter_pdb_by_api(SOURCE_FOLDER, TARGET_FOLDER, min_res=1.0, max_res=3.0)
