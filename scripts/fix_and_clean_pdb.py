import os

# --- CONFIGURATION ---
INPUT_FOLDERS = ["./cif_to_pdb"]
OUTPUT_FOLDER = "./docking_ready_pdb"
# ---------------------

def parse_pdb_line_loose(line):
    """
    Parses a PDB line tolerantly. 
    Returns a dictionary of data if it's a valid protein atom, else None.
    """
    if not line.startswith("ATOM"):
        return None
    
    # We use explicit slicing for standard PDB columns, 
    # but we DO NOT parse the integer fields (Serial/Seq) to avoid crashes.
    # We just grab the strings.
    
    try:
        atom_name = line[12:16]   # Keep spaces
        alt_loc = line[16]
        res_name = line[17:20]
        chain_id = line[21]
        res_seq = line[22:26]     # Keep as string
        icode = line[26]          # Insertion code
        
        # Coordinates must be floats. If these fail, the line is garbage.
        x = float(line[30:38])
        y = float(line[38:46])
        z = float(line[46:54])
        
        # Occupancy & B-factor (defaults if missing)
        try:
            occ = float(line[54:60])
        except:
            occ = 1.00
        
        try:
            tfactor = float(line[60:66])
        except:
            tfactor = 0.00
            
        # Element - Try columns 76-78, fallback to atom name logic
        element = line[76:78].strip()
        if not element:
            # Guess element from atom name (e.g., " CA " -> C)
            raw_atom = atom_name.strip()
            if raw_atom[0].isdigit(): # Handle 1HG1
                element = raw_atom[1]
            else:
                element = raw_atom[0]
                
        return {
            "name": atom_name,
            "alt": alt_loc,
            "res": res_name,
            "chain": chain_id,
            "seq": res_seq,
            "icode": icode,
            "x": x, "y": y, "z": z,
            "occ": occ, "tf": tfactor,
            "elem": element
        }
    except ValueError:
        return None

def write_pdb_atom(f, serial, atom_data):
    """
    Writes a standard PDB line with a clean Serial Number.
    Format: ATOM  12345  CA  ALA A 123      12.345  12.345  12.345  1.00  0.00           C
    """
    # Create the standard PDB format string
    # We truncate serial at 99999 to prevent column merging, 
    # though typical docking receptors shouldn't be that big after cleaning waters.
    
    clean_serial = serial % 100000 
    
    line = (
        f"ATOM  {clean_serial:5d} {atom_data['name']}{atom_data['res']} {atom_data['chain']}{atom_data['seq']}{atom_data['icode']}   "
        f"{atom_data['x']:8.3f}{atom_data['y']:8.3f}{atom_data['z']:8.3f}"
        f"{1.00:6.2f}{atom_data['tf']:6.2f}          {atom_data['elem']:>2}\n"
    )
    f.write(line)

def process_file_renumber(filepath, output_path):
    with open(filepath, 'r') as f_in, open(output_path, 'w') as f_out:
        
        serial_counter = 1
        seen_atoms = set() # To handle duplicate alt-locs
        
        for line in f_in:
            # 1. Parse line strictly as text
            data = parse_pdb_line_loose(line)
            
            if not data:
                continue # Skip non-ATOM or malformed lines

            # --- DOCKING FILTERS ---
            
            # Filter A: Remove Hydrogens
            if data['elem'] == 'H':
                continue

            # Filter B: Remove Waters
            if data['res'] in ['HOH', 'WAT', 'TIP', 'DOD']:
                continue

            # Filter C: Alt Conformations
            # If alt is not empty and not A, skip. 
            if data['alt'] not in [' ', 'A', '1']:
                continue
            
            # Deduplication for AltLocs (A vs Space)
            # Unique ID: Chain + Seq + AtomName
            atom_uid = f"{data['chain']}_{data['seq']}_{data['name']}"
            if atom_uid in seen_atoms:
                continue
            seen_atoms.add(atom_uid)
            
            # --- WRITE CLEAN LINE ---
            write_pdb_atom(f_out, serial_counter, data)
            serial_counter += 1
            
        f_out.write("END\n")

def process_folders(input_dirs, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for folder in input_dirs:
        if not os.path.isdir(folder):
            continue

        print(f"--- Processing folder: {folder} ---")
        files = [f for f in os.listdir(folder) if f.endswith(".pdb")]
        
        for filename in files:
            file_path = os.path.join(folder, filename)
            output_path = os.path.join(output_dir, f"clean_{filename}")
            
            try:
                process_file_renumber(file_path, output_path)
                print(f"Re-normalized: {filename}")
            except Exception as e:
                print(f"Failed {filename}: {e}")

if __name__ == "__main__":
    process_folders(INPUT_FOLDERS, OUTPUT_FOLDER)
    print("\nAll files re-normalized and cleaned.")
