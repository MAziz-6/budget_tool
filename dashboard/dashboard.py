import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import io
import zipfile

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="bud.get",      # <--- This puts "bud.get" on the browser tab!
    page_icon="💸",            # <--- This puts a money bag icon next to it
    layout="wide"
)

# --- 1. Load Data ---
@st.cache_data
def load_data():
    # Try finding the file in parent or current directory
    try:
        df = pd.read_csv('../master_budget.csv')
    except FileNotFoundError:
        try:
            df = pd.read_csv('master_budget.csv')
        except FileNotFoundError:
            return pd.DataFrame() # Return empty if not found
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

if df.empty:
    st.error("⚠️ Data file not found. Please run 'main.py' first to generate your budget.")
    st.stop()

# --- 2. Sidebar Filters ---
st.sidebar.header("Filter Your Data")

# Helper: Get Min/Max dates
min_date = df['date'].min().date()
max_date = df['date'].max().date()

# Session State for Date Picker
if 'date_range' not in st.session_state:
    st.session_state['date_range'] = (min_date, max_date)

def set_this_month():
    today = pd.Timestamp.now().date()
    start = today.replace(day=1)
    end = (pd.Timestamp(start) + pd.offsets.MonthEnd(0)).date()
    # Clip to available data range
    st.session_state['date_range'] = (max(start, min_date), min(end, max_date))

st.sidebar.button("📅 Focus on This Month", on_click=set_this_month)

start_date, end_date = st.sidebar.date_input(
    "Select Date Range", 
    min_value=min_date, 
    max_value=max_date,
    key='date_range'
)

# Categories
categories = sorted(df['category'].dropna().unique().tolist())
default_exclude = ['Income/Payroll', 'Transfer to Savings', 'Loan/Credit Card Payment', 'Transfers', 'Transfers/P2P']
# Only use defaults that actually exist in the data
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

# TAB 2: DEEP DIVE
with tab2:
    st.header("📂 Account Analysis")
    # Use full DF for list so 'Costco' always shows up
    accts = sorted(df['Account'].dropna().unique().tolist())
    sel_acct = st.selectbox("Select Account", accts)
    
    # Filter based on selection AND date range
    acct_df = filtered_df[(filtered_df['Account'] == sel_acct) & (filtered_df['amount'] < 0)]
    
    if not acct_df.empty:
        total = abs(acct_df['amount'].sum())
        count = len(acct_df)
        avg = total / count
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Spent", f"${total:,.2f}")
        c2.metric("Transactions", count)
        c3.metric("Avg Transaction", f"${avg:,.2f}")
        
        c_chart, c_data = st.columns([2,1])
        with c_chart:
            st.plotly_chart(px.bar(acct_df.groupby('category')['amount'].sum().abs().reset_index(), x='category', y='amount', text_auto='.2s'), use_container_width=True)
        with c_data:
            st.dataframe(acct_df[['date', 'description', 'amount', 'category']].sort_values('date', ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info(f"No spending found for {sel_acct} in this date range.")

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