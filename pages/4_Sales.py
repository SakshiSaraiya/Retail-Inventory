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
st.markdown("""
<style>
.kpi-section-card {
    background: #fff;
    border-radius: 24px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.10);
    padding: 2.5rem 2rem 2rem 2rem;
    margin-bottom: 2.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.kpi-row {
    display: flex;
    justify-content: center;
    gap: 2.2rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
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
    max-width: 200px;
    min-height: 110px;
    margin-bottom: 0;
}
.kpi-card-light .kpi-icon {
    font-size: 2.1rem;
    margin-bottom: 0.3rem;
}
.kpi-card-light .kpi-label {
    font-size: 1.1rem;
    color: #334155;
    font-weight: 600;
    margin-bottom: 0.2rem;
}
.kpi-card-light .kpi-value {
    font-size: 2rem;
    font-weight: 400;
    color: #f59e42;
}
.kpi-section-title {
    font-size: 1.45rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 2.2rem;
    letter-spacing: 0.5px;
    text-align: center;
}
.quick-insights-row {
    display: flex;
    justify-content: center;
    gap: 2.5rem;
    margin-top: 1.2rem;
    margin-bottom: 0.5rem;
    flex-wrap: wrap;
}
.quick-insight-card {
    background: #eaf1fb;
    border-radius: 14px;
    box-shadow: 0 2px 8px rgba(30,41,59,0.06);
    padding: 1.1rem 1.5rem;
    font-size: 1.08rem;
    color: #334155;
    display: flex;
    align-items: center;
    gap: 0.7rem;
    min-width: 220px;
    position: relative;
    top: -70px;
}
.quick-insight-card .icon {
    font-size: 1.5rem;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
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
    top: -80px;
}
.kpi-card-light .kpi-label {
    font-size: 1.1rem;
    color: #334155;
    font-weight: 600;
    margin-bottom: 0.2rem;
}
.kpi-card-light .kpi-value {
    font-size: 1.75rem;
    font-weight: 600;
    color: #000;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='font-size:2.5rem;color:#0F172A;font-weight:700;position:relative;left:-30px;top:-70px;'>Sales Overview</h2>", unsafe_allow_html=True)
st.markdown(
    "<div style='font-size:1.1rem; color:#475569;margin-bottom:-10.5rem;position:relative;left:-30px;top:-70px;'>"
    "Review sales performance, track order fulfillment, and gain insights into your revenue trends on this page."
    "</div>",
    unsafe_allow_html=True
)
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
st.markdown("""
    <style>
    /* Force black text for selectbox and multiselect in sidebar */
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * {
        color: #000 !important;
        border-radius: 12px !important;
    }
    /* Also target placeholder text */
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] [class*="Placeholder"] {
        color: #000 !important;
        opacity: 1 !important;
    }
    section[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] [class*="Placeholder"] {
        color: #000 !important;
        opacity: 1 !important;
    }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
    section[data-testid="stSidebar"] .stDateInput input {
        color: #000 !important;
        background-color: #fff !important;
    }
    </style>
""", unsafe_allow_html=True)


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
# KPIs (Light Card Format, Even Row, 4 KPIs, Match Inventory Style)
# ----------------------
avg_order_value = filtered_sales['revenue'].sum() / len(filtered_sales) if len(filtered_sales) > 0 else 0
st.markdown("<div style='max-width:900px;margin:0 auto 2.5rem auto;'>", unsafe_allow_html=True)
st.markdown("<div class='kpi-section-title'style='text-align:left;position:relative;margin-bottom:4.5rem;top:-30px;'>Key Metrics</div>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
        <div class='kpi-card-light' style='padding:1.3rem 1rem 1rem 1rem;min-width:170px;max-width:200px;'>
            <div class='kpi-label'>Total Sales</div>
            <div class='kpi-value'>{int(filtered_sales['quantity_sold'].sum())}</div>
        </div>
    """, unsafe_allow_html=True)
