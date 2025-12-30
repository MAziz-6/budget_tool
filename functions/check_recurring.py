def check_recurring(row):
    """
    Determines if a transaction is likely recurring based on Category or Keywords.
    Returns: Boolean (True/False)
    """
    category = row.get('Category_Rule', '')
    description = str(row['description']).upper()
    
    # 1. Inherently Recurring Categories
    # If it falls in these buckets, it is almost certainly a monthly fixed cost
    recurring_categories = [
        'Mortgage/Rent', 
        'Utilities', 
        'Subscriptions/Streaming', 
        'Gym/Health',
        'Loan/Credit Card Payment'
    ]
    
    if category in recurring_categories:
        return True
        
    # 2. Keyword Search
    # "PPD ID" usually indicates Prearranged Payment and Deposit (ACH Autopay)
    recurring_keywords = ['AUTOPAY', 'RECURRING', 'BILL PAY', 'INSURANCE', 'PPD ID']
    
    for keyword in recurring_keywords:
        if keyword in description:
            return True
            
    return False