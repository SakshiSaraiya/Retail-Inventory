import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_connection
from auth import check_login

# -------------------------------
# Page Config and Styling
# -------------------------------
st.set_page_config(page_title="📊 Retail Dashboard", layout="wide")
st.markdown(
    """
    <style>
        body {
            background-color: #F8FAFC;
        }
        section[data-testid="stSidebar"] {
            background-color: #0F172A;
        }
        .main > div {
            padding: 1rem 2rem;
        }
        h1, h2, h3, h4, h5, h6, p {
            color: #0F172A;
        }
        .metric-card {
            background-color: white;
            padding: 1rem;
            border-radius: 1rem;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        }
        .highlight-card {
            background-color: #0F172A;
            color: white;
            padding: 1rem;
            border-radius: 1rem;
            text-align: center;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
        }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Authentication Check
# -------------------------------
check_login()

st.title("📊 Retail Business Dashboard")
st.markdown("Comprehensive insights into sales, inventory, profits, and operational metrics.")

# -------------------------------
# Load Data
# -------------------------------
conn = get_connection()
products = pd.read_sql("SELECT * FROM Products", conn)
sales = pd.read_sql("SELECT * FROM Sales", conn)
purchases = pd.read_sql("SELECT * FROM Purchases", conn)

# -------------------------------
# KPI Cards
# -------------------------------
total_sales = (sales['quantity_sold'] * sales['selling_price']).sum()
total_cogs = 0
for _, row in sales.iterrows():
    cost = products.loc[products['product_id'] == row['product_id'], 'cost_price']
    if not cost.empty:
        total_cogs += row['quantity_sold'] * cost.values[0]
gross_profit = total_sales - total_cogs
profit_margin = (gross_profit / total_sales * 100) if total_sales > 0 else 0

col1, col2, col3 = st.columns(3)
col1.markdown(f"<div class='highlight-card'><h3>Total Sales</h3><h2>₹ {total_sales:,.2f}</h2></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='highlight-card'><h3>Cost of Goods Sold</h3><h2>₹ {total_cogs:,.2f}</h2></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='highlight-card'><h3>Gross Profit</h3><h2>₹ {gross_profit:,.2f}</h2></div>", unsafe_allow_html=True)

st.markdown("---")

# -------------------------------
# Category-wise Profitability
# -------------------------------
merged = pd.merge(sales, products[['product_id', 'NAME', 'category', 'cost_price']], on='product_id', how='left')
merged['Revenue'] = merged['quantity_sold'] * merged['selling_price']
merged['Cost'] = merged['quantity_sold'] * merged['cost_price']
merged['Profit'] = merged['Revenue'] - merged['Cost']

category_profit = merged.groupby('category')[['Revenue', 'Cost', 'Profit']].sum().reset_index()
fig_cat = px.bar(category_profit, x='category', y='Profit', color='category', title="Category-wise Profitability", 
                 color_discrete_sequence=px.colors.qualitative.Vivid)
fig_cat.update_layout(paper_bgcolor='white', plot_bgcolor='white')

st.plotly_chart(fig_cat, use_container_width=True)

# -------------------------------
# Inventory Holding Costs & DIO
# -------------------------------
purchase_qty = purchases.groupby('product_id')['quantity_purchased'].sum().reset_index(name='total_purchased')
sales_qty = sales.groupby('product_id')['quantity_sold'].sum().reset_index(name='total_sold')

live_stock = pd.merge(products, purchase_qty, on='product_id', how='left')
live_stock = pd.merge(live_stock, sales_qty, on='product_id', how='left')
live_stock['total_purchased'].fillna(0, inplace=True)
live_stock['total_sold'].fillna(0, inplace=True)
live_stock['live_stock'] = live_stock['total_purchased'] - live_stock['total_sold']
live_stock['holding_cost'] = live_stock['live_stock'] * live_stock['cost_price']

avg_inventory = (live_stock['live_stock'].mean() + live_stock['stock'].mean()) / 2
daily_cogs = total_cogs / 30 if total_cogs > 0 else 1
DIO = avg_inventory / daily_cogs

col4, col5 = st.columns(2)
col4.metric("Inventory Holding Cost", f"₹ {live_stock['holding_cost'].sum():,.2f}")
col5.metric("Days Inventory Outstanding (DIO)", f"{DIO:.1f} Days")

# -------------------------------
# Supplier Payment Simulation
# -------------------------------
purchases['outstanding'] = purchases.apply(lambda x: x['quantity_purchased'] * x['cost_price'] 
                                            if x['payment_status'].lower() == 'pending' else 0, axis=1)
supplier_outstanding = purchases.groupby('vendor_name')['outstanding'].sum().reset_index()
supplier_outstanding = supplier_outstanding[supplier_outstanding['outstanding'] > 0]

if not supplier_outstanding.empty:
    fig_out = px.pie(supplier_outstanding, names='vendor_name', values='outstanding', 
                     title='Pending Payments to Vendors', color_discrete_sequence=px.colors.sequential.Plasma)
    fig_out.update_layout(paper_bgcolor='white', plot_bgcolor='white')
    st.plotly_chart(fig_out, use_container_width=True)
else:
    st.success("✅ All supplier payments are cleared.")

# -------------------------------
# Low Stock Alert
# -------------------------------
low_stock_df = live_stock[live_stock['live_stock'] <= 5]
st.markdown("### 🧾 Low Stock Alerts")
if not low_stock_df.empty:
    st.dataframe(low_stock_df[['NAME', 'category', 'live_stock']], use_container_width=True)
else:
    st.success("✅ No low stock alerts!")
