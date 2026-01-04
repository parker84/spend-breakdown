# Spend Breakdown

A Streamlit dashboard to visualize and categorize your spending across multiple accounts (credit cards, chequing accounts) with keyword-based transaction classification.

## Features

- **Multi-account support**: TD Visa credit cards, TD chequing accounts, and Amex credit cards
- **Keyword-based classification**: Transactions are categorized using comprehensive keyword matching
- **Unified categories**: 25+ spending categories across all account types (groceries, eating out, coffee, travel, subscriptions, etc.)
- **Interactive dashboard**: Monthly spending trends, category breakdowns, and filterable transaction tables
- **Combined view**: View all accounts together or individually
- **Easy upload**: Drag-and-drop file upload directly in the UI—no manual file placement needed
- **Smart deduplication**: Automatic removal of duplicate transactions when combining multiple statements
- **Advanced settings**: Edit category definitions and re-classify transactions on demand

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

## Running the App

Start the Streamlit dashboard:

```bash
uv run streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

## Adding Accounts

### Through the UI (Recommended)

1. Launch the dashboard
2. Click the **"+ Add Account"** button
3. Select your account type:
   - **TD Credit Card** - Upload multiple monthly CSV statements
   - **TD Chequing** - Upload CSV export from TD
   - **Amex Credit Card** - Upload XLS/XLSX export from Amex
4. Enter an account name
5. Click "Process & Add" and watch the progress bar as transactions are classified

### Supported File Formats

| Account Type | File Format | Notes |
|--------------|-------------|-------|
| TD Credit Card | CSV (multiple) | Upload multiple monthly statements; auto-deduped |
| TD Chequing | CSV | Standard TD account activity export |
| Amex Credit Card | XLS, XLSX | Download "Excel" format from Amex online |

## Dashboard Features

### Account Selector
- Switch between individual accounts or view "All Accounts Combined"
- Date range filter to focus on specific periods

### Spending Overview
- **Total Spending**: Sum of all debits in the selected period
- **Monthly Trend**: Line chart showing spending over time
- **Category Breakdown**: Pie chart of spending by category

### Category Trends
- Individual line charts for each spending category
- Shows monthly spending trends with all months included (even if $0)

### Transaction Table
- Searchable and sortable list of all transactions
- Shows date, description, amount, and category

## Categories

All account types share a unified category system:

**Everyday Spending**
- `groceries` - Food and household supplies from grocery stores
- `eating_out` - Restaurants, cafes, fast food, prepared meals
- `coffee` - Coffee shops and cafes
- `ordering_in` - Food delivery services (UberEats, DoorDash)
- `beer_liquor` - Alcohol purchases

**Living Expenses**
- `mortgage` - Mortgage payments
- `housing` - Rent, condo fees, utilities (gas, hydro)
- `insurance` - Home, car, health, pet insurance
- `telecom` - Phone, internet, cable bills

**Transportation & Travel**
- `transportation` - Transit, rideshare, gas, parking
- `travel` - Flights, hotels, travel expenses

**Shopping & Lifestyle**
- `goods_gifts` - Clothing, electronics, home goods, gifts
- `beauty_lifestyle` - Salons, spas, cosmetics
- `entertainment` - Movies, concerts, events
- `subscriptions` - Streaming, software, memberships
- `pet` - Pet supplies and vet visits
- `home` - Home maintenance, repairs, decor

**Financial**
- `credit_card_payment` - Payments to credit cards
- `transfers` - Internal account transfers
- `e_transfers` - Interac e-Transfers
- `investments` - TFSA, RRSP, stock purchases
- `loans` - Loan payments
- `bank_fees` - Account fees, transaction fees
- `cash_withdrawal` - ATM withdrawals

**Other**
- `donations` - Charitable contributions
- `income` - Salary, refunds, payments received
- `utilities` - Utility bills (hydro, gas, water)

## Project Structure

```
spend-breakdown/
├── app.py                    # Streamlit dashboard (main application)
├── make_dataset.py           # Legacy data processing script
├── classify_transactions.py  # Legacy classification script
├── dedupe_kennedy_amex.py    # One-off deduplication script
├── data/
│   ├── raw/                  # Raw bank exports (for legacy workflow)
│   │   ├── credit_card/      # TD Visa CSVs
│   │   ├── amex_credit_card/ # Amex XLS/CSV files
│   │   └── chequings/        # Chequing account CSVs
│   ├── processed/            # Processed & classified data
│   ├── user_uploads/         # Uploaded files from the UI
│   ├── user_accounts.json    # Account configuration
│   └── user_categories.json  # Custom user-defined categories
├── pyproject.toml            # Project dependencies
└── README.md
```

## Keyword Classification

Transactions are classified using comprehensive keyword matching:

1. Each transaction description is checked against category keywords
2. The first matching category is assigned
3. Categories are checked in a specific order to ensure correct matching (e.g., "ordering_in" before "transportation" so "UBER CANADA/UBEREATS" matches food delivery, not rideshare)
4. Unmatched transactions are labeled as "uncategorized"

### Classification Priority

Keyword order matters for accurate classification. For example:
- `UBER CANADA/UBEREATS` → `ordering_in` (matched first due to "UBEREATS" keyword)
- `UBER` → `transportation` (generic Uber matches rideshare)

## Customizing Categories

### Through the UI

1. Open the sidebar
2. Under **Settings**, click **📋 Category Definitions**
3. Edit the JSON to add/modify categories and keywords
4. Click **Save Categories**
5. Click **🔄 Re-classify** → **Re-classify All Transactions** to apply changes

### In Code

Edit the category dictionaries in `app.py`:

```python
AMEX_CATEGORIES = {
    "groceries": [
        "METRO", "FARM BOY", "LOBLAWS", "YOUR_NEW_STORE"
    ],
    # ... more categories
}
```

The app merges keywords from three source dictionaries:
- `TD_CREDIT_CARD_CATEGORIES`
- `TD_CHEQUING_CATEGORIES`
- `AMEX_CATEGORIES`

## Troubleshooting

### "No spending transactions found"
- Ensure your file is in the correct format for the selected account type
- Check that the file contains transaction data (not just headers)

### Classification seems incorrect
- Add more specific keywords via **Settings** → **Category Definitions**
- Check keyword order—more specific keywords should come first
- Use **Re-classify All Transactions** after making changes

### Duplicate transactions
- TD Credit Card uploads are automatically deduplicated
- For manual deduplication, see `dedupe_kennedy_amex.py` as an example

### Categories missing in combined view
- Ensure all accounts are using the same unified category system
- Re-classify accounts after updating category definitions

## License

See [LICENSE](LICENSE) for details.
