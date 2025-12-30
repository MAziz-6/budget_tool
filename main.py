import os
import sys
import subprocess

from functions.build_df import build_current_budget_df

def main():
    # when ready change to the line below to have this run in the current directory
    # directory = '.'

    directory = r'/home/maziz/budget_tool/data' 
    output_path = r'/mnt/c/Users/matta/Downloads/master_budget.csv'
    
    dashboard_path = os.path.join('dashboard', 'dashboard.py')
    
    try:
        budget_df = build_current_budget_df(directory)
        
        if not budget_df.empty:
            print(f"Success! Combined {len(budget_df)} rows.")
            
            # local save for testing
            budget_df.to_csv('master_budget.csv', index=False)
            budget_df.to_csv(output_path, index=False)
            print(f"Master budget saved to {output_path}")

            # dashboard time! 
            if os.path.exists(dashboard_path):
                # CHECK: Are we running in WSL?
                # 'WSL_DISTRO_NAME' is an environment variable that only exists in WSL
                is_wsl = 'WSL_DISTRO_NAME' in os.environ
                
                # If WSL, use 0.0.0.0 (bridge to Windows)
                # If Windows, use localhost (avoid Firewall popup)
                server_address = "0.0.0.0" if is_wsl else "localhost"
                
                print("Dashboard is starting...")
                print(f"👉 GO TO THIS URL: http://localhost:8501")
                
                subprocess.run([
                    sys.executable, "-m", "streamlit", "run", dashboard_path,
                    f"--server.address={server_address}",
                    "--server.headless=true"
                ])
            else:
                print(f"Error: Could not find dashboard file at {dashboard_path}")

        else:
            print("No data found.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()