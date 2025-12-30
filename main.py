# main.py
from functions.get_csv import build_current_budget_df
from functions.standardize_columns import standardize_columns

def main():
    # Use r'' for Windows paths to ensure backslashes are read correctly
    directory = r'/home/maziz/budget_tool/data' 
    
    try:
        budget_df = build_current_budget_df(directory)
        
        if not budget_df.empty:
            print(f"Success! Combined {len(budget_df)} rows.")
            print(budget_df.head())
            
            # Optional: Save to a master CSV to verify
            # budget_df.to_csv('master_budget.csv', index=False)
        else:
            print("No data found.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()