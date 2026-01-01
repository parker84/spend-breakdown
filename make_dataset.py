import pandas as pd
from pathlib import Path

# Define paths
RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")

# Column names for the CSV files (they don't have headers)
COLUMNS = ["date", "description", "debit", "credit", "balance"]

# Account configurations
ACCOUNTS = {
    "td_visa_credit_card": {
        "path": RAW_DATA_DIR / "credit_card",
        "date_format": "%m/%d/%Y",
        "has_header": False,
    },
    "brydon_amex": {
        "path": RAW_DATA_DIR / "amex_credit_card" / "brydon_amex_2025.csv",
        "date_format": "%d %b. %Y",
        "has_header": True,
    },
    "kennedy_amex": {
        "path": RAW_DATA_DIR / "amex_credit_card" / "kennedy_amex_2025.csv",
        "date_format": "%d %b. %Y",
        "has_header": True,
    },
    "brydon_chequings": {
        "path": RAW_DATA_DIR / "chequings" / "Brydon Chequings - Account Activity Overview  - 2025.csv",
        "date_format": "%Y-%m-%d",
        "has_header": False,
    },
    "joint_chequings": {
        "path": RAW_DATA_DIR / "chequings" / "Joint Chequings -  Account Activity Overview - 2025.csv",
        "date_format": "%Y-%m-%d",
        "has_header": False,
    },
}


def process_account(account_name: str, config: dict) -> pd.DataFrame:
    """Process files for a single account."""
    path = config["path"]
    has_header = config.get("has_header", False)
    
    if path.is_dir():
        # Multiple CSV files in directory
        csv_files = list(path.glob("*.csv"))
        print(f"\n[{account_name}] Found {len(csv_files)} CSV files")
        
        dataframes = []
        for csv_file in csv_files:
            if has_header:
                df = pd.read_csv(csv_file)
            else:
                df = pd.read_csv(csv_file, header=None, names=COLUMNS)
            df["source_file"] = csv_file.stem
            dataframes.append(df)
            print(f"  - Loaded {len(df)} rows from {csv_file.name}")
        
        combined_df = pd.concat(dataframes, ignore_index=True)
    else:
        # Single CSV file
        print(f"\n[{account_name}] Loading {path.name}")
        if has_header:
            combined_df = pd.read_csv(path)
        else:
            combined_df = pd.read_csv(path, header=None, names=COLUMNS)
        combined_df["source_file"] = path.stem
        print(f"  - Loaded {len(combined_df)} rows")
    
    combined_df["account"] = account_name
    return combined_df


def deduplicate_kennedy_amex():
    """Remove Brydon Amex transactions from Kennedy Amex to avoid double-counting."""
    brydon_path = PROCESSED_DATA_DIR / "brydon_amex_combined.csv"
    kennedy_path = PROCESSED_DATA_DIR / "kennedy_amex_combined.csv"
    
    if not brydon_path.exists() or not kennedy_path.exists():
        return
    
    print("\n[Deduplication] Removing Brydon transactions from Kennedy Amex...")
    
    brydon = pd.read_csv(brydon_path)
    kennedy = pd.read_csv(kennedy_path)
    
    original_count = len(kennedy)
    
    # Create keys for matching (date + description + amount)
    brydon["key"] = brydon["date"].astype(str) + "|" + brydon["description"].astype(str) + "|" + brydon["debit"].astype(str)
    kennedy["key"] = kennedy["date"].astype(str) + "|" + kennedy["description"].astype(str) + "|" + kennedy["debit"].astype(str)
    
    # Remove Brydon transactions from Kennedy
    kennedy_filtered = kennedy[~kennedy["key"].isin(brydon["key"])].copy()
    kennedy_filtered = kennedy_filtered.drop(columns=["key"])
    
    # Save filtered Kennedy
    kennedy_filtered.to_csv(kennedy_path, index=False)
    
    removed = original_count - len(kennedy_filtered)
    print(f"  - Removed {removed} duplicate transactions")
    print(f"  - Kennedy Amex now has {len(kennedy_filtered)} transactions")


def main():
    print("=" * 60)
    print("Processing all accounts...")
    print("=" * 60)
    
    # Ensure processed directory exists
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process each account
    for account_name, config in ACCOUNTS.items():
        df = process_account(account_name, config)
        
        # Save to processed folder
        output_path = PROCESSED_DATA_DIR / f"{account_name}_combined.csv"
        df.to_csv(output_path, index=False)
        print(f"  -> Saved {len(df)} rows to: {output_path}")
    
    # Remove Brydon duplicates from Kennedy Amex
    deduplicate_kennedy_amex()
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
