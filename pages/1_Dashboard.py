import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_connection
from auth import check_login

# -------------------------------
# Page Config and Styling
# -------------------------------
st.set_page_config(page_title="📊 Dashboard", layout="wide")
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

# -------------------------------
# Load Data
# -------------------------------
conn = get_connection()
products = pd.read_sql("SELECT * FROM Products", conn)
sales = pd.read_sql("SELECT * FROM Sales", conn)
purchases = pd.read_sql("SELECT * FROM Purchases", conn)

# Merge for analysis
merged = pd.merge(sales, products[['product_id', 'NAME', 'category']], on='product_id', how='left')

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

col1, col2, col3 = st.columns(3)
col1.markdown(f"<div class='highlight-card'><h3>Total Sales</h3><h2>₹ {total_sales:,.2f}</h2></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='highlight-card'><h3>Cost of Goods Sold</h3><h2>₹ {total_cogs:,.2f}</h2></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='highlight-card'><h3>Gross Profit</h3><h2>₹ {gross_profit:,.2f}</h2></div>", unsafe_allow_html=True)

st.markdown("---")

# -------------------------------
# Category-wise Sales Pie Chart
# -------------------------------
category_sales = (
    merged.groupby('category')
    .apply(lambda x: (x['quantity_sold'] * x['selling_price']).sum())
    .reset_index(name='total_sales')
)

fig_pie = px.pie(category_sales, values='total_sales', names='category', title="Category-wise Sales",
                 color_discrete_sequence=px.colors.qualitative.Set3)
fig_pie.update_traces(textinfo='percent+label')
fig_pie.update_layout(showlegend=True, paper_bgcolor='white', plot_bgcolor='white')

# -------------------------------
# Top 5 Products by Sales
# -------------------------------
product_sales = (
    merged.groupby('NAME')
    .apply(lambda x: (x['quantity_sold'] * x['selling_price']).sum())
    .reset_index(name='total_sales')
    .sort_values(by='total_sales', ascending=False)
    .head(5)
)

fig_bar = px.bar(product_sales, x='NAME', y='total_sales',
                 title="Top 5 Products by Sales",
                 color='NAME', color_discrete_sequence=px.colors.qualitative.Prism)
fig_bar.update_layout(xaxis_title="", yaxis_title="Sales", paper_bgcolor='white', plot_bgcolor='white')

col4, col5 = st.columns(2)
with col4:
    st.plotly_chart(fig_pie, use_container_width=True)
with col5:
    st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------
# Live Stock Calculation
# -------------------------------
initial_stock = products[['product_id', 'NAME', 'category', 'stock']].copy()
purchase_qty = purchases.groupby('product_id')['quantity_purchased'].sum().reset_index(name='total_purchased')
sales_qty = sales.groupby('product_id')['quantity_sold'].sum().reset_index(name='total_sold')

live_stock = pd.merge(initial_stock, purchase_qty, on='product_id', how='left')
live_stock = pd.merge(live_stock, sales_qty, on='product_id', how='left')

live_stock['total_purchased'].fillna(0, inplace=True)
live_stock['total_sold'].fillna(0, inplace=True)

live_stock['live_stock'] = live_stock['stock'] + live_stock['total_purchased'] - live_stock['total_sold']

# -------------------------------
# Low Stock Alert
# -------------------------------
low_stock_df = live_stock[live_stock['live_stock'] <= 5]

st.markdown("### 🧾 Low Stock Alerts")
if not low_stock_df.empty:
    st.dataframe(low_stock_df[['NAME', 'category', 'live_stock']], use_container_width=True)
else:
    st.success("✅ No low stock alerts!")

