import csv
import os

# --- SETTINGS ---
# Change these filenames to match your actual files
ID_LIST_FILE = "top_hits.txt"  # Your text file with the 252 IDs
INPUT_CSV = "tm_scores_results.csv"   # Your main CSV file with the scores
OUTPUT_CSV = "sorted_top_hits.csv" # The final sorted output file

def sort_and_filter_csv():
    # 1. Read the 252 IDs into a set for lightning-fast lookup
    if not os.path.exists(ID_LIST_FILE):
        print(f"Error: Could not find '{ID_LIST_FILE}'. Please check the filename.")
        return
        
    valid_ids = set()
    with open(ID_LIST_FILE, 'r') as f:
        for line in f:
            # Cleans up the ID just in case it has .pdb attached
            clean_id = line.strip().replace(".pdb", "")
            if clean_id:
                valid_ids.add(clean_id)
                
    print(f"Loaded {len(valid_ids)} target IDs from your list.")

    # 2. Read the CSV and extract the matching rows
    if not os.path.exists(INPUT_CSV):
        print(f"Error: Could not find '{INPUT_CSV}'. Please check the filename.")
        return

    filtered_rows = []
    header = []
    
    with open(INPUT_CSV, 'r') as f:
        reader = csv.reader(f)
        try:
            header = next(reader) # Grab the header row
        except StopIteration:
            print("The CSV file is empty!")
            return
            
        # Dynamically find which column has the ID and the TM-score
        id_col_index = 1 
        score_col_index = 2
        
        for i, col_name in enumerate(header):
            col_upper = col_name.upper()
            if "ID" in col_upper or "TARGET" in col_upper:
                id_col_index = i
            elif "SCORE" in col_upper or "TMSPLIT" in col_upper or "ALNTMSCORE" in col_upper:
                score_col_index = i

        # Scan the CSV
        for row in reader:
            if len(row) > score_col_index:
                row_id = row[id_col_index].replace(".pdb", "")
                
                # If this row's ID is one of your 252 targets...
                if row_id in valid_ids:
                    try:
                        # Convert score to a decimal so Python can sort it mathematically
                        score = float(row[score_col_index])
                        filtered_rows.append((score, row))
                    except ValueError:
                        pass # Ignore any rows that say "Error" instead of a number

    # 3. Sort the filtered rows from highest TM-score to lowest
    filtered_rows.sort(key=lambda x: x[0], reverse=True)

    # 4. Write out the final, perfectly sorted CSV
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for score, row in filtered_rows:
            writer.writerow(row)

    print(f"\nSuccess! Filtered and sorted {len(filtered_rows)} rows.")
    print(f"Your clean dataset is saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    sort_and_filter_csv()
