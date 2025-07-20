import streamlit as st
from auth import login_user, register_user

# Page config
st.set_page_config(page_title="Home - Retail Management", layout="wide")

# Initialize session state
if "is_logged_in" not in st.session_state:
    st.session_state["is_logged_in"] = False
    st.session_state["user_id"] = None

# -------------------------------
# Custom Styling
# -------------------------------
st.markdown("""
    <style>
        .main {
            background-color: #F8FAFC;
        }
        .css-1d391kg { background-color: #0F172A; } /* Dark sidebar */
        .stButton>button {
            background-color: #0F172A;
            color: white;
            border-radius: 0.5rem;
        }
        .card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            margin-bottom: 1.5rem;
        }
        .section-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin: 1.5rem 0 1rem;
            color: #0F172A;
        }
        .nav-button {
            margin-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Heading and Features (Always Visible)
# -------------------------------
st.markdown("## Welcome to All-in-One Retail Management")
st.markdown("Your centralized platform for inventory, finance, and vendor performance insights.")

st.markdown("<div class='section-title'>Key Features</div>", unsafe_allow_html=True)

feature_cols = st.columns(3)
with feature_cols[0]:
    st.markdown("""
        <div class='card'>
            <h4>Inventory Overview</h4>
            <p>Monitor stock levels, categories, and reorder thresholds.</p>
        </div>
    """, unsafe_allow_html=True)
with feature_cols[1]:
    st.markdown("""
        <div class='card'>
            <h4>Sales Highlights</h4>
            <p>Visualize revenue, spot trends, and assess category performance.</p>
        </div>
    """, unsafe_allow_html=True)
with feature_cols[2]:
    st.markdown("""
        <div class='card'>
            <h4>Smart Inventory Suggestions</h4>
            <p>Leverage automated restocking alerts and demand forecasting.</p>
        </div>
    """, unsafe_allow_html=True)

# -------------------------------
# Login + Register (Shown Before Login)
# -------------------------------
if not st.session_state["is_logged_in"]:
    st.markdown("<div class='section-title'>Login or Register</div>", unsafe_allow_html=True)
    login_col, register_col = st.columns(2)

    with login_col:
        st.markdown("#### Login")
        with st.form("login_form"):
            username_or_email = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            login_submit = st.form_submit_button("Login")

            if login_submit:
                success, user_id = login_user(username_or_email, password)
                if success:
                    st.session_state["is_logged_in"] = True
                    st.session_state["user_id"] = user_id
                    st.success("Login successful!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials. Please try again.")

    with register_col:
        st.markdown("#### Register")
        with st.form("register_form"):
            new_username = st.text_input("New Username")
            new_email = st.text_input("New Email")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_submit = st.form_submit_button("Register")

            if register_submit:
                if new_password != confirm_password:
                    st.warning("Passwords do not match.")
                elif len(new_password) < 6:
                    st.warning("Password must be at least 6 characters.")
                else:
                    success, msg = register_user(new_username, new_email, new_password)
                    if success:
                        st.success(msg + " You can now log in.")
                    else:
                        st.error(msg)

# -------------------------------
# Quick Navigation Buttons (After Login)
# -------------------------------
if st.session_state["is_logged_in"]:
    st.markdown("<div class='section-title'>Quick Access</div>", unsafe_allow_html=True)

    pages = [
        {"name": "Upload Data", "desc": "Update your inventory, sales, or expense data.", "path": "Upload_Data"},
        {"name": "Finance Dashboard", "desc": "Explore profit, margin, and working capital insights.", "path": "Finance_Dashboard"},
        {"name": "Dashboard", "desc": "Visualize KPIs, trends, and product/category insights.", "path": "Dashboard"},
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
                <div class='card'>
                    <h4>{page['name']}</h4>
                    <p>{page['desc']}</p>
                    <div class='nav-button'>
                        <a href='/{page['path']}' target='_self'><button>Go to {page['name']}</button></a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
