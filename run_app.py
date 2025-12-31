import os
import sys
import webbrowser
from threading import Timer
import streamlit.web.cli as stcli
from functions.build_df import build_current_budget_df

def resolve_path(path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, path)

if __name__ == "__main__":
    exe_dir = os.getcwd() 
    output_file = os.path.join(exe_dir, 'master_budget.csv')
    
    print("------------------------------------------------")
    print("      💸 bud.get | Personal Finance Tool        ")
    print("------------------------------------------------")

    try:
        print("1. Scanning for data...")
        df = build_current_budget_df(exe_dir)
        if not df.empty:
            df.to_csv(output_file, index=False)
            print(f"   Success! Saved {len(df)} transactions.")
        else:
            print("   ⚠️  No data found.")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n2. Launching Dashboard...")
    
    # --- THE FIX: Force Open Browser ---
    def open_browser():
        webbrowser.open_new("http://localhost:8501")
    
    # Wait 1.5 seconds for the server to start, then open
    Timer(1.5, open_browser).start()

    dashboard_path = resolve_path(os.path.join('dashboard', 'dashboard.py'))

    sys.argv = [
        "streamlit",
        "run",
        dashboard_path,
        "--global.developmentMode=false",
        "--server.headless=true", # We keep this true so we can control the open with the Timer above
    ]
    
    sys.exit(stcli.main())