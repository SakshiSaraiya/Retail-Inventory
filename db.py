import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_connection
from auth import check_login

# -------------------------
# Config & Auth
# -------------------------
st.set_page_config(page_title="📊 Dashboard", layout="wide")
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #0F172A;
        }
        [data-testid="stSidebar"] * {
            color: white;
        }
        .main {
            background-color: #F8FAFC;
        }
    </style>
""", unsafe_allow_html=True)

check_login()
st.title("📊 Retail Dashboard")

# -------------------------
# Fetch Data
# -------------------------
conn = get_connection()
products = pd.read_sql("SELECT product_id, NAME, category, stock FROM Products", conn)
sales = pd.read_sql("SELECT product_id, quantity_sold, selling_price, sale_date FROM Sales", conn)
purchases = pd.read_sql("SELECT product_id, quantity_purchased FROM Purchases", conn)

# -------------------------
# Data Processing
# -------------------------
product_info = products[['product_id', 'NAME', 'category', 'stock']]

purchases_summary = purchases.groupby('product_id')['quantity_purchased'].sum().reset_index()
sales_summary = sales.groupby('product_id')['quantity_sold'].sum().reset_index()

merged = product_info.merge(purchases_summary, on='product_id', how='left')
merged = merged.merge(sales_summary, on='product_id', how='left')
merged['quantity_purchased'] = merged['quantity_purchased'].fillna(0)
merged['quantity_sold'] = merged['quantity_sold'].fillna(0)
merged['live_stock'] = merged['stock'] + merged['quantity_purchased'] - merged['quantity_sold']

# -------------------------
# Sidebar Filters
# -------------------------
category_filter = st.sidebar.multiselect("Filter by Category", merged['category'].unique(), default=merged['category'].unique())

filtered = merged[merged['category'].isin(category_filter)]

# -------------------------
# KPI Cards
# -------------------------
total_products = filtered['product_id'].nunique()
total_stock = int(filtered['live_stock'].sum())
total_sales = int(sales['quantity_sold'].sum())
total_revenue = (sales['quantity_sold'] * sales['selling_price']).sum()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("📦 Total Products", total_products)
kpi2.metric("📊 Total Sales Units", total_sales)
kpi3.metric("💰 Revenue", f"₹ {total_revenue:,.2f}")
kpi4.metric("📥 Live Stock", total_stock)

# -------------------------
# Visualizations
# -------------------------
st.markdown("---")
st.subheader("📈 Category-wise Stock Distribution")
cat_stock = filtered.groupby('category')['live_stock'].sum().reset_index()
fig1 = px.bar(cat_stock, x='category', y='live_stock', color_discrete_sequence=['#1E40AF'])
fig1.update_layout(plot_bgcolor='white', xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
st.plotly_chart(fig1, use_container_width=True)

st.subheader("📈 Monthly Sales Trend")
sales['sale_date'] = pd.to_datetime(sales['sale_date'])
sales['month'] = sales['sale_date'].dt.to_period('M').astype(str)
monthly_sales = sales.groupby('month')['quantity_sold'].sum().reset_index()
fig2 = px.line(monthly_sales, x='month', y='quantity_sold', markers=True, color_discrete_sequence=['#1E40AF'])
fig2.update_layout(plot_bgcolor='white', xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
st.plotly_chart(fig2, use_container_width=True)

st.subheader("🔍 Low Stock Alerts")
low_stock_df = filtered[filtered['live_stock'] < 10][['NAME', 'category', 'live_stock']]
st.dataframe(low_stock_df, use_container_width=True)

st.subheader("📊 Product-wise Inventory Overview")
st.dataframe(filtered[['NAME', 'category', 'stock', 'quantity_purchased', 'quantity_sold', 'live_stock']], use_container_width=True)

conn.close()
