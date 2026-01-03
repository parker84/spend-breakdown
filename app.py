import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import datetime
import json

# Paths
USER_ACCOUNTS_FILE = Path("data/user_accounts.json")
USER_DATA_DIR = Path("data/user_uploads")
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Page config
st.set_page_config(
    page_title="Spend Breakdown",
    page_icon="💰",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Mono:wght@400;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    h1, h2, h3 {
        font-family: 'Space Mono', monospace !important;
        color: #00d4aa !important;
    }
    
    .stMetric {
        background: rgba(0, 212, 170, 0.1);
        border: 1px solid rgba(0, 212, 170, 0.3);
        border-radius: 12px;
        padding: 1rem;
    }
    
    .stMetric label {
        color: #8892b0 !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #00d4aa !important;
        font-family: 'Space Mono', monospace !important;
    }
    
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Account type options
ACCOUNT_TYPES = {
    "amex": "Amex Credit Card",
    "td_credit_card": "TD Credit Card",
    "td_chequing": "TD Chequing Account"
}

# Category definitions for TD Chequing accounts
TD_CHEQUING_CATEGORIES = {
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
        "ATM W/D", "CASH WITHDRA", "FX ATM W/D"
    ],
    "income": [
        "RIPPLING CANADA", "PEOPLE CENTER", "CANADA LIFE      INS",
        "MOBILE DEPOSIT", "E-TRANSFER"
    ],
    "eating_out": [
        "DARK HORSE"
    ]
}

