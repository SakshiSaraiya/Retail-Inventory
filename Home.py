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

# --- Post-Login Navigation ---
if st.session_state["is_logged_in"]:
    st.markdown("<div class='section-title'>Quick Access</div>", unsafe_allow_html=True)

    pages = [
        {"name": "Upload Data", "desc": "Update your inventory, sales, or expense data.", "path": "Upload_Data"},
        {"name": "Finance Dashboard", "desc": "Explore profit, margin, and working capital insights.", "path": "Finance_Dashboard"},
        {"name": "Purchases", "desc": "View and analyze purchase history.", "path": "Purchases"},
        {"name": "Inventory", "desc": "Monitor inventory levels and alerts.", "path": "Inventory"},
        {"name": "Sales", "desc": "Analyze sales trends and forecasting.", "path": "Sales"},
        {"name": "Expenses", "desc": "Manage and track operating costs.", "path": "Expenses"},
    ]

    nav_cols = st.columns(3)
    for idx, page in enumerate(pages):
        col = nav_cols[idx % 3]
        with col:
            st.markdown(f"""
                <div class='nav-card'>
                    <h4>🔹 {page['name']}</h4>
                    <p>{page['desc']}</p>
                    <a href='/{page['path']}' target='_self'><button>Go to {page['name']}</button></a>
                </div>
            """, unsafe_allow_html=True)

    # Logout
    st.markdown("#### ")
    if st.button("Logout"):
        st.session_state["is_logged_in"] = False
        st.session_state["user_id"] = None
        st.rerun()
