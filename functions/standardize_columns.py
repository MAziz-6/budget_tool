def standardize_columns(df):
    """
    Normalizes column names and fixes sign mismatches.
    """
    # 1. Normalize headers
    df.columns = [c.strip().lower() for c in df.columns]

    # 2. Fix Costco (Debit/Credit split)
    if 'debit' in df.columns and 'credit' in df.columns:
        df['debit'] = df['debit'].fillna(0)
        df['credit'] = df['credit'].fillna(0)
        df['amount'] = (df['debit'] + df['credit']) * -1

    # 3. Define Mapping
    # FIX: Removed 'details' from description mapping to avoid collision with Chase 'Details' column
    column_mapping = {
        'date': ['posting date', 'transaction date', 'date', 'post date'],
        'description': ['description', 'merchant'], # 'details' removed
        'amount': ['amount'],
        'category': ['category', 'type']
    }

    # 4. Apply Renaming
    for standard_name, variations in column_mapping.items():
        # Only rename if we don't already have the standard column
        if standard_name not in df.columns:
            for variant in variations:
                if variant in df.columns:
                    df.rename(columns={variant: standard_name}, inplace=True)
                    break
    
    # 5. SAFETY: Drop duplicate columns if any were created
    # This specifically fixes "Reindexing only valid with uniquely valued Index objects"
    df = df.loc[:, ~df.columns.duplicated()]

    # 6. Final Filter
    desired_cols = ['date', 'amount', 'description', 'category', 'Account']
    
    # Fill missing columns with None
    for col in desired_cols:
        if col not in df.columns:
            df[col] = None 
            
    return df[desired_cols]