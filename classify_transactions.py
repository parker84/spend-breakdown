import pandas as pd
from pathlib import Path
import re

# Define paths
PROCESSED_DATA_DIR = Path("data/processed")

# Category definitions for credit card (case-insensitive matching)
CREDIT_CARD_CATEGORIES = {
    "groceries": [
        "METRO", "FARM BOY", "SUMMERHILL MARKET", "HEALTHY PLANET", 
        "SHOPPERS DRUG MART", "CANADIAN TIRE", "STONES DRUG STORE"
    ],
    "beer_liquor": [
        "CREEMORE SPRINGS", "LCBO", "BEER STORE", "SPIRIT OF YORK",
        "OLD FLAME BREWING", "INDIE ALEHOUSE", "PONDVIEW ESTATE",
        "MARYNISSEN", "BEERTOWN", "SAMARA BREWING", "MUDTOWN STATION",
        "WINIFREDS ENGLISH PUB", "BOTTEGA VOLO"
    ],
    "coffee": [
        "SUBTEXT COFFEE", "BALZAC", "TIM HORTONS", "PILOT COFFEE",
        "SAM JAMES COFFEE", "CABIN COFFEE", "AMICIS COFFEE", "CAFE AROMA",
        "FIRST SIP MATCHA", "FLYING KITE", "FROG PONDS CAFE", "CAFE LANDWER",
        "NEON COMMISSARY"
    ],
    "transportation": [
        "PRESTO", "VIA RAIL", "BIXI", "ALAMO CANADA", "TORONTO PARKING",
        "UBER CANADA/UBERTRIP", "UBER* TRIP", "UBER *TRIP"
    ],
    "subscriptions": [
        "RENDER.COM", "GOOGLE", "APPLE.COM/BILL", "NOTION LABS",
        "OPENAI", "Amazon Web Services", "SHOPIFY", "1PASSWORD",
        "GODADDY", "MEDIUM CORPORATION", "ABC*5028-ANYTIME FITNESS",
        "BALANCE PROTECTION"
    ],
    "eating_out": [
        "CHICAS CHICKEN", "PITA PIT", "BANK CAFE", "NODO RESTAURANT",
        "CHUCKS ROADHOUSE", "SUBWAY", "A&W RESTAURANT", "LYNWOOD INN",
        "FIVE FISHERMEN", "THE FREIGHT SHED", "CENTRAL TAPS",
        "THONSON CATERING", "BROAD NOSH BAGELS", "LEVAIN", "STACKED PANCAKE",
        "LA DIPERIE", "BIG CHILL ICE-CREAM", "CRAIG'S COOKIES", "AMADEUS PATISSERIE",
        "DISTILLERY RESTAURANTS", "FRIENDLY SOCIETY", "OLIVE ET GOURMANDO",
        "GASPAR PINCETTE", "MARRY ME MOCHI", "COWS CABLE", "FULL STOP",
        "ROD, GUN &BARBERS", "SOMA CHOCOLATE"
    ],
    "entertainment": [
        "CARL LAIDLAW ORCHARDS", "HAMILTON SPORTS GROUP", "FANFARE BOOKS",
        "CAPE BRETON HIGHLANDS", "LIBRAIRIE BERTRAND", "BLUEJAYS5050",
        "TIM HORTONS FIELD", "TMCANADA", "MARINE HERITAGE", "BRADSHAWS"
    ],
    "utilities": [
        "BELL MOBILITY", "TORONTO RSD"
    ],
    "goods_gifts": [
        "PROVINCE OF CAN", "DU/ER", "ARITZIA", "ROOTS", "AMZN", "Amazon.ca",
        "PEACE COLLECTIVE", "MEJURI", "THELATESTSCOOP", "MAJEWELRY",
        "KINDRED FOLK", "BIZJAK FARMS", "WYCHWOOD BARNS", "ROGERS' RANCH",
        "HOUSE OF GOOD", "NOMA GALLERY", "GREAVES JAMS", "LADY LOU",
        "GROHMANN KNIVES", "LAURASECORD", "ARTISANS CANADA", "CANADIAN PROTEIN",
        "SEASON'S HOME DECOR", "A NATURAL HOME", "COMMUNITY", "VISTAPRINT"
    ],
    "ordering_in": [
        "UBEREATS", "UBER* EATS", "UBER CANADA/UBEREATS", "DOORDASH", "UBER CANADA/UBERCASH"
    ],
    "donations": [
        "CANADAHELPS", "DAILY BREAD", "SICKKIDS", "CRC_DON", "GOFNDME",
        "LEGION POPPY", "SAL ARMY", "WIKIMEDIA", "AHOHP VET"
    ]
}

