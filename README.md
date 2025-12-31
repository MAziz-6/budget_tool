# 💸 bud.get

A private, automated personal finance dashboard running locally on Python. 
It ingests raw CSV exports from banks (Chase, Costco, Amazon), cleans and categorizes the data, and visualizes spending habits in an interactive Streamlit dashboard.

---

## 🚀 Features

* **Privacy First:** Runs 100% locally. No data is ever sent to the cloud.
* **Automated ETL Pipeline:** Instantly standardizes jagged CSVs, fixes negative/positive sign mismatches (e.g., Costco vs. Chase), and cleans currency formatting.
* **Smart Categorization:** Uses regex rules to auto-tag transactions (Groceries, Utilities, Recurring, etc.).
* **Interactive Dashboard:**
    * **Overview:** Net savings, savings rate, and category breakdowns.
    * **Account Deep Dive:** Analyze spending by specific folder/source.
    * **Savings Detective:** Auto-detects recurring subscriptions and the "Latte Factor" (dining/coffee spend).
    * **Exports:** Generates "Actual Budget" compatible import files (split by account) or raw CSV backups.

---

## 📂 Project Structure

```text
/Budget_Project
│
├── main.py                  # The Launcher: Runs the build process -> launches dashboard
├── master_budget.csv        # The Database: Generated automatically by main.py
│
├── functions/
│   └── build_df.py          # The Logic: Cleaning, categorizing, and compiling CSVs
│
├── dashboard/
│   └── dashboard.py         # The UI: Streamlit visualization code
│
└── data_folders/            # (User Created) Place your bank CSVs here
    ├── amazon/
    ├── bills/
    ├── costco/
    └── fun/
```


## 🛠️ Setup & Installation

This project is optimized for **WSL (Windows Subsystem for Linux)** using `uv` for package management.

### 1. Prerequisites
* Python 3.10+
* `uv` (Modern Python package manager)

### 2. Installation
```bash
# Clone or navigate to the project directory
cd /mnt/c/Budget_Project

# Create virtual environment
uv venv

# Activate environment
source .venv/bin/activate

# Install dependencies
uv pip install pandas streamlit plotly
```
## 🏃‍♂️ How to Run

1.  **Drop your files:** Place your latest bank CSV exports into the corresponding folders (e.g., `costco/`, `bills/`).
2.  **Run the launcher:**
    ```bash
    # Ensure your environment is active
    source .venv/bin/activate
    
    # Run the main script
    python main.py
    ```
3.  **View the Dashboard:**
    * The script will process the data and automatically launch the server.
    * Open your browser (in Windows) and go to: **`http://localhost:8501`**

## 📦 Building a Standalone Executable (.exe)

You can compile this project into a single `.exe` file that runs on Windows without needing Python installed.

### 1. Requirements
You must perform the build step **in Windows (PowerShell/CMD)**, not WSL.
```powershell
pip install pandas streamlit plotly pyinstaller
```
### 2. The Build Command
Run this command in the project root. It bundles Streamlit, your code, and the dashboard into one file.
```PowerShell
pyinstaller --noconfirm --onefile --console --name "bud.get" --clean `
    --icon "app_icon.ico" `
    --collect-all streamlit `
    --add-data "dashboard/dashboard.py;dashboard" `
    --hidden-import "pandas" `
    --hidden-import "plotly" `
    run_app.pyy
```
- `--console`: Hides the black terminal window.
- `--icon`: uses app_icon.ico` for the appplication icon (looks nice!).
- `run_app.py`: Special entry point script that handles the interal Streamlit server launch.

## ⚙️ Configuration

### Adjusting Categories
To change how transactions are labeled, edit the `rules` list in **`functions/build_df.py`**:
```python
rules = [
    ('Groceries', ['TRADER JOE', 'WHOLE FOODS', 'RALPHS']),
    ('Tech', ['OPENAI', 'GITHUB', 'CLAUDE']),
    # Add your own rules here...
]
```
### Debugging Invisible Data

If you see transactions in your CSV but not in the "Deep Dive" tab, it is usually because of a date mismatch or positive/negative sign issue.

1.  Scroll to the bottom of the **Account Deep Dive** tab.
2.  Expand **"🛠️ Developer Tools / Debugger"**.
3.  This panel will tell you exactly how many rows are being filtered out by the date slider vs. category filters.

## 📤 Exporting Data

Go to the **"Exports"** tab in the dashboard to download:
1.  **Actual Budget Zip:** A ZIP file containing separate CSVs for each account, formatted specifically for import into [Actual Budget](https://actualbudget.com/).
2.  **Master Backup:** A single CSV of your entire financial history.

## 📝 Notes
* **Recurring Detection:** The tool flags transactions as "Recurring" if they match specific categories (Utilities, Streaming) or contain keywords like "AUTOPAY" or "PPD ID".
* **Double Counting:** The dashboard automatically excludes "Transfers" and "Credit Card Payments" to prevent inflating your spending numbers.