with k2:
    st.markdown(f"""
        <div class='kpi-card-light' style='padding:1.3rem 1rem 1rem 1rem;min-width:170px;max-width:200px;'>
            <div class='kpi-label'>Total Revenue</div>
            <div class='kpi-value'>₹ {filtered_sales['revenue'].sum():,.2f}</div>
        </div>
    """, unsafe_allow_html=True)
with k3:
    st.markdown(f"""
        <div class='kpi-card-light' style='padding:1.3rem 1rem 1rem 1rem;min-width:170px;max-width:200px;'>
            <div class='kpi-label'>Total Profit</div>
            <div class='kpi-value'>₹ {filtered_sales['profit'].sum():,.2f}</div>
        </div>
    """, unsafe_allow_html=True)
with k4:
    st.markdown(f"""
        <div class='kpi-card-light' style='padding:1.3rem 1rem 1rem 1rem;min-width:170px;max-width:200px;'>
            <div class='kpi-label'>Avg. Order Value</div>
            <div class='kpi-value'>₹ {avg_order_value:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------
# Quick Insights Row
# ----------------------
best_seller = filtered_sales.groupby('Name')['quantity_sold'].sum().idxmax() if not filtered_sales.empty else None
most_profitable = filtered_sales.groupby('Name')['profit'].sum().idxmax() if not filtered_sales.empty else None
recent_sale = filtered_sales.sort_values('sales_date', ascending=False).iloc[0] if not filtered_sales.empty else None
st.markdown("<div class='quick-insights-row'>", unsafe_allow_html=True)
if best_seller:
    st.markdown(f"<div class='quick-insight-card'><span class='icon'>🏆</span>Best Seller: <b>{best_seller}</b></div>", unsafe_allow_html=True)
if most_profitable:
    st.markdown(f"<div class='quick-insight-card'><span class='icon'>💸</span>Most Profitable: <b>{most_profitable}</b></div>", unsafe_allow_html=True)
if recent_sale is not None:
    st.markdown(f"<div class='quick-insight-card'><span class='icon'>🕒</span>Recent Sale: <b>{recent_sale['Name']}</b> ({recent_sale['sales_date'].date()})</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------
# Download Sales Report
# ----------------------
import io
csv = filtered_sales.to_csv(index=False).encode('utf-8')
st.download_button('Download Sales Report (CSV)', csv, 'sales_report.csv', 'text/csv')

# ----------------------
# Raw Data Table with Edit/Delete (Sales)
# ----------------------
show_raw_sales = st.checkbox("Show Raw Sales Data (Edit/Delete)")
if show_raw_sales:
    st.markdown("<h4 style='margin-top:2.5rem;'>Sales Table (Raw Data)</h4>", unsafe_allow_html=True)
    st.dataframe(sales, use_container_width=True)
    st.markdown("<b>Edit or Delete a Sales Record:</b>", unsafe_allow_html=True)
    selected_sid = st.selectbox("Select Sale ID to Edit/Delete", sales['sale_id'] if 'sale_id' in sales.columns else sales.index)
    action = st.radio("Action", ["Edit", "Delete"], key="sales_action")
    if action == "Edit":
        row = sales[sales['sale_id'] == selected_sid].iloc[0] if 'sale_id' in sales.columns else sales.loc[[selected_sid]].iloc[0]
        with st.form("edit_sales_form"):
            st.write("Edit the fields and click Save:")
            product_id = st.text_input("Product ID", value=row['product_id'])
            quantity_sold = st.number_input("Quantity Sold", min_value=1, value=int(row['quantity_sold']))
            selling_price = st.number_input("Selling Price", min_value=0.0, value=float(row['selling_price']))
            sale_date = st.date_input("Sale Date", value=row['sale_date'])
            shipped_value = st.selectbox("Shipped", ["Yes", "No"], index=0 if row['shipped'] == 1 else 1)
            payment_received = st.selectbox("Payment Received",["Yes", "No"],index=0 if row['payment_received'] == 1 else 1) 
            submit = st.form_submit_button("Save Changes")
            if submit:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Sales SET product_id=%s, quantity_sold=%s, selling_price=%s, sale_date=%s, shipped=%s, payment_received=%s WHERE sale_id=%s
                """, (product_id, quantity_sold, selling_price, sale_date, shipped_value, payment_received, selected_sid))
                conn.commit()
                cursor.close()
                conn.close()
                st.success("Sales record updated!")
                st.rerun()
    elif action == "Delete":
        if st.button("Delete This Sale", key="delete_sale_btn", help="Delete this sale", use_container_width=True):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Sales WHERE sale_id=%s", (selected_sid,))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Sales record deleted!")
            st.rerun()
