import pandas as pd

def check_recurring(row):
    """
    Determines if a transaction is likely recurring.
    """
    cat_rule = str(row.get('Category_Rule', ''))
    cat_orig = str(row.get('category', ''))
    
    # We look at both. If either matches a recurring category, we count it.
    current_category = cat_rule if cat_rule != 'nan' and cat_rule != '' else cat_orig
    
    description = str(row['description']).upper()
    
    # 1. Inherently Recurring Categories
    recurring_categories = [
        'Mortgage/Rent', 
        'Utilities', 
        'Subscriptions/Streaming', 
        'Gym/Health',
        'Loan/Credit Card Payment'
    ]
    
    if current_category in recurring_categories:
        return True
        
    # 2. Keyword Search
    recurring_keywords = ['AUTOPAY', 'RECURRING', 'BILL PAY', 'INSURANCE', 'PPD ID']
    
    for keyword in recurring_keywords:
        if keyword in description:
            return True
            
    return False