# Category definitions for Amex credit card
AMEX_CATEGORIES = {
    "pet": [
        "PETSMART", "PET VALU", "SNIFFANY", "ANIMAL HOSPITAL", "GLOBAL PET",
        "ROVER.COM", "WAG!", "PETBARN", "PET SUPPLIES PLUS", "PETCO",
        "P U P P T O W N", "PUPPTOWN", "WOOFS & WAGS", "AHOHP VET",
        "MOLLYWAGZ", "PASADENAHUMANE", "ASKAVETONLINE"
    ],
    "groceries": [
        "METRO", "WHOLEFDS", "WHOLE FOODS", "FARM BOY", "LOBLAWS", "SOBEYS",
        "CVS/PHARMACY", "SHOPPERS DRUG MART", "REXALL", "LONGOS", "PUSATERI",
        "MCEWAN", "SUMMERHILL MARKET", "FIESTA FARMS", "HEALTHY PLANET",
        "VICTORIA FARMERS", "CO-OP", "HELLOFRESH", "GOODFOOD", "CHEF'S PLATE",
        "OAKRIDGES FINEST", "NATURE'S EMPORIUM", "BULK BARN", "T&T",
        "THE SWEET POTATO", "EREWHON", "PAVILIONS", "TRADER JOE",
        "RALPHS", "FRESHCO", "KENNEDY'S LAKESIDE"
    ],
    "beer_liquor": [
        "FLYING MONKEYS", "LCBO", "BEER STORE", "WINE RACK", "CREEMORE",
        "MILL STREET", "STEAM WHISTLE", "BELLWOODS BREWERY", "BEERTOWN",
        "HENDERSON BREWING", "BLOOD BROTHERS", "LEFT FIELD BREWERY",
        "AMSTERDAM BREWERY", "GODSPEED BREWERY", "HALO BREWERY",
        "NICKEL 9 DISTILLERY", "SPIRIT OF YORK", "DISTILLERY"
    ],
    "coffee": [
        "BLUE BOTTLE COFFEE", "STARBUCKS", "TIM HORTONS", "BALZAC",
        "CAFE AROMA", "SUBTEXT COFFEE", "GROUND CENTRAL", "CAFE LANDWER",
        "PILOT COFFEE", "SAM JAMES", "DARK HORSE", "ROOSTER COFFEE",
        "JIMMY'S COFFEE", "MERCHANTS OF GREEN", "NEO COFFEE",
        "HOLLIES COFFEE", "WEEKENDERS COFFEE", "CHOPCOFFEE",
        "PROPELLER COFFEE", "URTH CAFFE", "ROOMS COFFEE", "STREAMER COFFEE"
    ],
    "eating_out": [
        "HOLE IN THE WALL", "KINTON RAMEN", "THE OXLEY", "AZUCAR",
        "BOOZEHOUNDS", "AHBA", "GREAT WHITE", "TB REST", "SOMA CHOCOLATE",
        "BYBLOS", "LABORA", "GUSTO", "MONTECITO", "CAFE BOULUD",
        "CANOE", "PAI", "MOMOFUKU", "MIKU", "ARDO", "PIANO PIANO",
        "PLANTA", "JOSO", "HARBOUR 60", "BUCA", "CACTUS CLUB",
        "EARLS", "JOEYS", "MILESTONES", "KELSEYS", "MOXIES",
        "PICKLE BARREL", "JACK ASTOR", "KELSEY", "LONE STAR",
        "EAST SIDE MARIO", "BOSTON PIZZA", "SWISS CHALET",
        "WENDYS", "MCDONALDS", "BURGER KING", "HARVEYS", "POPEYES",
        "CHIPOTLE", "FRESHII", "PANERA", "NANDOS", "REDS MIDTOWN",
        "CIBO", "TERRONI", "FIGO", "PIZZERIA LIBRETTO", "PIZZAIOLO",
        "JERSEY MIKE", "SUBWAY", "TST*", "THE SMITH", "CRAIG'S COOKIES",
        "CHICK-FIL-A", "FIVE GUYS", "SHAKE SHACK", "IN-N-OUT",
        "SWEETGREEN", "CAVA", "HALAL GUYS", "RAMEN", "SUSHI",
        "TACOS", "BURRITO", "POKE", "SALAD", "DELI", "BAKERY",
        "BISTRO", "GRILL", "PUB", "TAVERN",
        "RESTAURANT", "KITCHEN", "EATERY", "DINER", "TRATTORIA",
        "OSTERIA", "IZAKAYA", "CANTINA", "TAQUERIA",
        "NOOK AND CRANNY", "FIONN MACCOOL", "THE BG", "ANNETTE FOOD MARKET",
        "CHIANG MAI", "OLIVE ET GOURMANDO", "BEER HALL", "HENRYS BURGER",
        "SEVEN ELEVEN", "CARL'S JR", "SOCAL VIBES", "HANARE",
        "STATE & MAIN", "RUMBLE CRUMBLE", "PLAYACABANA",
        "BUDAPEST BAKESHOP", "CHOCOSOL", "MENCHIES", "BASKIN ROBBINS",
        "DAIRY QUEEN", "MARBLE SLAB", "SWEET JESUS", "BANG BANG",
        "LA CARNITA", "WILBUR MEXICANA", "GUAC MEXI", "BURRITO BOYZ",
        "FRESHSLICE", "PIZZA NOVA", "PIZZAVILLE", "DOMINOS", "PAPA JOHNS",
        "SHOELESS JOE", "MARRY ME MOCHI", "SOMETHING BEAUTIFUL CAK",
        "MR. PUFFS", "TST-OLD SCHOOL", "THE HEARTH", "LEAFF WAFFLES",
        "GORDON RAMSAY", "BUTTER BAY", "U AND I ", "LS TOMMY CAFE",
        "CHATIME", "UDON IROHA", "ARASHIYAMA OMOKAGE", "WAFLA KYOTO",
        "MANY ROADS PURVEYORS", "ALBION GARDEN", "SHREE MAHANT"
    ],
    "goods_gifts": [
        "BEST BUY", "APPLE STORE", "AMAZON", "INDIGO", "CHAPTERS",
        "WINNERS", "HOMESENSE", "MARSHALLS", "COSTCO", "WALMART",
        "IKEA", "CB2", "CRATE AND BARREL", "WEST ELM", "POTTERY BARN",
        "SEPHORA", "HUDSON BAY", "NORDSTROM", "HOLT RENFREW",
        "UNIQLO", "ZARA", "H&M", "GAP", "BANANA REPUBLIC", "LULULEMON",
        "NIKE", "ADIDAS", "FOOT LOCKER", "SPORT CHEK", "ROOTS",
        "ARITZIA", "CLUB MONACO", "J CREW", "FRANK AND OAK",
        "PUZZLENERDS", "MAISONETTE", "TOKYUPLAZA", "HOME DEPOT",
        "DISNEY STORE", "LUSH", "KUROCHIKU", "SHIBUYA TSUTAYA", "KACTO",
        "OLD NAVY", "VISTAPRINT", "ONEQUINCE", "QUINCE", "RUDSAK",
        "SIMONS", "SAIL", "MEC", "RUNNING ROOM", "DECATHLON",
        "DOLLARAMA", "CANADIAN TIRE", "RONA", "LOWES", "STAPLES",
        "MUJI", "MINISO", "DAISO", "HALLMARK", "PAPYRUS",
        "MICHAELS", "JOANN", "HOBBY LOBBY", "AMERICAN EAGLE", "ABERCROMBIE",
        "URBAN OUTFITTERS", "ANTHROPOLOGIE", "FREE PEOPLE",
        "OLDNAVY.COM", "WWW.SPORTCHEK", "SEA HOUSE", "ETSY", 
        "SHE SELLS SANCTUARY", "LA VIE EN ROSE",
        "ARDENE", "DYNAMITE", "GARAGE", "REITMANS", "MADEWELL",
        "WALKING ON A CLOUD", "ANTHRO CA", "URBANOUTFITTERSCA",
        "WWW.MARKS.COM", "CARIBOU GIFTS", "NIKO AND TOKYO",
        "MARUI STORES", "TARGET", "ITX CANADA"
    ],
    "transportation": [
        "UBER", "LYFT", "PRESTO", "TTC", "GO TRANSIT", "VIA RAIL",
        "PARKING", "ESSO", "SHELL", "PETRO", "PIONEER", "CANADIAN TIRE GAS",
        "CURB SERVICE", "TAXI", "CAB", "SILVER DART", "IRVING", "CIRCLE K",
        "KOPIKALYAN", "JRPLUS", "JR PLUS", "TRAIN"
    ],
    "travel": [
        "HANEDA AIRPORT", "AIRPORT", "DEL MARCOS HOTEL", "HOTEL", "MOTEL",
        "AIRBNB", "HOSTEL", "INN", "RESORT",
        # Japan shops
        "KYOTO ENGINE", "WA FUJITATE", "YASUDASENKEIDO",
        # Disneyland & US travel
        "DLR ", "DISNEYLAND", "DISNEY CALIFORNIA", "COOKIE DOUGH LIGHTFUL",
        "TONGA HUT", "OUT WEST TRADING", "LITTLE LUNCH COFFEE",
        "EXPEDIA", "S AND R MEDALLION",
        "GO APP RIDE", "LS TRAVEL RETAIL", "PORTER AIRLINES",
        "SUICA", "CNP POINT THE WAY", "MOBILE ICOCA", "JRC SMART EX",
        "WDW TICKETS", "WDW CONNECTIONS", "ALIPAY", "FUELROD",
        "MAISONCO"
    ],
    "entertainment": [
        "CINEPLEX", "SCOTIABANK THEATRE", "TIFF", "TICKETMASTER",
        "STUBHUB", "VIVID SEATS", "SEATGEEK", "MUSEUM", "GALLERY",
        "AQUARIUM", "ZOO", "CN TOWER", "RIPLEYS", "COSMOPOL", "SUPERFRICO",
        "NIAGARA-ON-THE-LAKE", "NIAGARA ON THE", "WONDERLAND", "MARINELAND",
        "ESCAPE ROOM", "AXE THROWING", "BOWLING", "GOLF",
        "PARK MGM", "MAIKOYA", "DIAMONDDAY"
    ],
    "subscriptions": [
        "NETFLIX", "SPOTIFY", "APPLE.COM", "GOOGLE", "AMAZON PRIME",
        "DISNEY PLUS", "CRAVE", "HBO", "MEMBERSHIP FEE", "ANNUAL FEE",
        "BELL MEDIA", "INTEREST"
    ],
    "donations": [
        "HUMANE SOCIETY", "TORONTOHUMANESOCIETY", "CANADAHELPS", "DAILY BREAD",
        "SICKKIDS", "RED CROSS", "SALVATION ARMY", "UNITED WAY", "WWF",
        "GREENPEACE", "DOCTORS WITHOUT", "OXFAM", "GOFNDME", "GOFUNDME"
    ],
    "beauty_lifestyle": [
        "PEDI N NAILS", "NAIL SALON", "NAILS", "WELL.CA", "SEPHORA", "SEHPORA",
        "SHOP.SHOPPERSDRUGMART", "SHOPDRUGSMART", "SPA ", "SALON",
        "HAIR", "BEAUTY", "MASSAGE", "FACIAL", "WAXING", "BROW",
        "IHERB", "PRETTYCLEANSHOP"
    ],
    "home": [
        "SHERWIN WILLIAMS", "JUST JUNK", "SINKS DIRECT", "BENJAMIN MOORE",
        "DULUX", "HOME HARDWARE", "ACE HARDWARE", "PLUMBING", "ELECTRICAL",
        "OBH REFILLERY", "WWW.PICTOREM", "WEDGE STUDIO"
    ]
}

