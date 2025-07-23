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

st.set_page_config(page_title="Inventory", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)
# -------------------------
# Custom Styling
# -------------------------
st.markdown("""
    <style>
    .metric-card {
        background-color: #1E293B;
        color: #FFFFFF;
        padding: 0.7rem 1rem;
        border-radius: 0.75rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 1rem;
        min-height: 90px;
    }
    .metric-card h4 {
        font-size: 1.05rem;
        margin-bottom: 0.25rem;
        color: #CBD5E1;
    }
    .metric-card h2 {
        font-size: 1.9rem;
        margin: 0;
        font-weight: 700;
        color: #FACC15;
    }
    .dataframe tbody td {
        font-size: 0.95rem;
        color: #1F2937;
    }
    .dataframe thead th {
        background-color: #CBD5E1;
        font-weight: bold;
        color: #1E293B;
        font-size: 0.95rem;
    }
    .section-card {
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(30,41,59,0.08);
        padding: 1.5rem 1.5rem 1.2rem 1.5rem;
        margin-bottom: 2.5rem;
    }
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 1.1rem;
        display: flex;
        align-items: center;
        gap: 0.7rem;
    }
    .kpi-card-light {
        background: #fff;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.10);
        padding: 2rem 1.5rem 1.5rem 1.5rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-width: 180px;
        min-height: 90px;
        margin-bottom: 1.5rem;
        position: relative;
        top: -40px;
    }
    .kpi-card-light .kpi-label {
        font-size: 1.1rem;
        color: #334155;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    .kpi-card-light .kpi-value {
        font-size: 2rem;
        font-weight: 800;
        color: #000;
    }
    .kpi-section-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 1.1rem;
        text-align: center;
        color: #1E293B;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='font-size:2.5rem;color:#0F172A;font-weight:700;position:relative;left:-30px;top:-40px;'>Inventory Overview</h2>", unsafe_allow_html=True)

# -------------------------
# Load data
# -------------------------
conn = get_connection()

try:
    purchases = pd.read_sql("SELECT product_id, quantity_purchased, cost_price, order_date FROM Purchases", conn)
    sales = pd.read_sql("SELECT product_id, quantity_sold, selling_price, sale_date FROM Sales", conn)
    products = pd.read_sql("SELECT Name, category, product_id, cost_price, selling_price FROM Products", conn)
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# -------------------------
# Preprocessing
# -------------------------
purchases['product_id'] = purchases['product_id'].astype(str).str.strip().str.upper()
sales['product_id'] = sales['product_id'].astype(str).str.strip().str.upper()
products['product_id'] = products['product_id'].astype(str).str.strip().str.upper()

# Aggregate data
purchase_agg = purchases.groupby('product_id').agg({'quantity_purchased': 'sum'}).reset_index()
sales_agg = sales.groupby('product_id').agg({'quantity_sold': 'sum'}).reset_index()

# Merge all data
inventory_df = products.merge(purchase_agg, on='product_id', how='left')
inventory_df = inventory_df.merge(sales_agg, on='product_id', how='left')

# Fill NaNs
inventory_df['quantity_purchased'] = inventory_df['quantity_purchased'].fillna(0)
inventory_df['quantity_sold'] = inventory_df['quantity_sold'].fillna(0)

# Live stock = quantity_purchased - quantity_sold
inventory_df['live_stock'] = inventory_df['quantity_purchased'] - inventory_df['quantity_sold']
inventory_df['stock_value'] = inventory_df['live_stock'] * inventory_df['cost_price']
inventory_df['potential_revenue'] = inventory_df['live_stock'] * inventory_df['selling_price']
inventory_df['profit_margin'] = inventory_df['selling_price'] - inventory_df['cost_price']
inventory_df['total_profit'] = inventory_df['profit_margin'] * inventory_df['live_stock']

inventory_df.rename(columns={'Name': 'name', 'category': 'Category'}, inplace=True)

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("Filter Inventory")
categories = inventory_df['Category'].dropna().unique()
selected_category = st.sidebar.multiselect("Category", categories, default=list(categories))
search_term = st.sidebar.text_input("Search Product")

filtered = inventory_df[inventory_df['Category'].isin(selected_category)]
if search_term:
    filtered = filtered[filtered['name'].str.contains(search_term, case=False)]

# -------------------------
# Key Metrics (Light Card Format, Even Row, 4 KPIs)
# -------------------------
st.markdown("<div style='max-width:900px;margin:0 auto 2.5rem auto;'>", unsafe_allow_html=True)
st.markdown("<div class='kpi-section-title'>Key Metrics</div>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
        <div class='kpi-card-light' style='padding:1.3rem 1rem 1rem 1rem;min-width:170px;max-width:200px;'>
            <div class='kpi-label'>Total Live Stock</div>
            <div class='kpi-value'>{int(filtered['live_stock'].sum())}</div>
        </div>
    """, unsafe_allow_html=True)
