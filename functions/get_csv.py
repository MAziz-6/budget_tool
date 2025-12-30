import os
import pandas as pd
import glob

def build_current_budget_df(directory) -> pd.DataFrame:
    """
    Scans the directory for account folders. In each folder, finds the 
    most recent .csv, loads it, tags it, and merges all into one DataFrame.
    """
    all_dataframes = []
    abs_root = os.path.abspath(directory)

    
    if not os.path.exists(abs_root):
        raise FileNotFoundError(f"The directory {abs_root} does not exist.")
    
    print(f"Scanning directory: {abs_root}\n")

    with os.scandir(abs_root) as entries:
        for entry in entries:
            if entry.is_dir():
                account_name = entry.name
                folder_path = entry.path
                
                # Look for CSV files in this folder
                csv_pattern = os.path.join(folder_path, '*.csv')
                csv_files = glob.glob(csv_pattern)
                
                if csv_files:
                    newest_file = max(csv_files, key=os.path.getctime)
                    print(f"[{account_name}] Found: {os.path.basename(newest_file)}")
                    
                    try:
                        df = pd.read_csv(newest_file)
                        df['Account'] = account_name
                        all_dataframes.append(df)
                    except Exception as e:
                        print(f"  Error reading {newest_file}: {e}")
                else:
                    print(f"[{account_name}] No CSV files found.")

    if all_dataframes:
        master_df = pd.concat(all_dataframes, ignore_index=True)
        return master_df
    else:
        print("No data found in any subdirectory.")
        return pd.DataFrame()  # Always returns a DataFrame (even if empty)