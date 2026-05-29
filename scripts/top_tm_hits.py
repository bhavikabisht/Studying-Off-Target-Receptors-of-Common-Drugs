import csv
import os

# --- SETTINGS ---
INPUT_CSV = "tm_scores_results.csv"
OUTPUT_TXT = "top_hits.txt"

def extract_top_hits():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: Could not find '{INPUT_CSV}'.")
        return

    hits_count = 0

    with open(INPUT_CSV, mode='r') as infile, open(OUTPUT_TXT, mode='w') as outfile:
        reader = csv.reader(infile)
        
        # Skip the header row
        try:
            next(reader)
        except StopIteration:
            print("The CSV file is empty.")
            return

        for row in reader:
            # Ensure the row actually has our 3 columns (Folder, ID, Score)
            if len(row) >= 3:
                protein_id = row[1]
                score_str = row[2]

                # Try to convert the score to a decimal number
                try:
                    score_val = float(score_str)
                    
                    # The Golden Zone Filter
                    if score_val > 0.50:
                        # Adding .pdb so it perfectly matches your folder structure
                        outfile.write(f"{protein_id}.pdb\n")
                        hits_count += 1
                        
                except ValueError:
                    # If it says "Error" instead of a number, we just ignore it
                    pass

    print(f"Extraction complete!")
    print(f"Filtered down to exactly {hits_count} proteins with a TM-score > 0.50.")
    print(f"Saved your clean shortlist to: {OUTPUT_TXT}")

if __name__ == "__main__":
    extract_top_hits()
