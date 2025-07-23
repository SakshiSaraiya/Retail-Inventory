import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_connection, execute_query
from auth import check_login

st.set_page_config(page_title="📊 Dashboard", layout="wide")
st.markdown("""
    <style>
    body {background-color: #F8FAFC;}
    section[data-testid="stSidebar"] {background-color: #0F172A;}
    [data-testid="stSidebar"] * {color: #fff !important;}
    .kpi-card-home {background: #fff; color: #0F172A; border-radius: 18px; box-shadow: 0 4px 16px rgba(30,41,59,0.10); flex: 1; padding: 1.7rem 1.2rem 1.2rem 1.2rem; display: flex; flex-direction: column; align-items: center; justify-content: center; min-width: 180px; max-width: 300px; margin-bottom: 1.5rem;}
    .kpi-card-home .icon {font-size: 2.2rem; margin-bottom: 0.7rem;}
    .kpi-card-home .label {font-size: 1.1rem; font-weight: 600; margin-bottom: 0.2rem; color: #475569;}
    .kpi-card-home .value {font-size: 2rem; font-weight: 800; color: #0F172A;}
    .card {background: #fff; border-radius: 16px; box-shadow: 0 2px 8px rgba(30,41,59,0.08); padding: 1.5rem 2rem; margin-bottom: 2rem;}
    .alert-card {background: #fee2e2; color: #991b1b; border-radius: 12px; padding: 1rem 1.5rem; font-weight: 600; margin-bottom: 1.2rem;}
    .success-card {background: #dcfce7; color: #166534; border-radius: 12px; padding: 1rem 1.5rem; font-weight: 600; margin-bottom: 1.2rem;}
    .low-stock-table td, .low-stock-table th {padding: 0.5rem 1rem;}
    .low-stock-table th {background: #f1f5f9; color: #0F172A; font-weight: 700;}
    .low-stock-table tr.critical td {color: #b91c1c; font-weight: 700;}
    .low-stock-table tr.low td {color: #f59e42; font-weight: 600;}
    .metric-card-inv {background: #fff; border-radius: 16px; box-shadow: 0 2px 8px rgba(30,41,59,0.08); padding: 1.5rem 2rem; display: flex; flex-direction: column; align-items: center; margin-bottom: 1.5rem;}
    .metric-card-inv .icon {font-size: 2rem; margin-bottom: 0.5rem;}
    .metric-card-inv .label {font-size: 1.1rem; color: #475569; font-weight: 600; margin-bottom: 0.2rem;}
    .metric-card-inv .value {font-size: 2rem; font-weight: 800; color: #0F172A;}
    .metric-card-inv .desc {font-size: 0.98rem; color: #64748B; margin-top: 0.3rem; text-align: center;}
    </style>
""", unsafe_allow_html=True)

# --- Authentication Check ---
check_login()

st.markdown("<h1 style='text-align:center;margin-bottom:0.5rem;'>📊 Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;font-size:1.15rem;color:#475569;margin-bottom:2.5rem;font-weight:500;'>Unified business and finance insights at a glance.</div>", unsafe_allow_html=True)

# --- Load Data ---
conn = get_connection()
products = pd.read_sql("SELECT * FROM Products", conn)
sales = pd.read_sql("SELECT * FROM Sales", conn)
purchases = pd.read_sql("SELECT * FROM Purchases", conn)

# --- KPI Cards ---
total_sales = (sales['quantity_sold'] * sales['selling_price']).sum()
total_products = products.shape[0]
total_expenses = purchases['quantity_purchased'].sum() * purchases['cost_price'].mean() if not purchases.empty else 0
# COGS & Profit
cogs = 0
for _, row in sales.iterrows():
    cost = products.loc[products['product_id'] == row['product_id'], 'cost_price']
    if not cost.empty:
        cogs += row['quantity_sold'] * cost.values[0]
gross_profit = total_sales - cogs
# DIO
purchase_qty = purchases.groupby('product_id')['quantity_purchased'].sum().reset_index(name='total_purchased')
sales_qty = sales.groupby('product_id')['quantity_sold'].sum().reset_index(name='total_sold')
live_stock = pd.merge(products, purchase_qty, on='product_id', how='left')
live_stock = pd.merge(live_stock, sales_qty, on='product_id', how='left')
live_stock['total_purchased'].fillna(0, inplace=True)
live_stock['total_sold'].fillna(0, inplace=True)
live_stock['live_stock'] = live_stock['total_purchased'] - live_stock['total_sold']
live_stock['holding_cost'] = live_stock['live_stock'] * live_stock['cost_price']
avg_inventory = live_stock['live_stock'].mean()
daily_cogs = cogs / 30 if cogs > 0 else 1
DIO = avg_inventory / daily_cogs if daily_cogs else 0