# Category definitions for chequing accounts
CHEQUING_CATEGORIES = {
    "mortgage": [
        "FN               MTG"
    ],
    "housing": [
        "TSCC 1725", "ENERCARE HOME", "ENBRIDGE GAS", "TORONTO HYDRO",
        "TOR-UTILITIES", "TOR UTILITY", "TORONTO UTILITY"
    ],
    "insurance": [
        "BMO INSURANCE", "WAWANESA INS", "TRUPANION"
    ],
    "telecom": [
        "TELUS COMM", "BELL"
    ],
    "credit_card_payment": [
        "TD VISA PREAUTH", "AMEX BILL PYMT"
    ],
    "transfers": [
        "TFR-TO", "TFR-FR"
    ],
    "loans": [
        "SPL             LOAN", "SCOTIA PLAN", "BANK OF NOVA SC LOAN"
    ],
    "investments": [
        "WS INVESTMENTS"
    ],
    "bank_fees": [
        "MONTHLY ACCOUNT FEE", "WITHDRAWAL FEES", "OVERDRAFT INTEREST",
        "PODP FEE", "SEND E-TFR FEE", "FX ATM W/D FEE"
    ],
    "e_transfers": [
        "SEND E-TFR"
    ],
    "cash_withdrawal": [
        "ATM W/D", "CASH WITHDRA"
    ],
    "income": [
        "RIPPLING CANADA", "PEOPLE CENTER", "CANADA LIFE      INS",
        "MOBILE DEPOSIT", "E-TRANSFER"
    ],
    "eating_out": [
        "DARK HORSE"
    ]
}


