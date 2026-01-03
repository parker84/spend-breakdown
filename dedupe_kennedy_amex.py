"""
One-off script to remove Brydon's transactions from Kennedy's Amex statement.
This prevents double-counting since Brydon is a supplementary cardholder on Kennedy's account.
"""

import pandas as pd
from pathlib import Path

# File paths
KENNEDY_XLS = Path("data/raw/amex_credit_card/Kennedy Amex - 2025.xls")
BRYDON_XLS = Path("data/raw/amex_credit_card/Brydon Amex - 2025.xls")
OUTPUT_XLS = Path("data/raw/amex_credit_card/Kennedy Amex - 2025.xls")  # Overwrite original


def get_header_info(file_path: Path) -> tuple[int, list]:
    """Get header row index and column names from Amex XLS."""
    df = pd.read_excel(file_path, header=None)
    
    for idx, row in df.iterrows():
        if str(row.iloc[0]).strip() == "Date":
            header_values = [str(v).strip() for v in row.values]
            return idx, header_values
    
    raise ValueError(f"Could not find header row in {file_path}")


def parse_transactions(file_path: Path, header_row: int, header_values: list) -> pd.DataFrame:
    """Parse transactions from Amex XLS."""
    # Find column indices
    desc_col = header_values.index("Description") if "Description" in header_values else 2
    amount_col = header_values.index("Amount") if "Amount" in header_values else 3
    
    # Read transactions (skip to after header)
    df = pd.read_excel(file_path, skiprows=header_row + 1, header=None)
    
    # Create dedup key from date, description, amount
    df["_key"] = (
        df.iloc[:, 0].astype(str) + "|" + 
        df.iloc[:, desc_col].astype(str) + "|" + 
        df.iloc[:, amount_col].astype(str)
    )
    
    return df


def main():
    print("=" * 60)
    print("Deduplicating Kennedy Amex (removing Brydon's transactions)")
    print("=" * 60)
    
    # Get header info from both files
    print(f"\nReading Kennedy Amex: {KENNEDY_XLS}")
    kennedy_header_row, kennedy_header_values = get_header_info(KENNEDY_XLS)
    kennedy_txns = parse_transactions(KENNEDY_XLS, kennedy_header_row, kennedy_header_values)
    print(f"  Found {len(kennedy_txns)} transactions")
    
    print(f"\nReading Brydon Amex: {BRYDON_XLS}")
    brydon_header_row, brydon_header_values = get_header_info(BRYDON_XLS)
    brydon_txns = parse_transactions(BRYDON_XLS, brydon_header_row, brydon_header_values)
    print(f"  Found {len(brydon_txns)} transactions")
    
    # Find Brydon's transaction keys
    brydon_keys = set(brydon_txns["_key"])
    
    # Mark duplicates in Kennedy
    kennedy_txns["_is_duplicate"] = kennedy_txns["_key"].isin(brydon_keys)
    
    duplicates = kennedy_txns[kennedy_txns["_is_duplicate"]]
    print(f"\nFound {len(duplicates)} duplicate transactions to remove")
    
    if len(duplicates) > 0:
        desc_col = kennedy_header_values.index("Description") if "Description" in kennedy_header_values else 2
        amount_col = kennedy_header_values.index("Amount") if "Amount" in kennedy_header_values else 3
        
        print("\nDuplicates being removed:")
        for idx, row in duplicates.head(10).iterrows():
            date = row.iloc[0]
            desc = str(row.iloc[desc_col])[:40]
            amt = row.iloc[amount_col]
            print(f"  - {date}: {desc} ({amt})")
        if len(duplicates) > 10:
            print(f"  ... and {len(duplicates) - 10} more")
    
    # Filter to keep only non-duplicates
    kennedy_filtered = kennedy_txns[~kennedy_txns["_is_duplicate"]].copy()
    kennedy_filtered = kennedy_filtered.drop(columns=["_key", "_is_duplicate"])
    
    print(f"\nOriginal Kennedy Amex: {len(kennedy_txns)} transactions")
    print(f"After deduplication: {len(kennedy_filtered)} transactions")
    print(f"Removed: {len(kennedy_txns) - len(kennedy_filtered)} transactions")
    
    # Now rebuild the full XLS with header rows + filtered transactions
    full_df = pd.read_excel(KENNEDY_XLS, header=None)
    
    # Get header section (everything up to and including header row)
    header_section = full_df.iloc[:kennedy_header_row + 2]  # +2 because: rows 0 to header_row, plus the header row itself
    
    # Combine header section with filtered transactions
    result_df = pd.concat([header_section, kennedy_filtered], ignore_index=True)
    
    print(f"\nOriginal file: {len(full_df)} total rows")
    print(f"New file: {len(result_df)} total rows")
    
    # Save back to XLS
    print(f"\nSaving to: {OUTPUT_XLS}")
    result_df.to_excel(OUTPUT_XLS, index=False, header=False)
    print("✅ Done!")
    
    print("\n" + "=" * 60)
    print("Deduplication complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
