import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import io
import zipfile

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="bud.get",
    page_icon="💸",
    layout="wide"
)

# --- 1. Load Data ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('../master_budget.csv')
    except FileNotFoundError:
        try:
            df = pd.read_csv('master_budget.csv')
        except FileNotFoundError:
            return pd.DataFrame()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

if df.empty:
    st.error("⚠️ Data file not found. Please run the app next to your 'master_budget.csv'.")
    st.stop()

# --- 2. Sidebar Filters ---
st.sidebar.header("Filter Your Data")

min_date = df['date'].min().date()
max_date = df['date'].max().date()

if 'date_range' not in st.session_state:
    st.session_state['date_range'] = (min_date, max_date)

def set_this_month():
    today = pd.Timestamp.now().date()
    start = today.replace(day=1)
    end = (pd.Timestamp(start) + pd.offsets.MonthEnd(0)).date()
    st.session_state['date_range'] = (max(start, min_date), min(end, max_date))

st.sidebar.button("📅 Focus on This Month", on_click=set_this_month)

start_date, end_date = st.sidebar.date_input(
    "Select Date Range", 
    min_value=min_date, 
    max_value=max_date,
    key='date_range'
)

categories = sorted(df['category'].dropna().unique().tolist())
default_exclude = ['Income/Payroll', 'Transfer to Savings', 'Loan/Credit Card Payment', 'Transfers', 'Transfers/P2P']
default_exclude = [c for c in default_exclude if c in categories]

exclude_cats = st.sidebar.multiselect("Exclude Categories", options=categories, default=default_exclude)

# Apply Masks
mask = (
    (df['date'].dt.date >= start_date) & 
    (df['date'].dt.date <= end_date) & 
    (~df['category'].isin(exclude_cats))
)
filtered_df = df[mask]
income_df = filtered_df[filtered_df['amount'] > 0]
spend_df = filtered_df[filtered_df['amount'] < 0]

st.title("💸 bud.get")

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📂 Account Deep Dive", "💡 Savings Insights", "📤 Exports"])

# TAB 1: OVERVIEW
with tab1:
    tot_inc = income_df['amount'].sum()
    tot_spd = abs(spend_df['amount'].sum())
    savings = tot_inc - tot_spd
    rate = (savings / tot_inc * 100) if tot_inc > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Income", f"${tot_inc:,.2f}")
    c2.metric("Expenses", f"${tot_spd:,.2f}")
    c3.metric("Net Savings", f"${savings:,.2f}")
    c4.metric("Savings Rate", f"{rate:.1f}%")
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Spending by Category")
        cat_grp = spend_df.groupby('category')['amount'].sum().abs().reset_index().sort_values('amount', ascending=False)
        st.plotly_chart(px.bar(cat_grp, x='category', y='amount', color='category', text_auto='.2s'), use_container_width=True)
    with c2:
        st.subheader("Fixed vs Variable")
        rec_grp = spend_df.groupby('Is_Recurring')['amount'].sum().abs().reset_index()
        rec_grp['Label'] = rec_grp['Is_Recurring'].map({True: 'Fixed / Recurring', False: 'Discretionary'})
        st.plotly_chart(px.pie(rec_grp, values='amount', names='Label', hole=0.4), use_container_width=True)

# TAB 2: ACCOUNT DEEP DIVE
with tab2:
    st.header("📂 Analyze Specific Folders")
    
    account_list = sorted(df['Account'].dropna().unique().tolist())
    selected_account = st.selectbox("Select an Account / Source:", account_list)
    
    acct_spend = filtered_df[
        (filtered_df['Account'] == selected_account) & 
        (filtered_df['amount'] < 0)
    ]
    
    # --- Main Analysis UI ---
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
        st.info(f"No spending found for '{selected_account}' in the current view.")

    # --- Collapsed Debugger ---
    st.markdown("---")
    with st.expander("🛠️ Developer Tools / Debugger"):
        st.write(f"**Selected Account:** `{selected_account}`")
        
        debug_df = df[df['Account'] == selected_account]
        st.write(f"Total Rows in CSV: `{len(debug_df)}`")
        
        date_filtered = debug_df[
            (debug_df['date'].dt.date >= start_date) & 
            (debug_df['date'].dt.date <= end_date)
        ]
        st.write(f"Rows in Date Range: `{len(date_filtered)}`")
        
        neg_tx = date_filtered[date_filtered['amount'] < 0]
        st.write(f"Spending Rows (Negative): `{len(neg_tx)}`")

        if len(date_filtered) > 0 and len(neg_tx) == 0:
            st.error("🚨 Potential Issue: Transactions found but none are negative (spending).")
            st.dataframe(date_filtered.head())
        else:
            st.success("✅ Data checks out: Spending transactions detected.")

# TAB 3: SAVINGS
with tab3:
    st.header("💡 Savings Detective")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Recurring Subscriptions")
        subs = spend_df[(spend_df['Is_Recurring']) & (spend_df['category'].isin(['Subscriptions/Streaming', 'Gym/Health']))]
        if not subs.empty:
            st.metric("Total Cost", f"${abs(subs['amount'].sum()):,.2f}")
            st.dataframe(subs.groupby('description')['amount'].sum().abs().reset_index().sort_values('amount', ascending=False), use_container_width=True, hide_index=True)
        else:
            st.success("No subscriptions found.")
            
    with c2:
        st.subheader("Dining & Coffee")
        dining = spend_df[spend_df['category'].isin(['Dining/Restaurants', 'Coffee', 'Alcohol/Bars'])]
        val = abs(dining['amount'].sum())
        st.metric("Total Spent", f"${val:,.2f}")
        if val > 0: st.warning(f"That's ${val:,.2f} you could potentially reduce.")

    st.markdown("---")
    st.subheader("🐳 Top 10 Largest Purchases")
    top = spend_df.sort_values('amount', ascending=True).head(10)[['date','description','amount','category','Account']]
    top['amount'] = top['amount'].abs()
    st.dataframe(top.style.format({'amount': '${:,.2f}'}), use_container_width=True, hide_index=True)

# TAB 4: EXPORTS
with tab4:
    st.header("📤 Export Data")
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Actual Budget Zip")
        if st.button("Generate Zip"):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as zf:
                for acc in df['Account'].unique():
                    sub = df[df['Account'] == acc].copy()
                    exp = pd.DataFrame({
                        'Date': sub['date'].dt.strftime('%Y-%m-%d'),
                        'Payee': sub['description'],
                        'Category': sub['category'],
                        'Notes': "Imported from bud.get",
                        'Amount': sub['amount']
                    })
                    zf.writestr(f"Import_{acc}.csv", exp.to_csv(index=False))
            st.download_button("Download Zip", buf.getvalue(), "Actual_Budget_Imports.zip", "application/zip")
            
    with c2:
        st.subheader("Master Backup")
        st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8'), f"Budget_Backup_{datetime.date.today()}.csv", "text/csv")