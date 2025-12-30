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
            'DEPOSIT', 'REFUND', 'IRS TREAS', '9424300002'
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
        ('Cash Withdrawal', ['ATM WITHDRAWAL', 'CASH WITHDRAWAL', 'ATM WDL', 'ATM']),
        
        # 3. MAJOR BILLS
        ('Mortgage/Rent', ['JPMORGAN CHASE', 'MORTGAGE', 'RENT', 'HOA', 'QUAIL RIDGE']),
        ('Utilities', ['SD GAS & ELEC', 'COX COMM', 'WATER', 'WASTE', 'SOLAR']),
        ('Subscriptions/Streaming', [
            'NETFLIX', 'HULU', 'SPOTIFY', 'DISNEY', 'HBO', 'YOUTUBE', 
            'PEACOCK', 'AUDIBLE', 'PRIME VIDEO', 'APPLE.COM', 'GOOGLE *', 'AUTOMATIC PAYMENT'
        ]),

        # 4. DISCRETIONARY SPENDING
        ('Groceries', [
            'TRADER JOE', 'COSTCO WHSE', 'SPROUTS', 'RALPHS', 'VONS', 'ALBERTSONS', 
            'WHOLE FOODS', '88 RANCH', 'LAZY ACRES', 'FARMERS MARKET', 'CREAM OF',
            'FRAIZER FARMS', 'NATURAL GROCERS', 'GROCERY OUTLET', 'WORLD MARKET',
            'BABA NATURAL'
        ]),
        ('Amazon', ['AMAZON', 'AMZN']), 
        ('Dining/Restaurants', [
            'RIVIAN CAFE', 'IN-N-OUT', 'CHIPOTLE', 'BURGER', 'PIZZA', 'TACO', 
            'RAMEN', 'SUSHI', 'GRILL', 'CAFE', 'BISTRO', 'DINER', 'PUB', 'BAR',
            'DOORDASH', 'UBER EATS', 'GRUBHUB', 'MCDONALD', 'BAGEL', 'SAPPCLUB.COM',
            'DELI', 'PHO', 'DOUGHNUT', 'DONUTS', 'SAVORY', 'BEER', 'BREWERY', 'WINE',
            'COCKTAIL', 'TAVERN', 'BAO', 'JUICE', 'SMOOTHIE', 'WILDLAND', 'SUSHI',
            'ROBATA', 'POKE', 'JERSEY MIKE', 'SAMS KITCHEN', 'THAI', 'HOMESTATE',
            'HAWAIIAN', 'GREEK', 'MEDITERRANEAN', 'MEXICAN', 'ITALIAN', 'VIETNAMESE',
            'INDIAN', 'CHINESE', 'JAPANESE', 'KOREAN', 'FRENCH', 'NIKO', 'FISH MARKET',
            'PRAGER', 'DAIRY QUEEN', 'MADELINE', 'HENRY', 'RESTAURANT', 'RESTA', 'SUB',
            'WAWA', 'CAND', 'LITTLE MACS', 'BLUE BOWL', 'SUPERFOOD', 'EATERY', 'YAKISOBA',
            'DOUGH', 'HEIGHTS MARKET', 'HAWK', 'BAKE', 'BREWING', 'DOCENT', 'BREWER',
            'CHICKEN', 'FOODZ', 'HONG KONG'
        ]),
        ('Coffee', [
            'COFFEE', 'ROAST', 'CAFE', 'VIGILANTE', 'REVOLUTION', 'STARBUCKS', 'DUNKIN'
        ]),
        ('Shopping/Merchandise', [
            'TARGET', 'WALMART', 'HOMEGOODS', 'MARSHALLS', 'TJ MAXX', 'ROSS', 
            'NORDSTROM', 'UNIQLO', 'IKEA', 'LOWES', 'HOME DEPOT', 'CVS', 
            'RITE AID', 'WALGREENS', 'BEST BUY', 'APPLE STORE', 'ETSY', 'USPS', 'FEDEX',
            'OFFICE DEPOT', 'OFFICE MAX', 'MICRO CENTER', 'GAMESTOP', 'BARNES & NOBLE',
            'PIGMENT', 'COMETEER', 'VIOC',
        ]),
        ('Pet Supplies', ['KAHOOTS', 'CHEWY', 'PETCO', 'PETSMART', 'VET']),
        ('Automotive/Gas', [
            'EXPRESS FUEL', 'SHELL', 'CHEVRON', 'MOBIL', '76', 'ARCO', 'COSTCO GAS',
            'CAR WASH', 'SMOG', 'DMV', 'PARKING', 'FASTTRAK', 'TOYOTA', 'TESLA', 'NYX',
        ]),
        ('Gym/Health', ['ACTIVE N FIT', 'YMCA', '24 HOUR FITNESS', 'PLANET FITNESS', 'MACROFACTOR']),
        ('Personal Care', ['SALON', 'BARBER', 'SPA', 'HAIR', 'NAILS', 'COSMETICS', 'SEPHORA', 'ULTA', 'THRIVECAUSEMETICS']),
        ('Entertainment', ['STUBHUB', 'TICKETMASTER', 'CINEMA', 'THEATER', 'MUSEUM', 'AQUARIUM', 'STEAM', 'PLAYSTATION', 'NINTENDO']),
        ('Home Improvement', [
            'ACE HARDWARE', 'GARDENING', 'LANDSCAPING', 'FURNITURE', 'APPLIANCE', 'LOWE\'S', 'HOME DEPOT',
            'KEIL ELECTRIC', 'PLUMBING', 'PLANT', 'FLOWER', 'NURSERY', 'WAYFAIR.COM',
        ]),
        ('7-Eleven/Convenience Store', ['7-ELEVEN', '7ELEVEN', 'CONVENIENCE STORE', 'CIRCLE K']),
    ]

    # Apply Rules
    for category, keywords in rules:
        for keyword in keywords:
            # Check if keyword matches description
            if keyword in description:
                return category

    return 'Uncategorized'