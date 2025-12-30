import pandas as pd

def standardize_columns(df):
    """
    Renames columns in the dataframe based on a known mapping.
    Converts all column names to lowercase first to make matching easier.
    """
    # 1. Normalize existing columns to lowercase/strip whitespace
    # This ensures ' Amount ' matches 'amount'
    df.columns = [c.strip().lower() for c in df.columns]

    # 2. Define your "Translation Map"
    # Key = Standard Name you want
    # Value = List of possible names found in your CSVs
    column_mapping = {
        'date': ['order date', 'posting date', 'transaction date', 'post date'],
        'amount': ['debit', 'price', 'total', 'cost', 'payment amount'],
        'description': ['payee', 'merchant', 'item description', 'details'],
        'category': ['budget category', 'type']
    }

    # 3. Apply the renaming
    for standard_name, variations in column_mapping.items():
        for variant in variations:
            if variant in df.columns:
                # Rename the variant to the standard name
                df.rename(columns={variant: standard_name}, inplace=True)
                # Once we find a match for this standard name, we can stop checking variations
                # (Assuming only one variation exists per file)
                break
                
    # 4. (Optional) Filter to keep ONLY the standard columns + Account
    # This drops extra noise like "Transaction ID" or "City" that you might not need.
    keep_cols = ['date', 'amount', 'description', 'category', 'Account']
    
    # Filter for columns that actually exist in this DF
    existing_cols = [c for c in keep_cols if c in df.columns]
    return df[existing_cols]