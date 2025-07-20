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

# --- CSS Styling ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #0F172A;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
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
    .platform-list li {
        padding: 0.3rem 0;
        font-size: 0.95rem;
        color: #334155;
    }
    .stButton>button {
        background-color: #0F172A !important;
        color: white !important;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #1E293B !important;
    }
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<h1>Welcome to All-in-One Retail Management</h1>", unsafe_allow_html=True)
st.markdown("<div class='subheading'>Your centralized platform for inventory, finance, and vendor performance insights.</div>", unsafe_allow_html=True)

# --- Authentication Tabs ---
login_tab, register_tab = st.tabs(["Login", "Register"])

with login_tab:
    st.subheader("Login")
    username_or_email = st.text_input("Username or Email", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login", key="login_button"):
        success, user_id = login_user(username_or_email, login_password)
        if success:
            st.session_state.user_id = user_id
            st.success("Login successful!")
        else:
            st.error("Invalid credentials.")

with register_tab:
    st.subheader("Register")
    new_username = st.text_input("New Username", key="register_username")
    new_email = st.text_input("Email", key="register_email")
    new_password = st.text_input("Password", type="password", key="register_password")
    if st.button("Register", key="register_button"):
        success, message = register_user(new_username, new_email, new_password)
        if success:
            st.success(message)
        else:
            st.error(message)

# --- Conditional Access ---
if st.session_state.user_id:
    st.markdown("<div class='section-title'>Key Features</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class='feature-card'>
                <h4>Inventory Overview</h4>
                <p>Monitor stock levels, categories, and reorder thresholds.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class='feature-card'>
                <h4>Sales Highlights</h4>
                <p>Visualize revenue, spot trends, and assess category performance.</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class='feature-card'>
                <h4>Smart Inventory Suggestions</h4>
                <p>Leverage automated restocking alerts and demand forecasting.</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Quick Access</div>", unsafe_allow_html=True)
    col4, col5 = st.columns(2)
    with col4:
        st.markdown("""
            <div class='feature-card'>
                <h4>Upload New Data</h4>
                <p>Quickly upload product, purchase, or sales records.</p>
            </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/0_upload_data.py", label="Go to Upload Page")
    with col5:
        st.markdown("""
            <div class='feature-card'>
                <h4>View Financial Dashboard</h4>
                <p>Analyze revenue, expenses, and overall business health.</p>
            </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/5_Finance_Dashboard.py", label="Go to Financial Dashboard")

    st.markdown("<div class='section-title'>Platform Capabilities</div>", unsafe_allow_html=True)
    st.markdown("""
    <ul class='platform-list'>
        <li><b>Inventory Management</b> – Track stock, suppliers, and reorder levels.</li>
        <li><b>Sales Analytics</b> – Understand product demand, trends, and profitability.</li>
        <li><b>Purchase Monitoring</b> – Control procurement and vendor performance.</li>
        <li><b>Financial Dashboards</b> – Gain real-time insights into margins and cash flow.</li>
        <li><b>Expense Control</b> – Monitor costs and improve budgeting decisions.</li>
    </ul>
    """, unsafe_allow_html=True)
else:
    st.warning("Please login to access features and dashboards.")
