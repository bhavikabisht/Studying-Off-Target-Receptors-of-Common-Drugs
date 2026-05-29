import os
import urllib.request

def download_pdbs(list_file="ALL_UNIQUE_PDB_IDS.txt", download_folder="pdb_structures"):
    # Create the folder if it doesn't exist
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    # Read the IDs
    with open(list_file, 'r') as f:
        pdb_ids = [line.strip() for line in f if line.strip()]

    print(f"Downloading {len(pdb_ids)} PDB files to '{download_folder}'...")

    for pdb_id in pdb_ids:
        # URL for the PDB file (PDB format)
        url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
        destination = os.path.join(download_folder, f"{pdb_id}.pdb")
        
        # Skip if already downloaded
        if os.path.exists(destination):
            print(f"Skipping {pdb_id} (already exists)")
            continue

        try:
            urllib.request.urlretrieve(url, destination)
            print(f"Downloaded: {pdb_id}")
        except Exception as e:
            print(f"Failed to download {pdb_id}: {e}")

    print("Download complete.")

if __name__ == "__main__":
    download_pdbs()
