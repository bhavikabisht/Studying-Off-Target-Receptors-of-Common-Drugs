import os
import subprocess

# --- SETTINGS ---
FASTA_DIR = "Target_FASTAs"
# Put the exact name of your primary H1 FASTA file here
H1_FASTA_PATH = "rcsb_pdb_3RZE.fasta" 

# The temporary combined file and the final output file
COMBINED_FASTA = "master_sequences.fasta"
OUTPUT_ALN = "h1_offtargets_alignment.aln"

def prepare_and_run_msa():
    if not os.path.exists(FASTA_DIR):
        print(f"Error: Could not find '{FASTA_DIR}' folder.")
        return
    if not os.path.exists(H1_FASTA_PATH):
        print(f"Error: Could not find the main H1 FASTA '{H1_FASTA_PATH}'.")
        return

    # 1. Merge all FASTAs into one file
    print("Bundling sequences into a single multi-FASTA file...")
    
    # We read the H1 sequence first to make it the 'Reference' at the top
    with open(H1_FASTA_PATH, 'r') as h1_file:
        h1_content = h1_file.read()

    # Extract the ID from the H1 file so we don't accidentally add it twice
    h1_id = h1_content.split('\n')[0].replace(">", "").strip()

    merged_count = 1
    with open(COMBINED_FASTA, 'w') as out_file:
        # Write H1 first
        out_file.write(h1_content + "\n")
        
        # Loop through the Target_FASTAs folder
        for fasta_file in os.listdir(FASTA_DIR):
            if fasta_file.endswith(".fasta"):
                filepath = os.path.join(FASTA_DIR, fasta_file)
                
                with open(filepath, 'r') as f:
                    content = f.read()
                    file_id = content.split('\n')[0].replace(">", "").strip()
                    
                    # Prevent duplicating the H1 receptor if it's sitting in the folder
                    if file_id != h1_id:
                        out_file.write(content + "\n")
                        merged_count += 1

    print(f"Successfully combined {merged_count} sequences into {COMBINED_FASTA}")

    # 2. Run Clustal Omega
    print("\nStarting Clustal Omega Multiple Sequence Alignment...")
    print("This requires heavy computation and may take a few minutes. Please wait...")
    
    # The command: clustalo -i input.fasta -o output.aln --outfmt=clustal --force
    clustalo_cmd = [
        "clustalo", 
        "-i", COMBINED_FASTA, 
        "-o", OUTPUT_ALN, 
        "--outfmt=clustal", 
        "--force"
    ]

    try:
        subprocess.run(clustalo_cmd, check=True)
        print("\n--- MSA COMPLETE ---")
        print(f"Your final alignment is saved as: {OUTPUT_ALN}")
        print("You can open this .aln file in text editors or alignment viewers like Jalview!")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Clustal Omega failed to run. Check if it is installed correctly.")
        print(e)
    except FileNotFoundError:
        print("\n[ERROR] The 'clustalo' command was not found. Please install Clustal Omega.")

if __name__ == "__main__":
    prepare_and_run_msa()
