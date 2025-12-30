import re
import pandas as pd

def get_category(row):
    """
    Applies regex rules to categorize a transaction based on its description.
    Priority is top-to-bottom (just like an IFS formula).
    """
    description = str(row['description']).upper() # specific formatting
    amount = row['amount'] if pd.notnull(row['amount']) else 0
    
    # --- RULE SET ---
    # format: (Category Name, [List of Keywords])
    rules = [
        # 1. INCOME & DEPOSITS (Check strictly for Credit/Payroll first)
        ('Income/Payroll', [
            'RIVIAN AUTOMOTIV PAYROLL', 'CAREFUSION', 'DIRECT DEP', 'RESILIENT', 
            'DEPOSIT', 'REFUND', 'IRS TREAS'
        ]),
        
        # 2. TRANSFERS & PAYMENTS (Money moving around, not spending)
        ('Loan/Credit Card Payment', [
            'CHASE CREDIT CRD', 'CITI CARD ONLINE', 'PAYMENT TO CHASE', 'AUTOPAY',
            'EARNEST', 'NORTHWESTERN MU', 'ADVS ED SERV', 'MERCURY INS', 
            'AUTO LOAN', 'STUDNTLOAN', 'BARCLAYCARD'
        ]),
        ('Transfer to Savings', ['TRANSFER TO SAV']),
        ('Transfers/P2P', [
            'ONLINE TRANSFER', 'ZELLE', 'VENMO', 'PAYPAL', 'WIRE TRANSFER', 
            'ACCT_XFER', 'QUICKPAY'
        ]),
        
        # 3. MAJOR BILLS
        ('Mortgage/Rent', ['JPMORGAN CHASE', 'MORTGAGE', 'RENT', 'HOA', 'QUAIL RIDGE']),
        ('Utilities', ['SD GAS & ELEC', 'COX COMM', 'WATER', 'WASTE', 'SOLAR']),
        ('Subscriptions/Streaming', [
            'NETFLIX', 'HULU', 'SPOTIFY', 'DISNEY', 'HBO', 'YOUTUBE', 
            'PEACOCK', 'AUDIBLE', 'PRIME VIDEO', 'APPLE.COM', 'GOOGLE *'
        ]),

        # 4. DISCRETIONARY SPENDING
        ('Groceries', [
            'TRADER JOE', 'COSTCO WHSE', 'SPROUTS', 'RALPHS', 'VONS', 'ALBERTSONS', 
            'WHOLE FOODS', '88 RANCH', 'LAZY ACRES', 'FARMERS MARKET'
        ]),
        ('Amazon', ['AMAZON', 'AMZN']), # Keep this separate as requested
        ('Dining/Restaurants', [
            'RIVIAN CAFE', 'IN-N-OUT', 'CHIPOTLE', 'BURGER', 'PIZZA', 'TACO', 
            'RAMEN', 'SUSHI', 'GRILL', 'CAFE', 'BISTRO', 'DINER', 'PUB', 'BAR',
            'DOORDASH', 'UBER EATS', 'GRUBHUB', 'MCDONALD', 'STARBUCKS', 'COFFEE',
            'DUNKIN', 'REVOLUTION ROASTERS', 'VIGILANTE COFFEE', 'BAGEL'
        ]),
        ('Shopping/Merchandise', [
            'TARGET', 'WALMART', 'HOMEGOODS', 'MARSHALLS', 'TJ MAXX', 'ROSS', 
            'NORDSTROM', 'UNIQLO', 'IKEA', 'LOWES', 'HOME DEPOT', 'CVS', 
            'RITE AID', 'WALGREENS', 'BEST BUY', 'APPLE STORE', 'ETSY'
        ]),
        ('Pet Supplies', ['KAHOOTS', 'CHEWY', 'PETCO', 'PETSMART', 'VET']),
        ('Automotive/Gas', [
            'EXPRESS FUEL', 'SHELL', 'CHEVRON', 'MOBIL', '76', 'ARCO', 'COSTCO GAS',
            'CAR WASH', 'SMOG', 'DMV', 'PARKING', 'FASTTRAK', 'TOYOTA', 'TESLA'
        ]),
        ('Gym/Health', ['ACTIVE N FIT', 'YMCA', '24 HOUR FITNESS', 'PLANET FITNESS', 'MACROFACTOR']),
        ('Personal Care', ['SALON', 'BARBER', 'SPA', 'HAIR', 'NAILS', 'COSMETICS', 'SEPHORA', 'ULTA']),
        ('Entertainment', ['STUBHUB', 'TICKETMASTER', 'CINEMA', 'THEATER', 'MUSEUM', 'AQUARIUM', 'STEAM', 'PLAYSTATION', 'NINTENDO'])
    ]

    # --- LOGIC LOOP ---
    for category, keywords in rules:
        for keyword in keywords:
            # Check if keyword matches description
            if keyword in description:
                return category
            
    # Fallback: If amount is positive and heavily implies income (optional)
    # if amount > 1000 and 'Income' not in str(rules): 
    #     # You can add logic here if you want to catch uncategorized deposits
    #     pass

    return 'Uncategorized'