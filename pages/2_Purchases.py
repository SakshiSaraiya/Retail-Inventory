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


st.set_page_config(page_title="Purchases", layout="wide")

# -------------------------
# Custom Styling
# -------------------------
st.markdown("""
    <style>
    body {
        background-color: #F9FAFB;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #1E293B;
    }

    [data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
        font-size: 0.95rem;
    }

    .metric-card {
        background-color: #1E293B;
        color: #FFFFFF;
        padding: 0.6rem 0.8rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 1rem;
        min-height: 80px;
    }
    .metric-card h4 {
        font-size: 1rem;
        margin-bottom: 0.25rem;
        color: #F8FAFC;
    }
    .metric-card h2 {
        font-size: 1.6rem;
        margin: 0;
        font-weight: 700;
        color: #FACC15;
    }
    h1, h2, h3, h4, h5, h6, p {
        color: #0F172A;
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
    </style>
""", unsafe_allow_html=True)

# --- Custom CSS for dark sidebar/light main ---
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

# --- GLOBAL STYLES FOR ZOHO-LIKE LOOK ---
st.markdown("""
    <style>
    /* Main background */
    .main-bg {
        background: #f8fafc;
        min-height: 100vh;
        padding: 0 2.5rem 2rem 2.5rem;
    }
    /* Card styles */
    .kpi-card, .white-card {
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(30,41,59,0.08);
        padding: 1.5rem 1.5rem 1.2rem 1.5rem;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-width: 180px;
        min-height: 90px;
        margin-top: 0rem;
    }
    .kpi-label {
        font-size: 1.08rem;
        color: #475569;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 800;
        color: #000;
    }
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1.1rem;
        margin-top: 0rem;
    }
    .divider {
        border: none;
        border-top: 1.5px solid #e2e8f0;
        margin: 2.2rem 0 2.2rem 0;
    }
    /* Table styles */
    .white-card table {
        font-size: 1.01rem;
        color: #1e293b;
    }
    </style>
""", unsafe_allow_html=True)

# --- REMOVE CUSTOM SIDEBAR MENU WITH ICONS ---
# (No custom HTML sidebar menu here; rely on Streamlit's default sidebar navigation)

# --- MAIN CONTENT WRAPPER ---

# --- PAGE TITLE ---
st.markdown("<div class='section-title'<h1 style='font-size:2.5rem;color:#0F172A;font-weight:700;position:relative;left:-30px;top:-60px;'>Purchase Overview</div>", unsafe_allow_html=True)

# -------------------------
# Connect to SQL
# -------------------------
conn = get_connection()

# -------------------------
# Load Data from SQL
# -------------------------
purchases = pd.read_sql("SELECT * FROM Purchases", conn)
purchases['order_date'] = pd.to_datetime(purchases['order_date'], errors='coerce')
purchases['payment_due'] = pd.to_datetime(purchases['payment_due'], errors='coerce')

# -------------------------
# Compute KPIs
# -------------------------
total_orders = len(purchases)
total_quantity = purchases['quantity_purchased'].sum()
total_cost = (purchases['quantity_purchased'] * purchases['cost_price']).sum()
vendors = purchases['vendor_name'].nunique()

# --- KPI CARDS ---
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class='kpi-card'><div class='kpi-label'>Total Orders</div><div class='kpi-value'>{total_orders}</div></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class='kpi-card'><div class='kpi-label'>Units Purchased</div><div class='kpi-value'>{total_quantity}</div></div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class='kpi-card'><div class='kpi-label'>Total Spend</div><div class='kpi-value'>₹ {total_cost:,.2f}</div></div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class='kpi-card'><div class='kpi-label'>Vendors</div><div class='kpi-value'>{vendors}</div></div>""", unsafe_allow_html=True)

# --- DIVIDER ---
st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# --- Raw Data Table with Edit/Delete (toggle) ---
show_raw = st.checkbox("Show Raw Data Table (Edit/Delete)")
if show_raw:
    st.markdown("<h1 style='font-size:2.0rem;color:#0F172A;font-weight:00;position:relative:top:-40px;'>Purchase Records</h4>", unsafe_allow_html=True)
    raw_df = purchases.copy()
    st.dataframe(raw_df, use_container_width=True)
    st.markdown("<b>Edit or Delete a Purchase Record:</b>", unsafe_allow_html=True)
    selected_id = st.selectbox("Select Purchase ID to Edit/Delete", raw_df['purchase_id'] if 'purchase_id' in raw_df.columns else raw_df.index)
    action = st.radio("Action", ["Edit", "Delete"])
    if action == "Edit":
        row = raw_df[raw_df['purchase_id'] == selected_id].iloc[0] if 'purchase_id' in raw_df.columns else raw_df.loc[[selected_id]].iloc[0]
        with st.form("edit_purchase_form"):
            st.write("Edit the fields and click Save:")
            product_id = st.number_input("Product ID", min_value=1, value=int(row['product_id']))
            vendor_name = st.text_input("Vendor Name", value=row['vendor_name'])
            quantity_purchased = st.number_input("Quantity Purchased", min_value=1, value=int(row['quantity_purchased']))
            cost_price = st.number_input("Cost Price", min_value=0.0, value=float(row['cost_price']))
            order_date = st.date_input("Order Date", value=row['order_date'])
            payment_due = st.date_input("Payment Due Date", value=row['payment_due'])
            payment_status = st.selectbox("Payment Status", ["Pending", "Completed", "Overdue"], index=["Pending", "Completed", "Overdue"].index(row['payment_status']) if row['payment_status'] in ["Pending", "Completed", "Overdue"] else 0)
            submit = st.form_submit_button("Save Changes")
            if submit:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Purchases SET product_id=%s, vendor_name=%s, quantity_purchased=%s, cost_price=%s, order_date=%s, payment_due=%s, payment_status=%s WHERE purchase_id=%s
                """, (product_id, vendor_name, quantity_purchased, cost_price, order_date, payment_due, payment_status, selected_id))
                conn.commit()
                cursor.close()
                conn.close()
                st.success("Purchase record updated!")
                st.experimental_rerun()
    elif action == "Delete":
        if st.button("Delete This Record", key="delete_btn", help="Delete this record", use_container_width=True):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Purchases WHERE purchase_id=%s", (selected_id,))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Purchase record deleted!")
            st.experimental_rerun()