# Category definitions for TD Credit Card
TD_CREDIT_CARD_CATEGORIES = {
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

# Categories to exclude from spending analysis (to avoid double counting)
# - credit_card_payment: already tracked on the credit card
# - transfers: internal money movement, not spending
# - income: money coming in, not spending
# - investments: savings/investments, not spending
# - cash_withdrawal: cash itself isn't spending, what you buy with it is
EXCLUDED_CATEGORIES = {
    "credit_card_payment",
    "transfers",
    "income",
    "investments",
    "cash_withdrawal"
}

# Category definitions for Amex (from classify_transactions.py)
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
        "KYOTO ENGINE", "WA FUJITATE", "YASUDASENKEIDO",
        "DLR ", "DISNEYLAND", "DISNEY CALIFORNIA", "COOKIE DOUGH LIGHTFUL",
        "TONGA HUT", "OUT WEST TRADING", "LITTLE LUNCH COFFEE",
        "EXPEDIA", "S AND R MEDALLION",
        "GO APP RIDE", "LS TRAVEL RETAIL", "PORTER AIRLINES",
        "SUICA", "CNP POINT THE WAY", "MOBILE ICOCA", "JRC SMART EX",
        "WDW TICKETS", "WDW CONNECTIONS", "ALIPAY", "FUELROD", "MAISONCO"
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

# Color palette
COLORS = {
    "pet": "#f472b6",
    "groceries": "#00d4aa",
    "beer_liquor": "#ff6b6b",
    "coffee": "#c9a227",
    "eating_out": "#ff8c42",
    "goods_gifts": "#ec4899",
    "transportation": "#4ecdc4",
    "travel": "#818cf8",
    "entertainment": "#06b6d4",
    "subscriptions": "#a855f7",
    "donations": "#22c55e",
    "beauty_lifestyle": "#fb7185",
    "home": "#84cc16",
    # TD Chequing categories
    "mortgage": "#ef4444",
    "housing": "#f97316",
    "insurance": "#eab308",
    "telecom": "#22c55e",
    "credit_card_payment": "#14b8a6",
    "transfers": "#0ea5e9",
    "loans": "#6366f1",
    "investments": "#8b5cf6",
    "bank_fees": "#d946ef",
    "e_transfers": "#ec4899",
    "cash_withdrawal": "#f43f5e",
    "income": "#10b981",
    # TD Credit Card categories
    "utilities": "#0891b2",
    "ordering_in": "#f59e0b",
    "other": "#6b7280"
}


def classify_transaction(description: str, categories: dict = None) -> str:
    """Classify a transaction based on its description using keywords."""
    if categories is None:
        categories = AMEX_CATEGORIES
    description_upper = description.upper()
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.upper() in description_upper:
                return category
    return "other"


def load_user_accounts() -> dict:
    """Load user accounts from JSON file."""
    if USER_ACCOUNTS_FILE.exists():
        with open(USER_ACCOUNTS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_user_accounts(accounts: dict):
    """Save user accounts to JSON file."""
    USER_ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(USER_ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=2)


def parse_amex_xls(uploaded_file) -> pd.DataFrame:
    """Parse Amex XLS file and return cleaned DataFrame."""
    # Read the XLS file
    df = pd.read_excel(uploaded_file)
    
    # Find the header row (contains "Date" in first column)
    header_row = None
    header_values = None
    for idx, row in df.iterrows():
        if str(row.iloc[0]).strip() == "Date":
            header_row = idx
            header_values = [str(v).strip() for v in row.values]
            break
    
    if header_row is None:
        raise ValueError("Could not find header row with 'Date' column")
    
    # Find column indices dynamically (different Amex exports have different structures)
    date_col = 0  # Always first
    desc_col = header_values.index("Description") if "Description" in header_values else 2
    
    # Find Amount column - may be at different positions
    amount_col = None
    for i, h in enumerate(header_values):
        if h == "Amount":
            amount_col = i
            break
    if amount_col is None:
        amount_col = 3  # Fallback
    
    # Re-read with correct header
    uploaded_file.seek(0)
    df = pd.read_excel(uploaded_file, skiprows=header_row + 1, header=None)
    
    # Extract columns dynamically
    processed_df = pd.DataFrame({
        "date": df.iloc[:, date_col],
        "description": df.iloc[:, desc_col].astype(str),
        "amount_str": df.iloc[:, amount_col].astype(str)
    })
    
    # Parse dates
    processed_df["date"] = pd.to_datetime(processed_df["date"], format="mixed", dayfirst=True, errors="coerce")
    
    # Parse amounts (remove $ and commas)
    processed_df["debit"] = pd.to_numeric(
        processed_df["amount_str"].str.replace(r'[$,]', '', regex=True),
        errors="coerce"
    ).abs()
    
    # Drop invalid rows
    processed_df = processed_df.dropna(subset=["date", "description"])
    processed_df = processed_df[processed_df["description"].str.len() > 0]
    processed_df = processed_df[~processed_df["description"].str.lower().isin(["nan", "none", ""])]
    
    # Fill NaN amounts with 0
    processed_df["debit"] = processed_df["debit"].fillna(0)
    processed_df["credit"] = 0.0
    
    # Drop temporary column
    processed_df = processed_df.drop(columns=["amount_str"])
    
    return processed_df


def parse_td_chequing_csv(uploaded_file) -> pd.DataFrame:
    """Parse TD Chequing CSV file and return cleaned DataFrame."""
    # TD Chequing CSVs have no header, columns are: date, description, debit, credit, balance
    df = pd.read_csv(uploaded_file, header=None, names=["date", "description", "debit", "credit", "balance"])
    
    # Parse dates (format: YYYY-MM-DD)
    df["date"] = pd.to_datetime(df["date"], format="mixed", errors="coerce")
    
    # Clean up description
    df["description"] = df["description"].astype(str).str.strip()
    
    # Convert debit/credit to numeric
    df["debit"] = pd.to_numeric(df["debit"], errors="coerce").fillna(0)
    df["credit"] = pd.to_numeric(df["credit"], errors="coerce").fillna(0)
    
    # Drop invalid rows
    df = df.dropna(subset=["date"])
    df = df[df["description"].str.len() > 0]
    df = df[~df["description"].str.lower().isin(["nan", "none", ""])]
    
    # Drop balance column
    df = df.drop(columns=["balance"], errors="ignore")
    
    return df


def parse_td_credit_card_csvs(uploaded_files: list) -> pd.DataFrame:
    """Parse multiple TD Credit Card CSV files, combine and deduplicate."""
    all_dfs = []
    
    for uploaded_file in uploaded_files:
        # TD Credit Card CSVs have no header, columns are: date, description, debit, credit, balance
        # Date format is MM/DD/YYYY
        df = pd.read_csv(uploaded_file, header=None, names=["date", "description", "debit", "credit", "balance"])
        df["source_file"] = uploaded_file.name
        all_dfs.append(df)
    
    if not all_dfs:
        return pd.DataFrame()
    
    # Combine all files
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    # Parse dates (format: MM/DD/YYYY)
    combined_df["date"] = pd.to_datetime(combined_df["date"], format="mixed", errors="coerce")
    
    # Clean up description
    combined_df["description"] = combined_df["description"].astype(str).str.strip()
    
    # Convert debit/credit to numeric
    combined_df["debit"] = pd.to_numeric(combined_df["debit"], errors="coerce").fillna(0)
    combined_df["credit"] = pd.to_numeric(combined_df["credit"], errors="coerce").fillna(0)
    
    # Drop invalid rows
    combined_df = combined_df.dropna(subset=["date"])
    combined_df = combined_df[combined_df["description"].str.len() > 0]
    combined_df = combined_df[~combined_df["description"].str.lower().isin(["nan", "none", ""])]
    
    # Deduplicate based on date + description + debit + credit
    combined_df["dedup_key"] = (
        combined_df["date"].astype(str) + "|" + 
        combined_df["description"] + "|" + 
        combined_df["debit"].astype(str) + "|" + 
        combined_df["credit"].astype(str)
    )
    original_count = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=["dedup_key"], keep="first")
    dedup_count = original_count - len(combined_df)
    
    # Drop helper columns
    combined_df = combined_df.drop(columns=["balance", "source_file", "dedup_key"], errors="ignore")
    
    return combined_df


def process_uploaded_file(uploaded_file, account_name: str, account_type: str = "amex") -> tuple[pd.DataFrame, str]:
    """Process uploaded file: parse, classify, and save."""
    
    # Parse based on account type
    if account_type == "amex":
        df = parse_amex_xls(uploaded_file)
        categories = AMEX_CATEGORIES
    elif account_type == "td_chequing":
        df = parse_td_chequing_csv(uploaded_file)
        categories = TD_CHEQUING_CATEGORIES
    else:
        raise ValueError(f"Unknown account type: {account_type}")
    
    if len(df) == 0:
        raise ValueError("No valid transactions found in file")
    
    # Classify transactions
    df["category"] = df["description"].apply(lambda x: classify_transaction(x, categories))
    
    # Generate account key
    account_key = account_name.lower().replace(" ", "_").replace("-", "_")
    account_key = "".join(c for c in account_key if c.isalnum() or c == "_")
    
    # Save processed file
    output_path = USER_DATA_DIR / f"{account_key}_classified.csv"
    df.to_csv(output_path, index=False)
    
    # Save account config
    accounts = load_user_accounts()
    accounts[account_key] = {
        "name": account_name,
        "file_path": str(output_path),
        "original_filename": uploaded_file.name,
        "account_type": account_type
    }
    save_user_accounts(accounts)
    
    return df, account_key


def process_td_credit_card_files(uploaded_files: list, account_name: str) -> tuple[pd.DataFrame, str]:
    """Process multiple TD Credit Card CSV files: parse, combine, dedupe, classify, and save."""
    
    # Parse and combine all files
    df = parse_td_credit_card_csvs(uploaded_files)
    
    if len(df) == 0:
        raise ValueError("No valid transactions found in files")
    
    # Classify transactions
    df["category"] = df["description"].apply(lambda x: classify_transaction(x, TD_CREDIT_CARD_CATEGORIES))
    
    # Generate account key
    account_key = account_name.lower().replace(" ", "_").replace("-", "_")
    account_key = "".join(c for c in account_key if c.isalnum() or c == "_")
    
    # Save processed file
    output_path = USER_DATA_DIR / f"{account_key}_classified.csv"
    df.to_csv(output_path, index=False)
    
    # Save account config
    accounts = load_user_accounts()
    accounts[account_key] = {
        "name": account_name,
        "file_path": str(output_path),
        "original_filename": f"{len(uploaded_files)} CSV files",
        "account_type": "td_credit_card"
    }
    save_user_accounts(accounts)
    
    return df, account_key


@st.cache_data
def load_account_data(account_key: str) -> pd.DataFrame:
    """Load classified transaction data for an account."""
    accounts = load_user_accounts()
    if account_key not in accounts:
        return pd.DataFrame()
    
    config = accounts[account_key]
    file_path = Path(config["file_path"])
    
    if not file_path.exists():
        return pd.DataFrame()
    
    df = pd.read_csv(file_path)
    df["date"] = pd.to_datetime(df["date"], format="mixed", dayfirst=True, errors="coerce")
    df = df.dropna(subset=["date"])
    
    df["month"] = df["date"].dt.to_period("M")
    df["month_str"] = df["date"].dt.strftime("%b %Y")
    df["month_order"] = df["date"].dt.to_period("M").astype(str)
    
    df["debit"] = df["debit"].fillna(0)
    df["credit"] = df["credit"].fillna(0)
    df["account_name"] = config["name"]
    
    return df


def main():
    st.title("💰 Spend Breakdown Dashboard")
    
    # Load existing accounts
    accounts = load_user_accounts()
    
    # If no accounts exist, show prominent onboarding experience
    if not accounts:
        st.markdown("")
        st.markdown("")
        
        # Centered welcome section
        col_left, col_center, col_right = st.columns([1, 2, 1])
        
        with col_center:
            st.markdown("""
            <div style="text-align: center; padding: 2rem 0;">
                <h2 style="color: #00d4aa; margin-bottom: 0.5rem;">👋 Welcome!</h2>
                <p style="color: #8892b0; font-size: 1.1rem;">Get started by uploading your first account statement</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Account type selector
            onboard_account_type = st.selectbox(
                "Account Type",
                options=list(ACCOUNT_TYPES.keys()),
                format_func=lambda x: ACCOUNT_TYPES[x],
                key="onboard_account_type"
            )
            
            # File type hint and uploader based on account type
            if onboard_account_type == "amex":
                st.caption("Upload your Amex XLS export file")
                onboard_file = st.file_uploader(
                    "Choose file",
                    type=["xls", "xlsx"],
                    key="onboard_uploader",
                    label_visibility="collapsed"
                )
                onboard_files = [onboard_file] if onboard_file else []
            elif onboard_account_type == "td_credit_card":
                st.caption("Upload your TD Credit Card CSV files (multiple monthly statements)")
                onboard_files = st.file_uploader(
                    "Choose files",
                    type=["csv"],
                    key="onboard_uploader_multi",
                    label_visibility="collapsed",
                    accept_multiple_files=True
                )
            else:  # td_chequing
                st.caption("Upload your TD Chequing CSV export file")
                onboard_file = st.file_uploader(
                    "Choose file",
                    type=["csv"],
                    key="onboard_uploader",
                    label_visibility="collapsed"
                )
                onboard_files = [onboard_file] if onboard_file else []
            
            if onboard_files:
                # Suggest account name
                if onboard_account_type == "td_credit_card":
                    suggested_name = "TD Credit Card"
                    file_count_msg = f"{len(onboard_files)} file(s) selected"
                    st.caption(file_count_msg)
                else:
                    suggested_name = onboard_files[0].name.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
                
                onboard_account_name = st.text_input("Account Name", value=suggested_name, key="onboard_account_name")
                
                if st.button("🚀 Process & Add Account", type="primary", use_container_width=True, key="onboard_process"):
                    if not onboard_account_name.strip():
                        st.error("Please enter an account name")
                    else:
                        try:
                            with st.spinner("Processing your statement..."):
                                if onboard_account_type == "td_credit_card":
                                    df, account_key = process_td_credit_card_files(
                                        onboard_files,
                                        onboard_account_name.strip()
                                    )
                                else:
                                    df, account_key = process_uploaded_file(
                                        onboard_files[0],
                                        onboard_account_name.strip(),
                                        onboard_account_type
                                    )
                            st.success(f"✅ Added {len(df)} transactions!")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
        
        return
    
    # Header row with account selector and add button (only shown when accounts exist)
    col_select, col_add = st.columns([4, 1])
    
    with col_add:
        with st.popover("➕ Add Account"):
            st.markdown("### Upload Statement")
            
            # Account type selector
            account_type = st.selectbox(
                "Account Type",
                options=list(ACCOUNT_TYPES.keys()),
                format_func=lambda x: ACCOUNT_TYPES[x],
                key="header_account_type"
            )
            
            # File type hint and uploader based on account type
            if account_type == "amex":
                st.caption("Upload your Amex XLS export file")
                uploaded_file = st.file_uploader(
                    "Choose file",
                    type=["xls", "xlsx"],
                    key="uploader",
                    label_visibility="collapsed"
                )
                uploaded_files = [uploaded_file] if uploaded_file else []
            elif account_type == "td_credit_card":
                st.caption("Upload your TD Credit Card CSV files (multiple monthly statements)")
                uploaded_files = st.file_uploader(
                    "Choose files",
                    type=["csv"],
                    key="uploader_multi",
                    label_visibility="collapsed",
                    accept_multiple_files=True
                )
            else:  # td_chequing
                st.caption("Upload your TD Chequing CSV export file")
                uploaded_file = st.file_uploader(
                    "Choose file",
                    type=["csv"],
                    key="uploader",
                    label_visibility="collapsed"
                )
                uploaded_files = [uploaded_file] if uploaded_file else []
            
            if uploaded_files:
                # Suggest account name
                if account_type == "td_credit_card":
                    suggested_name = "TD Credit Card"
                    st.caption(f"{len(uploaded_files)} file(s) selected")
                else:
                    suggested_name = uploaded_files[0].name.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
                
                account_name = st.text_input("Account Name", value=suggested_name)
                
                if st.button("🚀 Process & Add", type="primary", use_container_width=True):
                    if not account_name.strip():
                        st.error("Please enter an account name")
                    else:
                        try:
                            with st.spinner("Processing..."):
                                if account_type == "td_credit_card":
                                    df, account_key = process_td_credit_card_files(
                                        uploaded_files,
                                    account_name.strip()
                                )
                                else:
                                    df, account_key = process_uploaded_file(
                                        uploaded_files[0],
                                        account_name.strip(),
                                        account_type
                                )
                            st.success(f"✅ Added {len(df)} transactions!")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
    
    with col_select:
        
        # Build account options (combined view if multiple accounts)
        account_options = {}
        if len(accounts) > 1:
            account_options["combined_all"] = "📊 All Accounts Combined"
        for key, config in accounts.items():
            account_options[key] = config["name"]
        
        account_key = st.selectbox(
            "Select Account",
            options=list(account_options.keys()),
            format_func=lambda x: account_options[x],
            label_visibility="collapsed"
        )
    
    # Load data
    if account_key == "combined_all":
        dfs = []
        for key in accounts.keys():
            df = load_account_data(key)
            if not df.empty:
                df["account"] = key
                dfs.append(df)
        if dfs:
            df = pd.concat(dfs, ignore_index=True)
        else:
            df = pd.DataFrame()
    else:
        df = load_account_data(account_key)
    
    if df.empty:
        st.warning("No data available. Try uploading a file.")
        return
    
    # Sidebar: Date filters and account management
    with st.sidebar:
        st.header("📅 Date Filters")
        
        min_date = df["date"].min().date()
        max_date = df["date"].max().date()
        
        # Default: Jan 2025 - Dec 2025
        default_start = max(datetime.date(2025, 1, 1), min_date)
        default_end = min(datetime.date(2025, 12, 31), max_date)
        
        start_date = st.date_input("Start", value=default_start, min_value=min_date, max_value=max_date)
        end_date = st.date_input("End", value=default_end, min_value=min_date, max_value=max_date)
        
        st.markdown("---")
        
        # Account management
        if accounts:
            st.header("⚙️ Manage Accounts")
            for key, config in list(accounts.items()):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.caption(config["name"])
                with col2:
                    if st.button("🗑️", key=f"del_{key}"):
                        try:
                            Path(config["file_path"]).unlink(missing_ok=True)
                        except:
                            pass
                        del accounts[key]
                        save_user_accounts(accounts)
                        st.cache_data.clear()
                        st.rerun()
            
            st.markdown("")
            with st.popover("➕ Add Account", use_container_width=True):
                st.markdown("### Upload Statement")
                
                # Account type selector
                sidebar_account_type = st.selectbox(
                    "Account Type",
                    options=list(ACCOUNT_TYPES.keys()),
                    format_func=lambda x: ACCOUNT_TYPES[x],
                    key="sidebar_account_type"
                )
                
                # File type hint and uploader based on account type
                if sidebar_account_type == "amex":
                    st.caption("Upload your Amex XLS export file")
                    sidebar_file = st.file_uploader(
                        "Choose file",
                        type=["xls", "xlsx"],
                        key="sidebar_uploader",
                        label_visibility="collapsed"
                    )
                    sidebar_files = [sidebar_file] if sidebar_file else []
                elif sidebar_account_type == "td_credit_card":
                    st.caption("Upload your TD Credit Card CSV files (multiple monthly statements)")
                    sidebar_files = st.file_uploader(
                        "Choose files",
                        type=["csv"],
                        key="sidebar_uploader_multi",
                        label_visibility="collapsed",
                        accept_multiple_files=True
                    )
                else:  # td_chequing
                    st.caption("Upload your TD Chequing CSV export file")
                    sidebar_file = st.file_uploader(
                        "Choose file",
                        type=["csv"],
                        key="sidebar_uploader",
                        label_visibility="collapsed"
                    )
                    sidebar_files = [sidebar_file] if sidebar_file else []
                
                if sidebar_files:
                    if sidebar_account_type == "td_credit_card":
                        suggested_name = "TD Credit Card"
                        st.caption(f"{len(sidebar_files)} file(s) selected")
                    else:
                        suggested_name = sidebar_files[0].name.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
                    
                    sidebar_account_name = st.text_input("Account Name", value=suggested_name, key="sidebar_account_name")
                    
                    if st.button("🚀 Process & Add", type="primary", use_container_width=True, key="sidebar_process"):
                        if not sidebar_account_name.strip():
                            st.error("Please enter an account name")
                        else:
                            try:
                                with st.spinner("Processing..."):
                                    if sidebar_account_type == "td_credit_card":
                                        df_new, account_key = process_td_credit_card_files(
                                            sidebar_files,
                                            sidebar_account_name.strip()
                                        )
                                    else:
                                        df_new, account_key = process_uploaded_file(
                                            sidebar_files[0],
                                            sidebar_account_name.strip(),
                                            sidebar_account_type
                                        )
                                st.success(f"✅ Added {len(df_new)} transactions!")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
    
    # Filter by date
    df = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)]
    
    if df.empty:
        st.warning("No transactions in selected date range.")
        return
    
    # Only spending (debit > 0) and exclude non-spending categories (to avoid double counting)
    spending_df = df[
        (df["debit"] > 0) & 
        (~df["category"].isin(EXCLUDED_CATEGORIES))
    ].copy()
    
    if spending_df.empty:
        st.warning("No spending transactions found.")
        return
    
    st.markdown("---")
    
    # Summary metrics
    total_spend = spending_df["debit"].sum()
    num_transactions = len(spending_df)
    avg_transaction = spending_df["debit"].mean()
    num_months = spending_df["month"].nunique()
    monthly_avg = total_spend / max(num_months, 1)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Spending", f"${total_spend:,.2f}")
    with col2:
        st.metric("Monthly Avg", f"${monthly_avg:,.2f}")
    with col3:
        st.metric("Transactions", f"{num_transactions:,}")
    with col4:
        st.metric("Avg Transaction", f"${avg_transaction:.2f}")
    
    st.markdown("---")
    
    # Charts
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📈 Monthly Spending")
        
        monthly = spending_df.groupby("month_order")["debit"].sum().reset_index()
        monthly = monthly.sort_values("month_order")
        monthly["label"] = pd.to_datetime(monthly["month_order"]).dt.strftime("%b %Y")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly["label"],
            y=monthly["debit"],
            mode="lines+markers",
            line=dict(color="#00d4aa", width=3),
            marker=dict(size=10),
            fill="tozeroy",
            fillcolor="rgba(0, 212, 170, 0.1)",
            hovertemplate="<b>%{x}</b><br>$%{y:,.2f}<extra></extra>"
        ))
        
        # Add average line
        fig.add_hline(y=monthly_avg, line_dash="dash", line_color="#ff6b6b",
                      annotation_text=f"Avg: ${monthly_avg:,.0f}")
        
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#8892b0"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", tickprefix="$"),
            margin=dict(l=0, r=0, t=20, b=0),
            height=350
        )
        st.plotly_chart(fig, width='stretch')
    
    with col_right:
        st.subheader("🍩 By Category")
        
        cat_spend = spending_df.groupby("category")["debit"].sum().reset_index()
        cat_spend = cat_spend.sort_values("debit", ascending=False)
        
        chart_colors = [COLORS.get(c, "#6b7280") for c in cat_spend["category"]]
        
        fig_donut = go.Figure(data=[go.Pie(
            labels=cat_spend["category"].str.replace("_", " ").str.title(),
            values=cat_spend["debit"],
            hole=0.6,
            marker=dict(colors=chart_colors),
            textinfo="percent",
            textfont=dict(color="white", size=11),
            hovertemplate="<b>%{label}</b><br>$%{value:,.2f}<br>%{percent}<extra></extra>"
        )])
        
        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#8892b0"),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, font=dict(size=10)),
            margin=dict(l=0, r=0, t=20, b=80),
            height=350
        )
        st.plotly_chart(fig_donut, width='stretch')
    
    st.markdown("---")
    
    # Category trends
    st.subheader("📊 Category Trends")
    
    categories_sorted = spending_df.groupby("category")["debit"].sum().sort_values(ascending=False).index.tolist()
    
    # Get all months in the date range for consistent x-axis
    all_months = spending_df.sort_values("month_order")["month_order"].unique()
    all_months_labels = [pd.to_datetime(m).strftime("%b") for m in all_months]
    
    cols_per_row = 4
    # Show all categories (no limit)
    for i in range(0, len(categories_sorted), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(categories_sorted):
                category = categories_sorted[i + j]
                cat_data = spending_df[spending_df["category"] == category]
                cat_monthly = cat_data.groupby("month_order")["debit"].sum()
                
                # Reindex to include all months with 0 for missing
                cat_monthly = cat_monthly.reindex(all_months, fill_value=0).reset_index()
                cat_monthly.columns = ["month_order", "debit"]
                cat_monthly["label"] = [pd.to_datetime(m).strftime("%b") for m in cat_monthly["month_order"]]
                
                total = cat_data["debit"].sum()
                cat_avg = total / num_months
                color = COLORS.get(category, "#6b7280")
                
                with col:
                    fig_cat = go.Figure()
                    fig_cat.add_trace(go.Scatter(
                        x=cat_monthly["label"],
                        y=cat_monthly["debit"],
                        mode="lines+markers",
                        line=dict(color=color, width=2),
                        marker=dict(size=6),
                        fill="tozeroy",
                        fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)",
                        hovertemplate="$%{y:,.0f}<extra></extra>"
                    ))
                    fig_cat.add_hline(y=cat_avg, line_dash="dot", line_color="#ff6b6b", line_width=1)
                    
                    fig_cat.update_layout(
                        title=dict(
                            text=f"{category.replace('_', ' ').title()}<br><span style='font-size:10px'>${total:,.0f} | ${cat_avg:,.0f}/mo</span>",
                            font=dict(size=12, color=color),
                            x=0.5
                        ),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#8892b0"),
                        xaxis=dict(showgrid=False, tickfont=dict(size=9)),
                        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", tickprefix="$", tickfont=dict(size=9)),
                        margin=dict(l=0, r=0, t=50, b=0),
                        height=180
                    )
                    st.plotly_chart(fig_cat, width='stretch')
    
    st.markdown("---")
    
    # Transaction table
    st.subheader("🔍 Transactions")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        sel_cats = st.multiselect("Filter Category", sorted(spending_df["category"].unique()))
    with col_f2:
        months = spending_df.sort_values("month_order")["month_str"].unique().tolist()
        sel_months = st.multiselect("Filter Month", months)
    
    filtered = spending_df.copy()
    if sel_cats:
        filtered = filtered[filtered["category"].isin(sel_cats)]
    if sel_months:
        filtered = filtered[filtered["month_str"].isin(sel_months)]
    
    display_cols = ["date", "description", "debit", "category"]
    if account_key == "combined_all":
        display_cols.insert(1, "account_name")
    
    display_df = filtered[display_cols].copy()
    display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
    display_df = display_df.sort_values("date", ascending=False)
    display_df.columns = ["Date", "Account", "Description", "Amount", "Category"] if account_key == "combined_all" else ["Date", "Description", "Amount", "Category"]
    
    st.markdown(f"**{len(display_df)} transactions** | **Total: ${filtered['debit'].sum():,.2f}**")
    st.dataframe(display_df, width='stretch', height=400, hide_index=True)


if __name__ == "__main__":
    main()