k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(f"""
        <div class='kpi-card-home'>
            <div class='icon'>💰</div>
            <div class='label'>Total Sales</div>
            <div class='value'>₹ {total_sales:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)
with k2:
    st.markdown(f"""
        <div class='kpi-card-home'>
            <div class='icon'>🛒</div>
            <div class='label'>Total Products</div>
            <div class='value'>{total_products}</div>
        </div>
    """, unsafe_allow_html=True)
with k3:
    st.markdown(f"""
        <div class='kpi-card-home'>
            <div class='icon'>📉</div>
            <div class='label'>Total Expenses</div>
            <div class='value'>₹ {total_expenses:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)
k4, k5, k6 = st.columns(3)
with k4:
    st.markdown(f"""
        <div class='kpi-card-home'>
            <div class='icon'>🧾</div>
            <div class='label'>COGS</div>
            <div class='value'>₹ {cogs:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)
with k5:
    st.markdown(f"""
        <div class='kpi-card-home'>
            <div class='icon'>📈</div>
            <div class='label'>Gross Profit</div>
            <div class='value'>₹ {gross_profit:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)
with k6:
    st.markdown(f"""
        <div class='kpi-card-home'>
            <div class='icon'>📦</div>
            <div class='label'>DIO</div>
            <div class='value'>{DIO:.1f} Days</div>
        </div>
    """, unsafe_allow_html=True)

# --- Category-wise Profitability ---
st.markdown("<div class='section-title'>Category-wise Profitability</div>", unsafe_allow_html=True)
merged = pd.merge(sales, products[['product_id', 'NAME', 'category', 'cost_price']], on='product_id', how='left')
merged['Revenue'] = merged['quantity_sold'] * merged['selling_price']
merged['Cost'] = merged['quantity_sold'] * merged['cost_price']
merged['Profit'] = merged['Revenue'] - merged['Cost']
category_profit = merged.groupby('category')[['Revenue', 'Cost', 'Profit']].sum().reset_index()
fig_cat = px.bar(category_profit, x='category', y='Profit', color='category', title="Category-wise Profitability", color_discrete_sequence=px.colors.qualitative.Vivid)
fig_cat.update_layout(
    paper_bgcolor='#fff', plot_bgcolor='#fff', margin=dict(l=20, r=20, t=40, b=20),
    font=dict(size=16, color='#1a2233'),
    xaxis=dict(showgrid=False, title='Category', tickfont=dict(size=15)),
    yaxis=dict(showgrid=False, title='Profit', tickfont=dict(size=15)),
    showlegend=False
)

# --- Interactive Sales Breakdown ---
st.markdown("<div class='section-title'>Sales Breakdown</div>", unsafe_allow_html=True)
num_products = merged['NAME'].nunique()
if num_products <= 3:
    top_n = num_products
else:
    top_n = st.slider("Top N Products by Sales", 3, min(50, num_products), min(5, num_products))
category_sales = (
    merged.groupby('category')
    .apply(lambda x: (x['quantity_sold'] * x['selling_price']).sum())
    .reset_index(name='total_sales')
)
fig_pie = px.pie(category_sales, values='total_sales', names='category', title="Category-wise Sales", color_discrete_sequence=px.colors.qualitative.Set3)
fig_pie.update_traces(textinfo='percent+label')
fig_pie.update_layout(
    showlegend=True, paper_bgcolor='#fff', plot_bgcolor='#fff',
    font=dict(size=16, color='#1a2233'),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(font=dict(size=14)),
)
product_sales = (
    merged.groupby('NAME')
    .apply(lambda x: (x['quantity_sold'] * x['selling_price']).sum())
    .reset_index(name='total_sales')
    .sort_values(by='total_sales', ascending=False)
    .head(top_n)
)
fig_bar = px.bar(product_sales, x='NAME', y='total_sales', title=f"Top {top_n} Products by Sales", color='NAME', color_discrete_sequence=px.colors.qualitative.Prism)
fig_bar.update_layout(
    xaxis_title="", yaxis_title="Sales", paper_bgcolor='#fff', plot_bgcolor='#fff',
    font=dict(size=16, color='#1a2233'),
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(showgrid=False, tickfont=dict(size=15)),
    yaxis=dict(showgrid=False, tickfont=dict(size=15)),
    showlegend=False
)

# --- Supplier Payment Simulation ---
st.markdown("<div class='section-title'>Supplier Payment Simulation</div>", unsafe_allow_html=True)
purchases['outstanding'] = purchases.apply(lambda x: x['quantity_purchased'] * x['cost_price'] if x['payment_status'].lower() == 'pending' else 0, axis=1)
supplier_outstanding = purchases.groupby('vendor_name')['outstanding'].sum().reset_index()
supplier_outstanding = supplier_outstanding[supplier_outstanding['outstanding'] > 0]
if not supplier_outstanding.empty:
    fig_out = px.pie(supplier_outstanding, names='vendor_name', values='outstanding', title='Pending Payments to Vendors', color_discrete_sequence=px.colors.sequential.Plasma)
    fig_out.update_layout(
        paper_bgcolor='#fff', plot_bgcolor='#fff', margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=16, color='#1a2233'),
        legend=dict(font=dict(size=14)),
        showlegend=True
    )
else:
    st.markdown("<div class='success-card'>✅ All supplier payments are cleared.</div>", unsafe_allow_html=True)

# --- Sales & Vendor Analytics Tabs ---
sales_tab, vendor_tab = st.tabs(["📊 Sales Analytics", "🤝 Vendor Analytics"])

with sales_tab:
    st.markdown("<div class='section-title'>Category-wise Profitability</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex;justify-content:center;'><div style='max-width:600px;width:100%;'>", unsafe_allow_html=True)
    st.plotly_chart(fig_cat, use_container_width=True)
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Sales Breakdown</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    col7, col8 = st.columns(2)
    with col7:
        st.markdown("<div style='display:flex;justify-content:center;'><div style='max-width:400px;width:100%;'>", unsafe_allow_html=True)
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div></div>", unsafe_allow_html=True)
    with col8:
        st.markdown("<div style='display:flex;justify-content:center;'><div style='max-width:400px;width:100%;'>", unsafe_allow_html=True)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)

