import os
from Bio import PDB

# --- CONFIGURATION ---
INPUT_FOLDERS = ["./pdb_structures"]
OUTPUT_FOLDER = "./docking_ready_pdbs"
# ---------------------

class DockingSelect(PDB.Select):
    """
    Filters atoms to create a clean 'Receptor' file for docking.
    """
    def accept_atom(self, atom):
        # 1. Remove Hydrogens
        if atom.element == 'H':
            return False
        
        # 2. Remove ANISOU (Noise for docking)
        # 2 indicates ANISOU data implies disorder in Biopython terms
        if atom.is_disordered() == 2: 
             return False
        
        return True

    def accept_residue(self, residue):
        # 3. Remove Waters (id starts with 'W')
        if residue.id[0].startswith("W"):
            return False
            
        # 4. Remove Existing Ligands/HETATMs (id starts with 'H_')
        if residue.id[0].startswith("H_"):
            return False
            
        return True

def clean_alt_conformations(structure):
    """
    Resolves Alternate Conformations (AltLocs).
    Only acts on atoms where is_disordered() == 1 (True AltLocs).
    """
    for model in structure:
        for chain in model:
            for residue in chain:
                # Iterate over a copy of atoms to allow modification
                for atom in list(residue):
                    # --- THE FIX IS HERE ---
                    # Only process if flag is 1. 
                    # Flag 2 means ANISOU, which caused your crash earlier.
                    if atom.is_disordered() == 1:
                        
                        try:
                            # Find the best altloc (usually 'A')
                            # We wrap this in try/except just to be absolutely safe
                            if 'A' in atom.disordered_get_list():
                                atom.disordered_select('A')
                            
                            # Unwrap the disordered atom to a simple Atom object
                            clean_atom = atom.disordered_get()
                            clean_atom.set_occupancy(1.00)
                            
                            # Replace in residue
                            residue.detach_child(atom.id)
                            residue.add(clean_atom)
                        except AttributeError:
                            # Fallback if something weird happens, though checking == 1 should fix it
                            pass
                    else:
                        # Ensure standard atoms have occupancy 1.00
                        atom.set_occupancy(1.00)

def process_docking_prep(input_dirs, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    parser = PDB.PDBParser(QUIET=True)
    io = PDB.PDBIO()
    
    docking_selector = DockingSelect()

    for folder in input_dirs:
        if not os.path.isdir(folder):
            print(f"Skipping invalid folder: {folder}")
            continue
            
        print(f"--- Processing folder: {folder} ---")
        files = [f for f in os.listdir(folder) if f.endswith(".pdb")]
        
        for filename in files:
            file_path = os.path.join(folder, filename)
            try:
                # Parse
                structure = parser.get_structure(filename, file_path)
                
                # Resolve Alt Conformations first
                clean_alt_conformations(structure)
                
                # Save with Docking Selector
                io.set_structure(structure)
                output_path = os.path.join(output_dir, f"clean_{filename}")
                io.save(output_path, select=docking_selector)
                
                print(f"Ready for docking: {filename}")
                
            except Exception as e:
                print(f"Failed {filename}: {e}")

if __name__ == "__main__":
    process_docking_prep(INPUT_FOLDERS, OUTPUT_FOLDER)
    print("\nAll files cleaned.")
