import streamlit as st
from auth import register_user, login_user

# --- Page Config ---
st.set_page_config(
    page_title="Home | Retail Management",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State ---
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# --- Header ---
st.markdown("<h1>Welcome to All-in-One Retail Management</h1>", unsafe_allow_html=True)
st.markdown("<div class='subheading'>Your centralized platform for inventory, finance, and vendor performance insights.</div>", unsafe_allow_html=True)

# --- Authentication Tabs ---
login_tab, register_tab = st.tabs(["Login", "Register"])

with login_tab:
    st.subheader("Login")
    username_or_email = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        success, user_id = login_user(username_or_email, password)
        if success:
            st.session_state.user_id = user_id
            st.success("Login successful!")
        else:
            st.error("Invalid credentials.")

with register_tab:
    st.subheader("Register")
    new_username = st.text_input("New Username")
    new_email = st.text_input("Email")
    new_password = st.text_input("Password", type="password")
    if st.button("Register"):
        success, message = register_user(new_username, new_email, new_password)
        if success:
            st.success(message)
        else:
            st.error(message)

# --- Conditional Access ---
if st.session_state.user_id:
    st.markdown("### Key Features")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Inventory Overview**\n\nMonitor stock levels, categories, and reorder thresholds.")
    with col2:
        st.markdown("**Sales Highlights**\n\nVisualize revenue, spot trends, and assess category performance.")
    with col3:
        st.markdown("**Smart Inventory Suggestions**\n\nLeverage automated restocking alerts and demand forecasting.")

    st.markdown("### Quick Access")
    col4, col5 = st.columns(2)
    with col4:
        st.markdown("**Upload New Data**\n\nQuickly upload product, purchase, or sales records.")
        st.page_link("pages/0_upload_data.py", label="Go to Upload Page")
    with col5:
        st.markdown("**View Financial Dashboard**\n\nAnalyze revenue, expenses, and overall business health.")
        st.page_link("pages/5_Finance_Dashboard.py", label="Go to Financial Dashboard")

    st.markdown("### Platform Capabilities")
    st.markdown("""
    - **Inventory Management** – Track stock, suppliers, and reorder levels.
    - **Sales Analytics** – Understand product demand, trends, and profitability.
    - **Purchase Monitoring** – Control procurement and vendor performance.
    - **Financial Dashboards** – Gain real-time insights into margins and cash flow.
    - **Expense Control** – Monitor costs and improve budgeting decisions.
    """)
else:
    st.warning("Please login to access features and dashboards.")
