import pandas as pd

def standardize_columns(df):
    """
    Normalizes column names, converts money columns to actual numbers, 
    and fixes sign mismatches (Costco vs Chase).
    """
    df.columns = [c.strip().lower() for c in df.columns]

    if 'account' in df.columns:
        df.rename(columns={'account': 'Account'}, inplace=True)

    # Force columns to be numeric where needed
    def clean_money_column(col_name):
        if col_name in df.columns:
            df[col_name] = df[col_name].astype(str).str.replace(r'[$,]', '', regex=True)
            df[col_name] = pd.to_numeric(df[col_name], errors='coerce').fillna(0)

    # Fix Costco (Debit/Credit split)
    if 'debit' in df.columns and 'credit' in df.columns:
        clean_money_column('debit')
        clean_money_column('credit')
        df['amount'] = (df['debit'] + df['credit']) * -1

    # Define Mapping
    column_mapping = {
        'date': ['posting date', 'transaction date', 'date', 'post date'],
        'description': ['description', 'merchant', 'details'], 
        'amount': ['amount'],
        'category': ['category', 'type']
    }

    # Apply Renaming
    for standard_name, variations in column_mapping.items():
        if standard_name not in df.columns:
            for variant in variations:
                if variant in df.columns:
                    df.rename(columns={variant: standard_name}, inplace=True)
                    break
    
    # Remove Duplicate Columns
    df = df.loc[:, ~df.columns.duplicated()]

    # Clean the final 'amount' column
    clean_money_column('amount')

    # Final Filter
    desired_cols = ['date', 'amount', 'description', 'category', 'Account']
    
    for col in desired_cols:
        if col not in df.columns:
            df[col] = None 
            
    return df[desired_cols]