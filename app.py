import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import datetime

# Page config
st.set_page_config(
    page_title="Spend Breakdown",
    page_icon="💰",
    layout="wide"
)

# Custom CSS for styling
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
    
    div[data-testid="stHorizontalBlock"] > div {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 12px;
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Account configurations
ACCOUNTS = {
    "combined_all": {
        "name": "📊 All Accounts Combined",
        "is_combined": True,
        "include_chequing": True,
    },
    "combined_credit_cards": {
        "name": "💳 Combined Credit Cards",
        "is_combined": True,
        "include_chequing": False,
    },
    "td_visa_credit_card": {
        "name": "TD Visa Credit Card",
        "date_format": "%m/%d/%Y",
        "filter_june": True,  # Filter out June for credit card (incomplete data)
        "debit_column": "debit",  # Spending is in debit column
        "filter_payments": True,  # Filter out PREAUTHORIZED PAYMENT
    },
    "brydon_amex": {
        "name": "Brydon Amex",
        "date_format": "mixed",  # Mixed formats: "29 Dec. 2025" and "21 May 2025"
        "filter_june": False,  # Full year data
        "debit_column": "debit",
        "filter_payments": False,
    },
    "kennedy_amex": {
        "name": "Kennedy Amex",
        "date_format": "mixed",  # Mixed formats: "29 Dec. 2025" and "21 May 2025"
        "filter_june": False,  # Full year data
        "debit_column": "debit",
        "filter_payments": False,
    },
    "brydon_chequings": {
        "name": "Brydon Chequings",
        "date_format": "%Y-%m-%d",
        "filter_june": False,
        "debit_column": "debit",  # Withdrawals are in debit column
        "filter_payments": False,
    },
    "joint_chequings": {
        "name": "Joint Chequings",
        "date_format": "%Y-%m-%d",
        "filter_june": False,
        "debit_column": "debit",
        "filter_payments": False,
    },
}

# Color palettes for different account types
CREDIT_CARD_COLORS = {
    "groceries": "#00d4aa",
    "beer_liquor": "#ff6b6b",
    "coffee": "#c9a227",
    "transportation": "#4ecdc4",
    "subscriptions": "#a855f7",
    "eating_out": "#ff8c42",
    "entertainment": "#06b6d4",
    "utilities": "#64748b",
    "goods_gifts": "#ec4899",
    "ordering_in": "#f59e0b",
    "donations": "#22c55e",
    "other": "#6b7280"
}

CHEQUING_COLORS = {
    "mortgage": "#ff6b6b",
    "housing": "#00d4aa",
    "insurance": "#a855f7",
    "telecom": "#4ecdc4",
    "credit_card_payment": "#ec4899",
    "transfers": "#64748b",
    "loans": "#f59e0b",
    "investments": "#22c55e",
    "bank_fees": "#6b7280",
    "e_transfers": "#06b6d4",
    "cash_withdrawal": "#c9a227",
    "income": "#10b981",
    "eating_out": "#ff8c42",
    "other": "#6b7280"
}

AMEX_COLORS = {
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
    "other": "#6b7280"
}

# Combined view uses all colors from all palettes
COMBINED_COLORS = {
    **CREDIT_CARD_COLORS,
    **AMEX_COLORS,
    **CHEQUING_COLORS,
}


@st.cache_data
def load_single_account(account_key: str):
    """Load and prepare the classified transactions data for a single account."""
    config = ACCOUNTS[account_key]
    file_path = Path(f"data/processed/{account_key}_classified.csv")
    
    df = pd.read_csv(file_path)
    
    # Filter out PREAUTHORIZED PAYMENT for credit card
    if config.get("filter_payments", False):
        df = df[~df["description"].str.contains("PREAUTHORIZED PAYMENT", case=False, na=False)]
    
    # Parse dates
    date_format = config["date_format"]
    if date_format == "mixed":
        # For Amex: mixed formats like "29 Dec. 2025" and "21 May 2025"
        df["date"] = pd.to_datetime(df["date"], format="mixed", dayfirst=True)
    else:
        df["date"] = pd.to_datetime(df["date"], format=date_format)
    
    # Filter out June for credit card (incomplete data)
    if config.get("filter_june", False):
        df = df[df["date"].dt.month != 6]
    
    df["month"] = df["date"].dt.to_period("M")
    df["month_str"] = df["date"].dt.strftime("%b %Y")
    df["month_order"] = df["date"].dt.to_period("M").astype(str)
    
    # Fill NaN debits with 0 for calculations
    df["debit"] = df["debit"].fillna(0)
    df["credit"] = df["credit"].fillna(0)
    
    # Add account name for combined view
    df["account_name"] = config["name"]
    
    return df


@st.cache_data
def load_combined_data(include_chequing: bool = False):
    """Load and combine data from multiple accounts."""
    credit_accounts = ["td_visa_credit_card", "brydon_amex", "kennedy_amex"]
    chequing_accounts = ["brydon_chequings", "joint_chequings"]
    
    accounts_to_load = credit_accounts.copy()
    if include_chequing:
        accounts_to_load.extend(chequing_accounts)
    
    dfs = []
    for account_key in accounts_to_load:
        if account_key in ACCOUNTS:
            df = load_single_account(account_key)
            dfs.append(df)
    
    combined = pd.concat(dfs, ignore_index=True)
    return combined


@st.cache_data
def load_data(account_key: str):
    """Load data for a specific account or combined view."""
    if account_key == "combined_all":
        return load_combined_data(include_chequing=True)
    elif account_key == "combined_credit_cards":
        return load_combined_data(include_chequing=False)
    return load_single_account(account_key)


def get_colors(account_key: str) -> dict:
    """Get the color palette for the account type."""
    if account_key in ["combined_all", "combined_credit_cards"]:
        return COMBINED_COLORS
    elif account_key == "td_visa_credit_card":
        return CREDIT_CARD_COLORS
    elif account_key in ["brydon_amex", "kennedy_amex"]:
        return AMEX_COLORS
    return CHEQUING_COLORS


def main():
    st.title("💰 Spend Breakdown Dashboard")
    
    # Account selector
    account_key = st.selectbox(
        "Select Account",
        options=list(ACCOUNTS.keys()),
        format_func=lambda x: ACCOUNTS[x]["name"],
        index=0
    )
    
    # Load data for selected account
    df = load_data(account_key)
    colors = get_colors(account_key)
    
    # Sidebar date filters
    with st.sidebar:
        st.header("📅 Date Filters")
        
        # Get min/max dates from data
        min_date = df["date"].min().date()
        max_date = df["date"].max().date()
        
        # Default start date: July for TD Visa and Combined views (June is incomplete), January for others
        if account_key in ["td_visa_credit_card", "combined_all", "combined_credit_cards"]:
            # Start from July 1st (after incomplete June)
            default_start = datetime.date(2025, 7, 1)
            if default_start < min_date:
                default_start = min_date
        else:
            # Start from January 1st
            default_start = datetime.date(2025, 1, 1)
            if default_start < min_date:
                default_start = min_date
        
        start_date = st.date_input(
            "Start Date",
            value=default_start,
            min_value=min_date,
            max_value=max_date
        )
        
        end_date = st.date_input(
            "End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )
        
        st.markdown("---")
    
    # Apply date filters
    df = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)]
    
    st.markdown("---")
    
    # Only include debit transactions (spending/withdrawals)
    spending_df = df[df["debit"] > 0].copy()
    
    # For chequing accounts (or combined views that include them), exclude income and transfers
    if account_key in ["brydon_chequings", "joint_chequings"]:
        exclude_categories = ["income", "transfers", "credit_card_payment"]
        spending_df = spending_df[~spending_df["category"].isin(exclude_categories)]
    elif account_key == "combined_all":
        # For combined all, only exclude these categories from chequing account transactions
        chequing_mask = spending_df["account"].isin(["brydon_chequings", "joint_chequings"])
        exclude_categories = ["income", "transfers", "credit_card_payment"]
        exclude_mask = chequing_mask & spending_df["category"].isin(exclude_categories)
        spending_df = spending_df[~exclude_mask]
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_spend = spending_df["debit"].sum()
    num_transactions = len(spending_df)
    avg_transaction = spending_df["debit"].mean() if num_transactions > 0 else 0
    num_months = spending_df["month"].nunique()
    
    with col1:
        st.metric("Total Spending", f"${total_spend:,.2f}")
    with col2:
        st.metric("Transactions", f"{num_transactions:,}")
    with col3:
        st.metric("Avg Transaction", f"${avg_transaction:.2f}")
    with col4:
        st.metric("Monthly Avg", f"${total_spend / max(num_months, 1):,.2f}")
    
    st.markdown("---")
    
    # Row 1: Monthly spend line chart + Donut chart
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📈 Monthly Spending Trend")
        
        monthly_spend = spending_df.groupby("month_order")["debit"].sum().reset_index()
        monthly_spend = monthly_spend.sort_values("month_order")
        monthly_spend["month_label"] = pd.to_datetime(monthly_spend["month_order"]).dt.strftime("%b %Y")
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=monthly_spend["month_label"],
            y=monthly_spend["debit"],
            mode="lines+markers",
            line=dict(color="#00d4aa", width=3),
            marker=dict(size=10, color="#00d4aa"),
            fill="tozeroy",
            fillcolor="rgba(0, 212, 170, 0.1)",
            hovertemplate="<b>%{x}</b><br>$%{y:,.2f}<extra></extra>"
        ))
        
        fig_line.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#8892b0"),
            xaxis=dict(
                showgrid=False,
                tickfont=dict(color="#8892b0")
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(255,255,255,0.05)",
                tickfont=dict(color="#8892b0"),
                tickprefix="$"
            ),
            margin=dict(l=0, r=0, t=20, b=0),
            height=350
        )
        
        st.plotly_chart(fig_line, use_container_width=True)
    
    with col_right:
        st.subheader("🍩 Spending by Category")
        
        category_spend = spending_df.groupby("category")["debit"].sum().reset_index()
        category_spend = category_spend.sort_values("debit", ascending=False)
        
        chart_colors = [colors.get(cat, "#6b7280") for cat in category_spend["category"]]
        
        fig_donut = go.Figure(data=[go.Pie(
            labels=category_spend["category"],
            values=category_spend["debit"],
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
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5,
                font=dict(size=10, color="#8892b0")
            ),
            margin=dict(l=0, r=0, t=20, b=80),
            height=350
        )
        
        st.plotly_chart(fig_donut, use_container_width=True)
    
    st.markdown("---")
    
    # Row 2: Category trends over time
    st.subheader("📊 Spending by Category Over Time")
    
    # Create monthly spend by category
    monthly_category = spending_df.groupby(["month_order", "category"])["debit"].sum().reset_index()
    monthly_category = monthly_category.sort_values("month_order")
    monthly_category["month_label"] = pd.to_datetime(monthly_category["month_order"]).dt.strftime("%b %Y")
    
    # Get unique categories sorted by total spend
    categories_sorted = spending_df.groupby("category")["debit"].sum().sort_values(ascending=False).index.tolist()
    
    # Create a 3-column grid for category charts
    cols_per_row = 3
    for i in range(0, len(categories_sorted), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(categories_sorted):
                category = categories_sorted[i + j]
                cat_data = monthly_category[monthly_category["category"] == category]
                
                # Ensure all months are present
                all_months = monthly_category["month_order"].unique()
                cat_data_full = pd.DataFrame({"month_order": all_months})
                cat_data_full = cat_data_full.merge(cat_data[["month_order", "debit"]], on="month_order", how="left")
                cat_data_full["debit"] = cat_data_full["debit"].fillna(0)
                cat_data_full = cat_data_full.sort_values("month_order")
                cat_data_full["month_label"] = pd.to_datetime(cat_data_full["month_order"]).dt.strftime("%b")
                
                total = cat_data["debit"].sum()
                monthly_avg = total / num_months
                
                with col:
                    fig_cat = go.Figure()
                    cat_color = colors.get(category, "#6b7280")
                    
                    # Parse hex color to RGB for fill
                    hex_color = cat_color.lstrip('#')
                    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    
                    fig_cat.add_trace(go.Scatter(
                        x=cat_data_full["month_label"],
                        y=cat_data_full["debit"],
                        mode="lines+markers",
                        line=dict(color=cat_color, width=2),
                        marker=dict(size=6),
                        fill="tozeroy",
                        fillcolor=f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.15)",
                        hovertemplate="$%{y:,.2f}<extra></extra>"
                    ))
                    
                    fig_cat.update_layout(
                        title=dict(
                            text=f"{category.replace('_', ' ').title()}<br><span style='font-size:12px;color:#8892b0'>${total:,.0f} total · ${monthly_avg:,.0f}/mo</span>",
                            font=dict(size=14, color=cat_color),
                            x=0.5
                        ),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="DM Sans", color="#8892b0"),
                        xaxis=dict(showgrid=False, tickfont=dict(size=9, color="#8892b0")),
                        yaxis=dict(
                            showgrid=True,
                            gridcolor="rgba(255,255,255,0.05)",
                            tickfont=dict(size=9, color="#8892b0"),
                            tickprefix="$"
                        ),
                        margin=dict(l=0, r=0, t=50, b=0),
                        height=200
                    )
                    
                    st.plotly_chart(fig_cat, use_container_width=True)
    
    st.markdown("---")
    
    # Row 3: Filterable transactions table
    st.subheader("🔍 Transaction Details")
    
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        selected_categories = st.multiselect(
            "Filter by Category",
            options=sorted(spending_df["category"].unique()),
            default=[]
        )
    
    with col_filter2:
        month_options = spending_df.sort_values("month_order")["month_str"].unique().tolist()
        selected_months = st.multiselect(
            "Filter by Month",
            options=month_options,
            default=[]
        )
    
    # Apply filters
    filtered_df = spending_df.copy()
    
    if selected_categories:
        filtered_df = filtered_df[filtered_df["category"].isin(selected_categories)]
    
    if selected_months:
        filtered_df = filtered_df[filtered_df["month_str"].isin(selected_months)]
    
    # Prepare display dataframe
    if account_key in ["combined_all", "combined_credit_cards"]:
        display_df = filtered_df[["date", "account_name", "description", "debit", "category"]].copy()
        display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
        display_df = display_df.sort_values("date", ascending=False)
        display_df.columns = ["Date", "Account", "Description", "Amount", "Category"]
    else:
        display_df = filtered_df[["date", "description", "debit", "category"]].copy()
        display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
        display_df = display_df.sort_values("date", ascending=False)
        display_df.columns = ["Date", "Description", "Amount", "Category"]
    
    # Show summary for filtered data
    st.markdown(f"**Showing {len(display_df)} transactions** | **Total: ${filtered_df['debit'].sum():,.2f}**")
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        hide_index=True
    )


if __name__ == "__main__":
    main()