else:
    # ----------------------
    # Sales Transactions Table (only if raw data is not shown)
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
# Sales by Product (Donut/Pie Chart + Ranked Table)
# ----------------------
st.markdown("---")
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:500'>Product Sales Share</div>", unsafe_allow_html=True)
trend_products = st.multiselect("Select Products for Chart", filtered_sales['Name'].unique(), default=list(filtered_sales['Name'].unique())[:3], key="trend_products")
trend_df = filtered_sales[filtered_sales['Name'].isin(trend_products)]
if not trend_df.empty:
    pie_df = trend_df.groupby('Name')['quantity_sold'].sum().reset_index().sort_values(by='quantity_sold', ascending=False)
    top_pie = pie_df.iloc[0]['Name'] if not pie_df.empty else None
    st.markdown(f"<div style='font-size:1.08rem;color:#2563eb;margin-bottom:0.7rem;'>Top seller: <b>{top_pie}</b> ({int(pie_df.iloc[0]['quantity_sold'])} sold)</div>", unsafe_allow_html=True)
    fig_pie = px.pie(pie_df, names='Name', values='quantity_sold', hole=0.45, color_discrete_sequence=[
        "#A3C4F3", "#FFB7B2", "#B5EAD7", "#FFDAC1", "#E2F0CB",
        "#C7CEEA", "#FFFACD", "#FFD6E0", "#D4A5A5", "#B5B2C2"], title="")
    fig_pie.update_traces(textinfo='percent+label')
    fig_pie.update_layout(showlegend=True, template='plotly_white')
    st.plotly_chart(fig_pie, use_container_width=True)
    # Ranked table with color-coded sales
    styled_table = pie_df.style
    st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:500'>Ranked Product Sales</div>", unsafe_allow_html=True)
    st.dataframe(styled_table, use_container_width=True)
else:
    st.info("No data for selected products.")
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------
# Profitability by Category
# ----------------------
st.markdown("---")
st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:500'>Profitability by Category</div>", unsafe_allow_html=True)
if 'category' in filtered_sales.columns:
    cat_profit = filtered_sales.groupby('category')['profit'].sum().reset_index()
    fig_cat = px.bar(cat_profit, x='category', y='profit', color='profit', color_continuous_scale='peach', title="Profit by Category")
    fig_cat.update_layout(xaxis_title="Category", yaxis_title="Profit", template='plotly_white')
    st.plotly_chart(fig_cat, use_container_width=True)
else:
    st.info("No category data available.")

# ----------------------
# Top Selling Products
# ----------------------
st.markdown("---")
st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:500'>Top-Selling Products</div>", unsafe_allow_html=True)
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
st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:500'>Monthly Trends</div>", unsafe_allow_html=True)
sales['month'] = sales['sales_date'].dt.to_period('M').astype(str)
monthly = sales.groupby('month')[['quantity_sold', 'revenue', 'profit']].sum().reset_index()
fig_combined = px.line(monthly, x='month', y=['quantity_sold', 'revenue', 'profit'], markers=True, title="Monthly Sales Trends")
fig_combined.update_layout(yaxis_title="Values", xaxis_title="Month", template='plotly_white')
st.plotly_chart(fig_combined, use_container_width=True)

# ----------------------
# Forecast Section
# ----------------------
st.markdown("---")
st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:500'>Forecasted Sales</div>", unsafe_allow_html=True)

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