with vendor_tab:
    st.markdown("<div class='section-title'>Supplier Payment Simulation</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    if not supplier_outstanding.empty:
        st.markdown("<div style='display:flex;justify-content:center;'><div style='max-width:600px;width:100%;'>", unsafe_allow_html=True)
        st.plotly_chart(fig_out, use_container_width=True)
        st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='success-card'>✅ All supplier payments are cleared.</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)

# --- Inventory Holding Costs & DIO ---
st.markdown("<div class='section-title'>Inventory Holding Costs & DIO</div>", unsafe_allow_html=True)
col4, col5 = st.columns(2)
with col4:
    st.markdown(f"""
        <div class='metric-card-inv'>
            <div class='icon'>💸</div>
            <div class='label'>Inventory Holding Cost</div>
            <div class='value'>₹ {live_stock['holding_cost'].sum():,.2f}</div>
            <div class='desc'>Total value of unsold inventory currently held.</div>
        </div>
    """, unsafe_allow_html=True)
with col5:
    st.markdown(f"""
        <div class='metric-card-inv'>
            <div class='icon'>⏳</div>
            <div class='label'>Days Inventory Outstanding (DIO)</div>
            <div class='value'>{DIO:.1f} Days</div>
            <div class='desc'>Average days inventory is held before sale.</div>
        </div>
    """, unsafe_allow_html=True)
st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)

# --- Low Stock Alert ---
st.markdown("<div class='section-title'>Low Stock Alerts</div>", unsafe_allow_html=True)
low_stock_df = live_stock[live_stock['live_stock'] <= 5].copy()
if not low_stock_df.empty:
    st.markdown("<div class='alert-card'>⚠️ <b>Some products are low on stock!</b></div>", unsafe_allow_html=True)
    # Add status and action columns
    def status(row):
        if row['live_stock'] < 0:
            return 'Critical'
        else:
            return 'Low'
    low_stock_df['Status'] = low_stock_df.apply(status, axis=1)
    low_stock_df['Action'] = 'Reorder Now'
    st.dataframe(
        low_stock_df[['NAME', 'category', 'live_stock', 'Status', 'Action']]
        .style.applymap(lambda v: 'color: #b91c1c; font-weight:700;' if v == 'Critical' else ('color: #f59e42; font-weight:600;' if v == 'Low' else ''), subset=['Status'])
        .applymap(lambda v: 'color: #2563eb; font-weight:600;' if v == 'Reorder Now' else '', subset=['Action']),
        use_container_width=True
    )
else:
    st.markdown("<div class='success-card'>✅ No low stock alerts!</div>", unsafe_allow_html=True)

# --- Recent Transactions ---
st.markdown("<div class='section-title'>Recent Transactions</div>", unsafe_allow_html=True)
recent_sales = sales.sort_values('sale_date', ascending=False).head(5)
recent_purchases = purchases.sort_values('order_date', ascending=False).head(5)
col6, col7 = st.columns(2)
with col6:
    st.markdown("<b>Recent Sales</b>", unsafe_allow_html=True)
    st.dataframe(recent_sales[['sale_date', 'product_id', 'quantity_sold', 'selling_price']], use_container_width=True)
with col7:
    st.markdown("<b>Recent Purchases</b>", unsafe_allow_html=True)
    st.dataframe(recent_purchases[['order_date', 'product_id', 'quantity_purchased', 'cost_price']], use_container_width=True)

# --- Download Report Button ---
import io
import base64
report_df = pd.DataFrame({
    'Total Sales': [total_sales],
    'Total Products': [total_products],
    'Total Expenses': [total_expenses],
    'COGS': [cogs],
    'Gross Profit': [gross_profit],
    'DIO': [DIO]
})
output = io.BytesIO()
report_df.to_csv(output, index=False)
b64 = base64.b64encode(output.getvalue()).decode()
st.markdown(f"<a href='data:file/csv;base64,{b64}' download='dashboard_report.csv' style='color:#2563eb;font-weight:700;'>⬇️ Download Key Metrics as CSV</a>", unsafe_allow_html=True)
