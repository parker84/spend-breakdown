import pandas as pd
from pathlib import Path
import re

# Define paths
PROCESSED_DATA_DIR = Path("data/processed")
INPUT_FILE = PROCESSED_DATA_DIR / "combined_transactions.csv"
OUTPUT_FILE = PROCESSED_DATA_DIR / "classified_transactions.csv"

# Category definitions with keywords (case-insensitive matching)
CATEGORIES = {
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


def classify_transaction(description: str) -> str:
    """Classify a transaction based on its description."""
    description_upper = description.upper()
    
    # Check each category's keywords
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword.upper() in description_upper:
                return category
    
    return "other"


def main():
    # Read the combined transactions
    print(f"Reading transactions from: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} transactions")
    
    # Classify each transaction
    df["category"] = df["description"].apply(classify_transaction)
    
    # Print category breakdown
    print("\n--- Category Breakdown ---")
    category_counts = df["category"].value_counts()
    for category, count in category_counts.items():
        print(f"  {category}: {count}")
    
    # Calculate spending by category (only debits, ignore credits)
    print("\n--- Spending by Category ---")
    spending_by_category = df.groupby("category")["debit"].sum().sort_values(ascending=False)
    for category, total in spending_by_category.items():
        if pd.notna(total) and total > 0:
            print(f"  {category}: ${total:,.2f}")
    
    # Save classified transactions
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved classified transactions to: {OUTPUT_FILE}")
    
    # Show some "other" transactions for review
    other_transactions = df[df["category"] == "other"]["description"].unique()
    if len(other_transactions) > 0:
        print(f"\n--- Transactions classified as 'other' ({len(other_transactions)} unique) ---")
        for desc in other_transactions[:20]:
            print(f"  - {desc}")
        if len(other_transactions) > 20:
            print(f"  ... and {len(other_transactions) - 20} more")


if __name__ == "__main__":
    main()

