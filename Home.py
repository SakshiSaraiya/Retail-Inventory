import streamlit as st  
from auth import register_user, login_user

# --- Page Config ---
st.set_page_config(
    page_title="Home | Retail Management",
    layout="wide",
    initial_sidebar_state="expanded" if st.session_state.get("is_logged_in", False) else "collapsed"
)

# --- Session State ---
if "is_logged_in" not in st.session_state:
    st.session_state["is_logged_in"] = False
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

# --- Custom Styling ---
st.markdown("""
    <style>
    .block-container {
        background-color: #F8FAFC;
        padding-top: 2rem;
    }
    h1 {
        color: #0F172A !important;
        font-weight: 900;
        font-size: 2.4rem !important;
        margin-bottom: 0.4rem;
    }
    .subheading {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        color: #1E293B;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 180px;
    }
    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1E293B;
        margin: 2rem 0 1rem;
    }
    .nav-card {
        background-color: #FFFFFF;
        color: #0F172A;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .nav-card h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1.2rem;
    }
    .nav-card p {
        font-size: 0.95rem;
        margin-bottom: 1rem;
        color: #0F172A ;
    }
    .nav-card a button {
        background-color: #0F172A;
        color: white;
        border: none;
        padding: 0.5rem 1.2rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: 0.3s;
    }
    .nav-card a button:hover {
        background-color: #1E293B;
    }
    [data-testid="stSidebar"] {
        background-color: #0F172A;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- Main Header ---
st.markdown("<h1>Welcome to All-in-One Retail Management</h1>", unsafe_allow_html=True)
st.markdown("<div class='subheading'>Your centralized platform for inventory, finance, and vendor performance insights.</div>", unsafe_allow_html=True)

# --- Features Summary ---
st.markdown("<div class='section-title'>Key Features</div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
        <div class='feature-card'>
            <h4>📦 Inventory Management</h4>
            <p>Track stock levels, categories, reorder alerts.</p>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
        <div class='feature-card'>
            <h4>📊 Sales & Profit Analysis</h4>
            <p>Visual dashboards for revenue and trends.</p>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
        <div class='feature-card'>
            <h4>📈 Smart Forecasting</h4>
            <p>Predict demand and optimize inventory costs.</p>
        </div>
    """, unsafe_allow_html=True)

# --- Authentication ---
if not st.session_state["is_logged_in"]:
    login_tab, register_tab = st.tabs(["🔐 Login", "📝 Register"])

    with login_tab:
        st.subheader("Login")
        username_or_email = st.text_input("Username or Email")
        password = st.text_input("Password", type="password", key="login_password")
        login_submit = st.button("Login")

        if login_submit:
            success, user_id = login_user(username_or_email, password)
            if success:
                st.session_state["is_logged_in"] = True
                st.session_state["user_id"] = user_id
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

    with register_tab:
        st.subheader("Register")
        new_username = st.text_input("New Username")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password", key="register_password")
        register_submit = st.button("Register")

        if register_submit:
            success, message = register_user(new_username, new_email, new_password)
            if success:
                st.success(message)
            else:
                st.error(message)

# --- Post-Login Summary Dashboard ---
if st.session_state["is_logged_in"]:
    st.markdown("<div class='section-title'>Your Retail Summary</div>", unsafe_allow_html=True)


    import pandas as pd
    import plotly.express as px
    from db import get_connection

    # --- Fetch Data from MySQL ---
    conn = get_connection()
    total_products, total_sales, total_expenses = 0, 0, 0
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Products WHERE user_id = %s", (st.session_state["user_id"],))
        total_products = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(quantity_sold * selling_price) FROM Sales WHERE user_id = %s", (st.session_state["user_id"],))
        total_sales = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(amount) FROM Expenses WHERE user_id = %s", (st.session_state["user_id"],))
        total_expenses = cursor.fetchone()[0] or 0

        cursor.close()
        conn.close()

    # --- Professional Metric Cards ---
    card_style = """
        background-color: white;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: center;
        font-weight: 600;
        color: #0F172A;
        font-size: 20px;
    """
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div style='{card_style}'>🛒<br>Total Products<br><span style='font-size:26px'>{total_products}</span></div>", unsafe_allow_html=True)
    col2.markdown(f"<div style='{card_style}'>💰<br>Total Sales<br><span style='font-size:26px'>₹{total_sales:,.2f}</span></div>", unsafe_allow_html=True)
    col3.markdown(f"<div style='{card_style}'>📉<br>Total Expenses<br><span style='font-size:26px'>₹{total_expenses:,.2f}</span></div>", unsafe_allow_html=True)

# Recent Activities (from Sales table)
try:
    user_id = st.session_state.user_id
    query = """
        SELECT s.sale_date, p.NAME, s.quantity_sold
        FROM Sales s
        JOIN Products p ON s.product_id = p.product_id
        WHERE s.user_id = %s
        ORDER BY s.sale_date DESC
        LIMIT 5
    """
    recent_sales = pd.read_sql(query, conn, params=(user_id,))
except Exception as e:
    recent_sales = pd.DataFrame()

# ----------------------------
# To-Do Items (manual)
todos = [
    "Reorder stock for low inventory items",
    "Verify vendor payments",
    "Check today's sales reports",
    "Schedule team meeting",
    "Update product catalog"
]

st.markdown('<div class="section-title">Daily Overview</div>', unsafe_allow_html=True)
left_col, right_col = st.columns(2)

with left_col:
    st.markdown('<div class="card"><h4 style="margin-top:0;">Recent Activities</h4>', unsafe_allow_html=True)
    if not recent_sales.empty:
        for _, row in recent_sales.iterrows():
            sale_date = pd.to_datetime(row['sale_date']).strftime('%d %b %Y')
            st.markdown(f"<div class='box-content'><strong>{row['NAME']}</strong> - {row['quantity_sold']} pcs on {sale_date}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='box-content'>No recent sales data.</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="card"><h4 style="margin-top:0;">To-do Reminders</h4>', unsafe_allow_html=True)
    for task in todos:
        st.markdown(f"<div class='box-content'>{task}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Footer
st.markdown("""
---
<p style='text-align: center; color: #94A3B8;'>© 2025 Retail Analytics | All rights reserved</p>
""", unsafe_allow_html=True)

    # --- Logout Button ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button("Logout"):
    st.session_state["is_logged_in"] = False
    st.session_state["user_id"] = None
    st.rerun()



