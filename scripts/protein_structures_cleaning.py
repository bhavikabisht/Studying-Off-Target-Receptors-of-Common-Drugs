import os
from Bio import PDB
from Bio.PDB import PDBIO, Select

# ================= CONFIGURATION =================
# Change these folder names to match your actual directories
INPUT_FOLDER = "protein_structures(not_cleaned)"      # Where your raw PDBs are
OUTPUT_FOLDER = "protein_structures(cleaned)"       # Where clean PDBs will go
# =================================================

class CleanStructure(Select):
    """
    Custom filter to remove 'noise' from PDB files.
    """
    def accept_residue(self, residue):
        # 1. Remove Waters and Solvent
        # Common names for water in PDB files
        if residue.get_resname() in ['HOH', 'WAT', 'SOL', 'DOD', 'TIP']:
            return 0
        return 1

    def accept_atom(self, atom):
        # 2. Remove Hydrogens
        # Most docking software requires you to add fresh hydrogens 
        # based on pH, so we strip the static ones from the crystal.
        if atom.element == 'H':
            return 0
            
        # 3. Remove Alternate Conformers
        # PDBs often have two positions for a side chain (A and B).
        # We keep only the primary one (' ' or 'A').
        altloc = atom.get_altloc()
        if altloc not in [' ', 'A']:
            return 0
            
        return 1

def remove_aniso_records(structure):
    """
    Iterates through all atoms and explicitly removes ANISOU annotations
    so they are not written to the file.
    """
    for atom in structure.get_atoms():
        if "ANISOU" in atom.xtra:
            del atom.xtra["ANISOU"]

def process_folder():
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    parser = PDB.PDBParser(QUIET=True)
    io = PDBIO()
    clean_selector = CleanStructure()

    # Get list of pdb files
    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.pdb')]
    print(f"Found {len(files)} files. Starting cleanup...")

    count = 0
    for filename in files:
        in_path = os.path.join(INPUT_FOLDER, filename)
        out_path = os.path.join(OUTPUT_FOLDER, filename)

        try:
            # 1. Parse Structure
            structure = parser.get_structure("temp", in_path)

            # 2. Remove ANISOU (Anisotropic Temperature Factors)
            # These are extra lines describing thermal vibration that 
            # confuse some docking programs.
            remove_aniso_records(structure)

            # 3. Save Cleaned Structure
            # The 'select' argument applies the CleanStructure class logic
            io.set_structure(structure)
            io.save(out_path, select=clean_selector)
            
            count += 1
            if count % 100 == 0:
                print(f"  Processed {count} files...")

        except Exception as e:
            print(f"  [Error] Could not process {filename}: {e}")

    print("-" * 30)
    print(f"Successfully cleaned {count} files.")
    print(f"Clean files are saved in: {OUTPUT_FOLDER}")

if __name__ == "__main__":
    process_folder()
