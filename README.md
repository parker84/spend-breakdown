# Spend Breakdown

A Streamlit dashboard to visualize and categorize your spending across multiple accounts (credit cards, chequing accounts).

## Features

- **Multi-account support**: TD Visa, Amex credit cards, and chequing accounts
- **Automatic categorization**: Transactions are classified into categories like groceries, eating out, coffee, travel, etc.
- **Interactive dashboard**: Monthly trends, category breakdowns, and filterable transaction tables
- **Customizable**: Add your own keywords to improve classification accuracy

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd spend-breakdown
   ```

2. Install dependencies with uv:
   ```bash
   uv sync
   ```

## Adding Your Data

### TD Visa Credit Card

1. Export your account activity CSV files from TD
2. Place them in `data/raw/credit_card/`
3. Files should be named like `Account Activity - Aug 2025.csv`

### Amex Credit Cards

1. Export your account activity as XLS from Amex
2. Place the XLS file in `data/raw/amex_credit_card/`
3. Convert to CSV by running the conversion script (see below)

### Chequing Accounts

1. Export your account activity CSV from your bank
2. Place in `data/raw/chequings/`

## Running the App

### Step 1: Process Raw Data

Convert and combine raw data files:

```bash
uv run python make_dataset.py
```

### Step 2: Classify Transactions

Categorize all transactions:

```bash
uv run python classify_transactions.py
```

### Step 3: Launch Dashboard

Start the Streamlit app:

```bash
uv run streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

## Customizing Categories

To improve classification accuracy, edit `classify_transactions.py`:

1. Find the appropriate category dictionary (e.g., `AMEX_CATEGORIES`)
2. Add keywords to match your transaction descriptions
3. Re-run classification: `uv run python classify_transactions.py`

### Example

```python
"groceries": [
    "METRO", "FARM BOY", "LOBLAWS",
    "YOUR_LOCAL_STORE"  # Add your store here
],
```

## Project Structure

```
spend-breakdown/
├── app.py                    # Streamlit dashboard
├── make_dataset.py           # Data processing script
├── classify_transactions.py  # Transaction categorization
├── data/
│   ├── raw/                  # Raw bank exports
│   │   ├── credit_card/      # TD Visa CSVs
│   │   ├── amex_credit_card/ # Amex XLS/CSV files
│   │   └── chequings/        # Chequing account CSVs
│   └── processed/            # Processed & classified data
├── pyproject.toml            # Project dependencies
└── README.md
```

## Categories

### Credit Card Categories
- groceries, beer_liquor, coffee, transportation, subscriptions
- eating_out, entertainment, utilities, goods_gifts, ordering_in
- donations, travel, pet, beauty_lifestyle, home

### Chequing Categories
- mortgage, housing, insurance, telecom, credit_card_payment
- transfers, loans, investments, bank_fees, e_transfers
- cash_withdrawal, income, eating_out

## License

See [LICENSE](LICENSE) for details.
