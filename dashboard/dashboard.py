import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# Page Setup
st.set_page_config(page_title="Budget Dashboard", layout="wide")

# --- 1. Load Data ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('../master_budget.csv')
    except FileNotFoundError:
        df = pd.read_csv('master_budget.csv')
    
    df['date'] = pd.to_datetime(df['date'])
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Data file not found. Please run main.py first.")
    st.stop()

# --- 2. Sidebar Filters ---
st.sidebar.header("Filter Your Data")

# Helper: Get Min/Max dates from data
min_date = df['date'].min().date()
max_date = df['date'].max().date()

# --- Session State Logic ---
if 'date_range' not in st.session_state:
    st.session_state['date_range'] = (min_date, max_date)

def set_this_month():
    """Sets the date_range state to the current calendar month."""
    today = pd.Timestamp.now().date()
    start_of_month = today.replace(day=1)
    end_of_month = (pd.Timestamp(start_of_month) + pd.offsets.MonthEnd(0)).date()
    
    final_start = max(start_of_month, min_date)
    final_end = min(end_of_month, max_date)
    
    if final_start > final_end:
        final_start, final_end = min_date, max_date
        
    st.session_state['date_range'] = (final_start, final_end)

st.sidebar.button("📅 Focus on This Month", on_click=set_this_month)

start_date, end_date = st.sidebar.date_input(
    "Select Date Range", 
    min_value=min_date,
    max_value=max_date,
    key='date_range'
)

# Global Exclusions
categories = sorted(df['category'].dropna().unique().tolist())
default_exclude = ['Income/Payroll', 'Transfer to Savings', 'Loan/Credit Card Payment', 'Transfers', 'Transfers/P2P']
default_exclude = [c for c in default_exclude if c in categories]

exclude_cats = st.sidebar.multiselect(
    "Exclude Categories", 
    options=categories, 
    default=default_exclude
)

# Apply Filters
mask = (
    (df['date'].dt.date >= start_date) & 
    (df['date'].dt.date <= end_date) & 
    (~df['category'].isin(exclude_cats))
)
filtered_df = df[mask]

# Separate Income vs Spend
income_df = filtered_df[filtered_df['amount'] > 0]
spend_df = filtered_df[filtered_df['amount'] < 0]

st.title("💸 Personal Budget Dashboard")

# --- TABS SETUP ---
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📂 Account Deep Dive", "💡 Savings Insights"])

# ==============================================================================
# TAB 1: OVERVIEW
# ==============================================================================
with tab1:
    total_income = income_df['amount'].sum()
    total_spend = abs(spend_df['amount'].sum())
    net_savings = total_income - total_spend
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Income", f"${total_income:,.2f}")
    col2.metric("Total Expenses", f"${total_spend:,.2f}")
    col3.metric("Net Savings", f"${net_savings:,.2f}", delta_color="normal")
    col4.metric("Savings Rate", f"{savings_rate:.1f}%")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Spending by Category")
        cat_spend = spend_df.groupby('category')['amount'].sum().abs().reset_index()
        cat_spend = cat_spend.sort_values(by='amount', ascending=False)
        
        fig_cat = px.bar(
            cat_spend, 
            x='category', y='amount', color='category', 
            text_auto='.2s', title="Where is the money going?"
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with col2:
        st.subheader("🔄 Recurring vs One-Off")
        rec_spend = spend_df.groupby('Is_Recurring')['amount'].sum().abs().reset_index()
        rec_spend['Label'] = rec_spend['Is_Recurring'].map({True: 'Fixed / Recurring', False: 'Discretionary'})
        
        fig_rec = px.pie(
            rec_spend, values='amount', names='Label', 
            title="Fixed Costs vs Variable Spending", hole=0.4
        )
        st.plotly_chart(fig_rec, use_container_width=True)

    st.subheader("📅 Daily Spending Trend")
    daily_spend = spend_df.set_index('date').resample('D')['amount'].sum().abs().reset_index()
    fig_line = px.line(daily_spend, x='date', y='amount')
    st.plotly_chart(fig_line, use_container_width=True)

# ==============================================================================
# TAB 2: ACCOUNT DEEP DIVE
# ==============================================================================
with tab2:
    st.header("📂 Analyze Specific Folders")
    
    # FIX: Use 'df' (unfiltered) so 'Costco' appears even if date range is currently excluding it
    account_list = sorted(df['Account'].dropna().unique().tolist())
    selected_account = st.selectbox("Select an Account / Source:", account_list)
    
    acct_df = filtered_df[filtered_df['Account'] == selected_account]
    acct_spend = acct_df[acct_df['amount'] < 0]
    
    if not acct_spend.empty:
        acct_total = abs(acct_spend['amount'].sum())
        acct_tx_count = len(acct_spend)
        avg_tx = acct_total / acct_tx_count
        
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Total Spent in '{selected_account}'", f"${acct_total:,.2f}")
        c2.metric("Total Transactions", acct_tx_count)
        c3.metric("Average Purchase", f"${avg_tx:,.2f}")
        
        col_chart, col_data = st.columns([2, 1])
        with col_chart:
            acct_cat_spend = acct_spend.groupby('category')['amount'].sum().abs().reset_index().sort_values('amount', ascending=False)
            fig_acct = px.bar(acct_cat_spend, x='category', y='amount', color='category', text_auto='.2s')
            st.plotly_chart(fig_acct, use_container_width=True)
            
        with col_data:
            st.dataframe(acct_spend[['date', 'description', 'amount', 'category']].sort_values('date', ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info(f"No spending found for '{selected_account}' in the selected date range.")

# ==============================================================================
# TAB 3: SAVINGS INSIGHTS
# ==============================================================================
with tab3:
    st.header("💡 Savings Detective")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🕵️ Recurring Subscriptions")
        
        # Filter for Recurring + (Streaming OR Gym)
        subs = spend_df[(spend_df['Is_Recurring'] == True) & (spend_df['category'].isin(['Subscriptions/Streaming', 'Gym/Health']))]
        
        if not subs.empty:
            # NEW: Calculate and show the Total
            total_subs = abs(subs['amount'].sum())
            st.metric("Total Subscriptions (Selected Period)", f"${total_subs:,.2f}")
            
            subs_grouped = subs.groupby('description')['amount'].sum().abs().reset_index().sort_values('amount', ascending=False)
            st.dataframe(subs_grouped, use_container_width=True, hide_index=True)
        else:
            st.success("No subscriptions found!")
            
    with col2:
        st.subheader("☕ The 'Latte Factor'")
        dining_spend = spend_df[spend_df['category'].isin(['Dining/Restaurants', 'Coffee', 'Alcohol/Bars'])]
        total_dining = abs(dining_spend['amount'].sum())
        st.metric("Total Dining & Coffee", f"${total_dining:,.2f}")
        if total_dining > 0:
            st.warning(f"You spent ${total_dining:,.2f} on dining/coffee.")

    st.markdown("---")
    st.subheader("🐳 The 'Whales' (Largest Single Purchases)")
    top_purchases = spend_df.sort_values(by='amount', ascending=True).head(10)
    display_top = top_purchases[['date', 'description', 'amount', 'category', 'Account']].copy()
    display_top['amount'] = display_top['amount'].abs()
    st.dataframe(display_top.style.format({"amount": "${:,.2f}"}), use_container_width=True, hide_index=True)