def classify_transaction(description: str, categories: dict) -> str:
    """Classify a transaction based on its description."""
    description_upper = description.upper()
    
    # Check each category's keywords
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.upper() in description_upper:
                return category
    
    return "other"


def process_account(account_name: str, categories: dict):
    """Process and classify transactions for an account."""
    input_file = PROCESSED_DATA_DIR / f"{account_name}_combined.csv"
    output_file = PROCESSED_DATA_DIR / f"{account_name}_classified.csv"
    
    print(f"\n[{account_name}]")
    print(f"  Reading from: {input_file}")
    
    df = pd.read_csv(input_file)
    print(f"  Loaded {len(df)} transactions")
    
    # Classify each transaction
    df["category"] = df["description"].apply(lambda x: classify_transaction(x, categories))
    
    # Print category breakdown
    print("  Category breakdown:")
    category_counts = df["category"].value_counts()
    for category, count in category_counts.items():
        print(f"    {category}: {count}")
    
    # Save classified transactions
    df.to_csv(output_file, index=False)
    print(f"  Saved to: {output_file}")
    
    # Show "other" transactions for review
    other_transactions = df[df["category"] == "other"]["description"].unique()
    if len(other_transactions) > 0:
        print(f"  Transactions classified as 'other' ({len(other_transactions)} unique):")
        for desc in other_transactions[:10]:
            print(f"    - {desc}")
        if len(other_transactions) > 10:
            print(f"    ... and {len(other_transactions) - 10} more")


def main():
    print("=" * 60)
    print("Classifying transactions...")
    print("=" * 60)
    
    # Process credit cards
    process_account("td_visa_credit_card", CREDIT_CARD_CATEGORIES)
    process_account("brydon_amex", AMEX_CATEGORIES)
    process_account("kennedy_amex", AMEX_CATEGORIES)
    
    # Process chequing accounts
    process_account("brydon_chequings", CHEQUING_CATEGORIES)
    process_account("joint_chequings", CHEQUING_CATEGORIES)
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
