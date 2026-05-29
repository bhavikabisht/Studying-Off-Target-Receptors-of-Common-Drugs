import os

# --- SETTINGS ---
INPUT_PDB = "3RZE.pdb"
OUTPUT_PDB = "clean_3RZE.pdb"

def clean_pdb():
    if not os.path.exists(INPUT_PDB):
        print(f"[ERROR] Could not find '{INPUT_PDB}'.")
        return

    print(f"Reading {INPUT_PDB} and applying strict cleaning filters...")
    
    atom_count = 0
    removed_hetatm = 0
    removed_hydrogens = 0
    removed_alt_locs = 0

    with open(INPUT_PDB, 'r') as f_in, open(OUTPUT_PDB, 'w') as f_out:
        for line in f_in:
            # 1. Drop all Ligands, Lipids, and Waters (HETATM)
            if line.startswith("HETATM"):
                removed_hetatm += 1
                continue
                
            # We ONLY process standard ATOM lines (and TER/END lines to keep formatting)
            if line.startswith("ATOM  "):
                
                # 2. Filter Alternate Conformers
                # Column 17 (index 16) contains the AltLoc identifier (A, B, C...)
                alt_loc = line[16]
                if alt_loc not in [' ', 'A', '1']:
                    removed_alt_locs += 1
                    continue # Throw away 'B', 'C', etc.
                
                # If it's the 'A' conformer, erase the 'A' so downstream software doesn't get confused
                if alt_loc != ' ':
                    line = line[:16] + ' ' + line[17:]

                # 3. Filter Hydrogens
                # The element symbol is in columns 77-78 (index 76:78)
                element = line[76:78].strip().upper()
                atom_name = line[12:16].strip()
                
                is_hydrogen = False
                if element == 'H':
                    is_hydrogen = True
                # Fallback in case the element column is blank (common in older PDBs)
                elif element == '' and (atom_name.startswith('H') or (atom_name[0].isdigit() and atom_name[1] == 'H')):
                    is_hydrogen = True
                    
                if is_hydrogen:
                    removed_hydrogens += 1
                    continue

                # 4. If it survived all filters, write it to the new file!
                f_out.write(line)
                atom_count += 1
                
            # Keep chain terminators and the end of the file
            elif line.startswith("TER") or line.startswith("END"):
                f_out.write(line)

    print("\n=== CLEANUP SUMMARY ===")
    print(f"Removed Ligands/Waters:   {removed_hetatm} atoms")
    print(f"Removed Hydrogens:        {removed_hydrogens} atoms")
    print(f"Removed Alt Conformers:   {removed_alt_locs} atoms")
    print("-" * 25)
    print(f"Final Pristine Atoms:     {atom_count}")
    print(f"\nSuccessfully saved to: {OUTPUT_PDB}")

if __name__ == "__main__":
    clean_pdb()
