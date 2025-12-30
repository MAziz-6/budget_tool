from functions.build_df import build_current_budget_df

def main():
    directory = r'/home/maziz/budget_tool/data' 
    output_path = r'/mnt/c/Users/matta/Downloads/master_budget.csv'
    
    try:
        budget_df = build_current_budget_df(directory)
        
        if not budget_df.empty:
            print(f"Success! Combined {len(budget_df)} rows.")
            print(budget_df.head())
            
            # Optional: Save to a master CSV to verify
            budget_df.to_csv('master_budget.csv', index=False)
            budget_df.to_csv(output_path, index=False)
            print(f"Master budget saved to {output_path}")
        else:
            print("No data found.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()