with k2:
    st.markdown(f"""
        <div class='kpi-card-light' style='padding:1.3rem 1rem 1rem 1rem;min-width:170px;max-width:200px;'>
            <div class='kpi-label'>Stock Value</div>
            <div class='kpi-value'>₹ {filtered['stock_value'].sum():,.2f}</div>
        </div>
    """, unsafe_allow_html=True)
with k3:
    st.markdown(f"""
        <div class='kpi-card-light' style='padding:1.3rem 1rem 1rem 1rem;min-width:170px;max-width:200px;'>
            <div class='kpi-label'>Revenue Potential</div>
            <div class='kpi-value'>₹ {filtered['potential_revenue'].sum():,.2f}</div>
        </div>
    """, unsafe_allow_html=True)
with k4:
    st.markdown(f"""
        <div class='kpi-card-light' style='padding:1.3rem 1rem 1rem 1rem;min-width:170px;max-width:200px;'>
            <div class='kpi-label'>Avg. Margin</div>
            <div class='kpi-value'>₹ {filtered['profit_margin'].mean():.2f}</div>
        </div>
    """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Product Table
# -------------------------
st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:500'>Product List (Live Stock)</div>", unsafe_allow_html=True)
st.dataframe(filtered[['product_id', 'name', 'Category', 'cost_price', 'selling_price', 'live_stock', 'stock_value']], use_container_width=True)

# -------------------------
# Raw Data Table with Edit/Delete (Products)
# -------------------------
show_raw_products = st.checkbox("Show Raw Product Data (Edit/Delete)")
if show_raw_products:
    st.markdown("<h4 style='margin-top:2.5rem;'>Products Table (Raw Data)</h4>", unsafe_allow_html=True)
    st.dataframe(products, use_container_width=True)
    st.markdown("<b>Edit or Delete a Product Record:</b>", unsafe_allow_html=True)
    selected_pid = st.selectbox("Select Product ID to Edit/Delete", products['product_id'] if 'product_id' in products.columns else products.index)
    action = st.radio("Action", ["Edit", "Delete"], key="product_action")
    if action == "Edit":
        row = products[products['product_id'] == selected_pid].iloc[0] if 'product_id' in products.columns else products.loc[[selected_pid]].iloc[0]
        with st.form("edit_product_form"):
            st.write("Edit the fields and click Save:")
            name = st.text_input("Product Name", value=row['Name'])
            category = st.text_input("Category", value=row['category'])
            cost_price = st.number_input("Cost Price", min_value=0.0, value=float(row['cost_price']))
            selling_price = st.number_input("Selling Price", min_value=0.0, value=float(row['selling_price']))
            submit = st.form_submit_button("Save Changes")
            if submit:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Products SET Name=%s, category=%s, cost_price=%s, selling_price=%s WHERE product_id=%s
                """, (name, category, cost_price, selling_price, selected_pid))
                conn.commit()
                cursor.close()
                conn.close()
                st.success("Product record updated!")
                st.experimental_rerun()
    elif action == "Delete":
        if st.button("Delete This Product", key="delete_product_btn", help="Delete this product", use_container_width=True):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Products WHERE product_id=%s", (selected_pid,))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Product record deleted!")
            st.experimental_rerun()

# -------------------------
# Slow Moving Products (last 30 days)
# -------------------------
if 'sale_date' in sales.columns:
    sales['sale_date'] = pd.to_datetime(sales['sale_date'], errors='coerce')
    last_30 = sales[sales['sale_date'] >= pd.Timestamp.now() - pd.Timedelta(days=30)]
    slow_sales = last_30.groupby('product_id')['quantity_sold'].sum().reset_index()
    slow_sales = products.merge(slow_sales, on='product_id', how='left')
    slow_sales['quantity_sold'] = slow_sales['quantity_sold'].fillna(0)
    slowest = slow_sales.sort_values(by='quantity_sold').head(10)
    st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:500'>Slow Moving Products (Last 30 Days)</div>", unsafe_allow_html=True)
    st.dataframe(slowest[["product_id", "Name", "category", "quantity_sold"]], use_container_width=True)

# -------------------------
# Download Inventory Report
# -------------------------
import io
csv = filtered.to_csv(index=False).encode('utf-8')
st.download_button('Download Inventory Report (CSV)', csv, 'inventory_report.csv', 'text/csv')
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Inventory Age Analysis (if purchase date available)
# -------------------------
if 'order_date' in purchases.columns:
    purchases['order_date'] = pd.to_datetime(purchases['order_date'], errors='coerce')
    product_first_purchase = purchases.groupby('product_id')['order_date'].min().reset_index()
    inventory_age = products.merge(product_first_purchase, on='product_id', how='left')
    inventory_age['days_in_stock'] = (pd.Timestamp.now() - inventory_age['order_date']).dt.days
    st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:500'>Inventory Age Analysis</div>", unsafe_allow_html=True)
    st.dataframe(inventory_age[["product_id", "Name", "category", "days_in_stock"]], use_container_width=True)

# -------------------------
# Low Stock Alerts with Reorder Action
# -------------------------
low_stock = filtered[filtered['live_stock'] < 10]
if not low_stock.empty:
    st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:500'>Low Stock Alerts</div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style='background-color:#F87171;padding:10px;border-radius:5px;color:white;font-weight:600;margin-bottom:1rem;'>
            ⚠️ {low_stock.shape[0]} product(s) are low on stock
        </div>
    """, unsafe_allow_html=True)
    low_stock['Action'] = 'Reorder Now'
    st.dataframe(low_stock[["product_id", "name", "Category", "live_stock", "Action"]], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.success('✅ All filtered products are well stocked.')

# -------------------------
# Visualizations
# -------------------------
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    category_value = filtered.groupby('Category')['stock_value'].sum().reset_index()
    fig1 = px.pie(category_value, names='Category', values='stock_value',
                 title="Inventory Value by Category", hole=0.45,
                 color_discrete_sequence=px.colors.sequential.RdBu)
    fig1.update_layout(showlegend=True, plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    top_profit = filtered.sort_values(by='total_profit', ascending=False).head(10)
    fig2 = px.bar(top_profit, x='name', y='total_profit', color='profit_margin',
                 title="Top Products by Profit Potential",
                 color_continuous_scale='viridis')
    fig2.update_layout(xaxis_title="Product", yaxis_title="Profit", showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# Top Products by Stock
# -------------------------
st.markdown("---")
st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:500'>Top N Products by Stock</div>", unsafe_allow_html=True)
top_stock = st.slider("", 5, 20, 10)
stock_bar = px.bar(
    filtered.sort_values(by='live_stock', ascending=False).head(top_stock),
    x='name', y='live_stock',
    title=f"Top {top_stock} Products by Live Stock",
    color='live_stock',
    color_continuous_scale='sunsetdark'
)
stock_bar.update_layout(xaxis_title="Product", yaxis_title="Live Stock", showlegend=False)
st.plotly_chart(stock_bar, use_container_width=True)
