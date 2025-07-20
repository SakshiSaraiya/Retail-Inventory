import streamlit as st 
import pandas as pd
import plotly.express as px
from db import get_connection
from auth import check_login

# -------------------------
# Authentication Check
# -------------------------
check_login()
user_id = st.session_state.user_id

st.set_page_config(page_title="📈 Sales", layout="wide")



st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #0F172A;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    .metric-card {
        background-color: #1E293B;
        color: white;
        padding: 0.8rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        text-align: center;
        min-height: 100px;
    }
    .metric-card h4 {
        font-size: 1rem;
        margin-bottom: 0.2rem;
        color: #CBD5E1;
    }
    .metric-card h2 {
        font-size: 1.7rem;
        font-weight: 700;
        color: #FACC15;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""<h2 style='margin-bottom:1rem;'>📈 Sales Overview</h2>""", unsafe_allow_html=True)

conn = get_connection()

try:
    sales = pd.read_sql("SELECT * FROM Sales", conn)
    products = pd.read_sql("SELECT product_id, Name, category FROM Products", conn)
    purchases = pd.read_sql("SELECT product_id, cost_price FROM Purchases", conn)
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# ----------------------
# Preprocessing
# ----------------------
sales['product_id'] = sales['product_id'].astype(str).str.strip().str.upper()
products['product_id'] = products['product_id'].astype(str).str.strip().str.upper()
purchases['product_id'] = purchases['product_id'].astype(str).str.strip().str.upper()

sales = sales.merge(products, on='product_id', how='left')
sales = sales.merge(purchases.groupby('product_id').mean().reset_index(), on='product_id', how='left')

sales['sales_date'] = pd.to_datetime(sales['sale_date'], errors='coerce')
sales['revenue'] = sales['quantity_sold'] * sales['selling_price']
sales['profit'] = sales['quantity_sold'] * (sales['selling_price'] - sales['cost_price'])

# ----------------------
# Sidebar Filters
# ----------------------
st.sidebar.header("🔍 Filter Sales")
product_filter = st.sidebar.multiselect("Product", sales['Name'].dropna().unique(), default=sales['Name'].dropna().unique())
shipped_filter = st.sidebar.selectbox("Shipped Status", ["All"] + sorted(sales['shipped'].dropna().unique().tolist()))
payment_filter = st.sidebar.selectbox("Payment Status", ["All"] + sorted(sales['payment_received'].dropna().unique().tolist()))
start_date = st.sidebar.date_input("Start Date", sales['sales_date'].min())
end_date = st.sidebar.date_input("End Date", sales['sales_date'].max())

filtered_sales = sales[
    (sales['Name'].isin(product_filter)) &
    (sales['sales_date'] >= pd.to_datetime(start_date)) &
    (sales['sales_date'] <= pd.to_datetime(end_date))
]

if shipped_filter != "All":
    filtered_sales = filtered_sales[filtered_sales['shipped'] == shipped_filter]
if payment_filter != "All":
    filtered_sales = filtered_sales[filtered_sales['payment_received'] == payment_filter]

# ----------------------
# KPIs
# ----------------------
st.markdown("### 📊 Sales KPIs")
k1, k2, k3, k4 = st.columns(4)
k1.metric("🧾 Total Sales", int(filtered_sales['quantity_sold'].sum()))
k2.metric("💰 Total Revenue", f"₹ {filtered_sales['revenue'].sum():,.2f}")
k3.metric("📈 Total Profit", f"₹ {filtered_sales['profit'].sum():,.2f}")
k4.metric("🛙 Orders", len(filtered_sales))

# ----------------------
# Transactions Table
# ----------------------
st.markdown("### 📋 Sales Transactions")
if filtered_sales.empty:
    st.warning("⚠️ No matching sales records found with current filters.")
else:
    st.dataframe(
        filtered_sales[['sale_id', 'sales_date', 'Name', 'quantity_sold', 'revenue', 'profit', 'shipped', 'payment_received']],
        use_container_width=True
    )

# ----------------------
# Top Selling Products
# ----------------------
st.markdown("---")
st.markdown("### 🏆 Top-Selling Products")
top_n = st.slider("Top N Products", 5, 20, 10)
top_products = filtered_sales.groupby('Name')[['quantity_sold', 'revenue', 'profit']].sum().reset_index()
top_products = top_products.sort_values(by='quantity_sold', ascending=False).head(top_n)

col1, col2 = st.columns(2)
with col1:
    fig1 = px.bar(top_products, x='Name', y='quantity_sold', title=f"Top {top_n} by Quantity", color='quantity_sold', color_continuous_scale='Tealgrn')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(top_products, x='Name', y='revenue', title=f"Top {top_n} by Revenue", color='revenue', color_continuous_scale='Emrld')
    st.plotly_chart(fig2, use_container_width=True)

# ----------------------
# Monthly Trends
# ----------------------
st.markdown("---")
st.markdown("### 📊 Monthly Trends")
sales['month'] = sales['sales_date'].dt.to_period('M').astype(str)
monthly = sales.groupby('month')[['quantity_sold', 'revenue', 'profit']].sum().reset_index()
fig_combined = px.line(monthly, x='month', y=['quantity_sold', 'revenue', 'profit'], markers=True, title="Monthly Sales Trends")
fig_combined.update_layout(yaxis_title="Values", xaxis_title="Month", template='plotly_white')
st.plotly_chart(fig_combined, use_container_width=True)

# ----------------------
# Forecast Section
# ----------------------
st.markdown("---")
st.markdown("### 🔮 Forecasted Sales")

available_products = sales['Name'].dropna().unique()
selected_product = st.selectbox("Select Product", sorted(available_products))
forecast_sales = sales[sales['Name'] == selected_product].copy()
forecast_sales['month'] = forecast_sales['sales_date'].dt.to_period('M').astype(str)
forecast_grouped = forecast_sales.groupby('month')['quantity_sold'].sum().reset_index()
forecast_grouped['month'] = pd.to_datetime(forecast_grouped['month'], errors='coerce')
forecast_grouped = forecast_grouped.sort_values('month')
forecast_grouped['forecast'] = forecast_grouped['quantity_sold'].rolling(3, min_periods=1).mean()

if not forecast_grouped.empty:
    last_month = forecast_grouped['month'].max()
    forecast_months = pd.date_range(start=last_month + pd.offsets.MonthBegin(), periods=3, freq='MS')
    future_forecast = pd.DataFrame({
        'month': forecast_months,
        'quantity_sold': [None]*3,
        'forecast': [forecast_grouped['forecast'].iloc[-1]]*3
    })
    combined_forecast = pd.concat([forecast_grouped, future_forecast], ignore_index=True)

    fig = px.line(combined_forecast, x='month', y='forecast', title=f"Forecast: {selected_product}", labels={'forecast': 'Forecasted Quantity'}, markers=True)
    fig.add_scatter(x=forecast_grouped['month'], y=forecast_grouped['quantity_sold'], mode='lines+markers', name='Actual Quantity', line=dict(color='orange'))
    fig.update_layout(template='plotly_white')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ No data available to forecast for this product.")
