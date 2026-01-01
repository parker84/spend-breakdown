import pandas as pd
from pathlib import Path

# Define paths
RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")

# Column names for the CSV files (they don't have headers)
COLUMNS = ["date", "description", "debit", "credit", "balance"]

# Read all CSV files from raw data directory
csv_files = list(RAW_DATA_DIR.glob("*.csv"))
print(f"Found {len(csv_files)} CSV files:")
for f in csv_files:
    print(f"  - {f.name}")

# Read each file into a dataframe
dataframes = []
for csv_file in csv_files:
    df = pd.read_csv(csv_file, header=None, names=COLUMNS)
    # Add source file column to track origin
    df["source_file"] = csv_file.stem
    dataframes.append(df)
    print(f"Loaded {len(df)} rows from {csv_file.name}")

# Concatenate all dataframes
combined_df = pd.concat(dataframes, ignore_index=True)
print(f"\nTotal rows after concatenation: {len(combined_df)}")

# Ensure processed directory exists
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Save to processed folder
output_path = PROCESSED_DATA_DIR / "combined_transactions.csv"
combined_df.to_csv(output_path, index=False)
print(f"\nSaved combined dataset to: {output_path}")