# -------------------------
# Sidebar Filters
# -------------------------
st.markdown("""
<style>
   [data-testid="stSidebar"] {
        background-color: #0F172A !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Filters ---
product_filter = st.sidebar.multiselect("Product ID", purchases['product_id'].dropna().unique(), default=purchases['product_id'].unique(), key="product_filter")
vendor_filter = st.sidebar.multiselect("Vendor", purchases['vendor_name'].dropna().unique(), default=purchases['vendor_name'].unique(), key="vendor_filter")
status_filter = st.sidebar.multiselect("Payment Status", purchases['payment_status'].dropna().unique(), default=purchases['payment_status'].unique(), key="status_filter")
start_date = st.sidebar.date_input("Start Date", purchases['order_date'].min(), key="start_date")
end_date = st.sidebar.date_input("End Date", purchases['order_date'].max(), key="end_date")

filtered = purchases[
    (purchases['product_id'].isin(product_filter)) &
    (purchases['vendor_name'].isin(vendor_filter)) &
    (purchases['payment_status'].isin(status_filter)) &
    (purchases['order_date'] >= pd.to_datetime(start_date)) &
    (purchases['order_date'] <= pd.to_datetime(end_date))
]

# -------------------------
# Display Filtered Table
# -------------------------
if show_raw:
    st.markdown("<h4 style='margin-top:2rem;'>Purchase Records</h4>", unsafe_allow_html=True)
    st.dataframe(filtered, use_container_width=True)

# ---------- Payment Alerts ----------
st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:600;position:relative:top:-40px;'>Payment Alerts</div>", unsafe_allow_html=True)
today = pd.to_datetime("today")
pending = purchases[(purchases['payment_status'].str.lower() == "pending") & (purchases['payment_due'] >= today)]
overdue = purchases[(purchases['payment_status'].str.lower() == "pending") & (purchases['payment_due'] < today)]

col1, col2 = st.columns(2)

with col1:
    if not pending.empty:
        st.markdown("<div style='background-color:#FDE68A;padding:1rem;border-radius:0.5rem;'>", unsafe_allow_html=True)
        st.warning(f"Pending Payments: {len(pending)}")
        st.dataframe(pending[['vendor_name', 'product_id', 'payment_due']], use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("No pending payments.")

with col2:
    if not overdue.empty:
        st.markdown("<div style='background-color:#FCA5A5;padding:1rem;border-radius:0.5rem;'>", unsafe_allow_html=True)
        st.error(f"Overdue Payments: {len(overdue)}")
        st.dataframe(overdue[['vendor_name', 'product_id', 'payment_due']], use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("No overdue payments.")

# -------------------------
# Visualizations (Updated Layout & Color)
# -------------------------
st.markdown("---")
st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:600;position:relative:top:-40px;'>Insightful Visualisations</div>", unsafe_allow_html=True)
# Donut Chart for Vendors
col1, col2 = st.columns(2)

with col1:
    vendor_summary = purchases.groupby('vendor_name')['quantity_purchased'].sum().reset_index()
    fig_donut = px.pie(
        vendor_summary,
        names='vendor_name',
        values='quantity_purchased',
        title="Vendor Share",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_donut.update_layout(
        font=dict(family="Segoe UI", size=14, color="#0F172A"),
        showlegend=True,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF"
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# Top Products Chart
with col2:
    product_summary = purchases.groupby('product_id')['quantity_purchased'].sum().reset_index().sort_values(by='quantity_purchased', ascending=False)
    fig_product = px.bar(
        product_summary,
        x='product_id',
        y='quantity_purchased',
        title="Top Products by Purchase Volume",
        color='quantity_purchased',
        color_continuous_scale='Plasma'
    )
    fig_product.update_layout(
        xaxis_title="Product ID", yaxis_title="Quantity",
        font=dict(family="Segoe UI", size=14, color="#0F172A"),
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF"
    )
    st.plotly_chart(fig_product, use_container_width=True)

# Monthly Trend
monthly_summary = purchases.groupby(purchases['order_date'].dt.to_period('M').astype(str))['quantity_purchased'].sum().reset_index()
fig_monthly = px.area(
    monthly_summary,
    x='order_date',
    y='quantity_purchased',
    title="Monthly Purchase Volume",
    color_discrete_sequence=['#1D4ED8']
)
fig_monthly.update_layout(
    xaxis_title="Month", yaxis_title="Quantity",
    font=dict(family="Segoe UI", size=14, color="#0F172A"),
    plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF"
)
st.plotly_chart(fig_monthly, use_container_width=True)

# --- END MAIN CONTENT WRAPPER ---
