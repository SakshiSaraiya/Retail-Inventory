import streamlit as st
import datetime
from auth import register_user, login_user
import pandas as pd
import plotly.express as px
from db import get_connection, fetch_data, execute_query


if st.session_state.get("scroll_to_top", False):
    st.markdown(
        """
        <script>
        setTimeout(function() {
            window.scrollTo({top: 0, behavior: 'smooth'});
        }, 500);
        </script>
        """,
        unsafe_allow_html=True
    )
    st.session_state["scroll_to_top"] = False

# --- Branding with Logo (always visible) ---
st.markdown("<div style='text-align:left;margin-top:-5rem;'><h1 style='font-size:3.0rem;color:#0F172A;font-weight:700;letter-spacing:1px;margin-bottom:0.4rem;position:relative;left:-130px;bottom:-30px;'>Welcome to Retail Pulse</h1><div style='font-size:1.15rem;color:#475569;margin-bottom:1.5rem;font-weight:400;position:relative;left:-160px;top:10px;'>Insightful Retail & Smarter Decisions.</div></div>", unsafe_allow_html=True)

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

st.markdown("""
    <style>
    /* Style the Streamlit tabs */
    .stTabs [data-baseweb="tab"] {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        color: #000 !important;
        padding: 0.75rem 2.5rem !important;
        margin-right: 8px !important;
        transition: background 0.2s, color 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background: #0F172A !important;
        color: #fff !important;
        box-shadow: 0 4px 16px rgba(59,130,246,0.10);
    }
    </style>
""", unsafe_allow_html=True)

# --- Key Features Section (before login) ---
def show_features():
    st.markdown("""
        <style>
        .landing-hero {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 1.5rem;
            margin-bottom: 2.5rem;
        }
        .hero-illustration {
            font-size: 3.5rem;
            margin-bottom: 1.2rem;
            filter: drop-shadow(0 4px 16px rgba(37,99,235,0.10));
        }
        .features-row {
            display: flex;
            gap: 2.5rem;
            justify-content: center;
            margin-bottom: 2.5rem;
        }
        .feature-card {
            background: #fff;
            padding: 2rem 1.5rem 1.2rem 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(30,41,59,0.08);
            width: 260px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .feature-card .icon {
            font-size: 2.5rem;
            margin-bottom: 0.8rem;
        }
        .feature-card .title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 0.4rem;
        }
        .feature-card .desc {
            font-size: 1rem;
            color: #475569;
            text-align: center;
        }
        .landing-bg {
            background: linear-gradient(120deg, #f8fafc 0%, #e0e7ef 100%);
            min-height: 350px;
            border-radius: 24px;
            margin: 0 auto 2.5rem auto;
            max-width: 900px;
            box-shadow: 0 8px 32px rgba(30,41,59,0.06);
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div class='landing-bg'>
            <div class='landing-hero'>
                <div class='hero-illustration'>🛒📦📈</div>
                <div style='font-size:1.35rem;font-weight:700;color:#1E293B;margin-bottom:2.2rem;'>Why Choose Retail Pulse?</div>
                <div class='features-row'>
                    <div class='feature-card'>
                        <div class='icon'>📦</div>
                        <div class='title'>Inventory Management</div>
                        <div class='desc'>Track stock levels, categories, and get reorder alerts.</div>
                    </div>
                    <div class='feature-card'>
                        <div class='icon'>📊</div>
                        <div class='title'>Sales & Profit Analysis</div>
                        <div class='desc'>Visual dashboards for revenue and trends.</div>
                    </div>
        <div class='feature-card'>
                        <div class='icon'>💸</div>
                        <div class='title'>Expense Tracking</div>
                        <div class='desc'>Monitor and control your business expenses efficiently.</div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- Dashboard (Styled) ---
def show_dashboard():
    import datetime
    today = datetime.datetime.now().strftime('%A, %d %B %Y')
    # --- Dashboard Cards (fetch real data) ---
    user_id = st.session_state["user_id"]
    conn = get_connection()
    total_products, total_sales, total_expenses = 0, 0, 0
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Products WHERE user_id = %s", (user_id,))
        total_products = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(quantity_sold * selling_price) FROM Sales WHERE user_id = %s", (user_id,))
        total_sales = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(amount) FROM Expenses WHERE user_id = %s", (user_id,))
        total_expenses = cursor.fetchone()[0] or 0
        cursor.close()
        conn.close()

    # --- Render dashboard CSS ---
    st.markdown("""
        <style>
        .main-dashboard-card {
            background: #fff;
            border-radius: 22px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.10);
            padding: 2.5rem 2.5rem 1.5rem 2.5rem;
            margin: 2rem auto 2.5rem auto;
            max-width: 800px;
        }
        .dashboard-cards {display: flex; gap: 2rem; margin-bottom: 2.5rem;}
        .dashboard-card {
            background: #eaf1fb;
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(30,41,59,0.08);
            flex: 1;
            padding: 2rem 1.5rem 1.5rem 1.5rem;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            min-width: 180px;
        }
        .dashboard-card .icon {font-size: 2.2rem; margin-bottom: 0.7rem;}
        .dashboard-card .label {font-size: 1.1rem; color: #475569; font-weight: 600; margin-bottom: 0.2rem;}
        .dashboard-card .value {font-size: 2rem; font-weight: 800; color: #1a2233;}
        .quick-actions-row {margin-bottom: 2.5rem;}
        div[data-testid="column"] > div > button:first-child {
            background: #2563eb !important;
            color: #fff !important;
        }
        div[data-testid="column"] > div > button:nth-child(2) {
            background: #22c55e !important;
            color: #fff !important;
        }
        div[data-testid="column"] > div > button:nth-child(3) {
            background: #f59e42 !important;
            color: #fff !important;
        }
        .stButton>button {
            font-weight: 700 !important;
            font-size: 1.08rem !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.8rem 1.7rem !important;
            box-shadow: 0 2px 8px rgba(37,99,235,0.08) !important;
            transition: background 0.2s;
            margin: 0.5rem 0;
        }
        .stButton>button:hover {
            background: #1a2233 !important;
            color: #fff !important;
        }
        .welcome-banner {
            background: #eaf1fb;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(30,41,59,0.06);
            padding: 1.5rem 2rem 1.2rem 2rem;
            margin-bottom: 2.2rem;
            display: flex; align-items: center; gap: 1.5rem;
        }
        .welcome-banner .icon {font-size: 2.5rem; margin-right: 1.2rem;}
        .welcome-banner .main {flex: 1;}
        .welcome-banner .main .greeting {font-size: 1.2rem; font-weight: 700; color: #1a2233; margin-bottom: 0.2rem;}
        .welcome-banner .main .date {font-size: 1.05rem; color: #2563eb; margin-bottom: 0.5rem;}
        .welcome-banner .main .health {font-size: 1.05rem; color: #22c55e; margin-bottom: 0.5rem;}
        .welcome-banner .main .quote {font-size: 1.05rem; color: #475569; font-style: italic;}
        .tips-card {
            background: #f8fafc;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(30,41,59,0.08);
            padding: 1.5rem 2rem;
            margin-bottom: 2rem;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
            font-size: 1.08rem;
            color: #334155;
        }
        .tips-card .tips-title {
            font-weight: 700;
            color: #2563eb;
            margin-bottom: 0.5rem;
            font-size: 1.15rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Render dashboard card and content ---
    st.markdown(f"""
        <div class='main-dashboard-card'>
            <div class='welcome-banner'>
                <span class='icon'>🛍️</span>
                <div class='main'>
                    <div class='greeting'>Welcome back, <span style='color:#2563eb;'>User</span>!</div>
                    <div class='date'>{today}</div>
                    <div class='health'><b>Business Health:</b> All systems normal</div>
                    <div class='quote'>“Opportunities don't happen. You create them.”</div>
                </div>
            </div>
            <div class='dashboard-cards'>
                <div class='dashboard-card'><span class='icon'>🛒</span><div class='label'>Total Products</div><div class='value'>{total_products}</div></div>
                <div class='dashboard-card'><span class='icon'>💰</span><div class='label'>Total Sales</div><div class='value'>₹{total_sales:,.2f}</div></div>
                <div class='dashboard-card'><span class='icon'>📉</span><div class='label'>Total Expenses</div><div class='value'>₹{total_expenses:,.2f}</div></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- Quick Actions (aligned, colored, with icons) ---
    st.markdown("<div class='quick-actions-row'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🛒 + Add Product"):
            st.session_state["show_add_product"] = True
    with col2:
        if st.button("📦 + Add Purchase"):
            st.session_state["show_add_purchase"] = True
    with col3:
        if st.button("💰 + Add Sale"):
            st.session_state["show_add_sale"] = True
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Add Product Form ---
    if st.session_state.get("show_add_product"):
        with st.form("add_product_form"):
            st.subheader("Add Product")
            name = st.text_input("Product Name")
            category = st.text_input("Category")
            cost_price = st.number_input("Cost Price", min_value=0.0, key="prod_cost")
            selling_price = st.number_input("Selling Price", min_value=0.0, key="prod_sell")
            stock = st.number_input("Stock", min_value=0)
            submit = st.form_submit_button("Submit Product")
            if submit:
                query = """
                    INSERT INTO Products (user_id, NAME, category, cost_price, selling_price, stock)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                execute_query(query, (user_id, name, category, cost_price, selling_price, stock))
                st.success("Product added successfully!")
                st.session_state["show_add_product"] = False
                st.rerun()

    # --- Add Purchase Form ---
    if st.session_state.get("show_add_purchase"):
        with st.form("add_purchase_form"):
            st.subheader("Add Purchase")
            product_id = st.number_input("Product ID", min_value=1, key="purchase_pid")
            vendor_name = st.text_input("Vendor Name")
            quantity_purchased = st.number_input("Quantity Purchased", min_value=1)
            cost_price = st.number_input("Cost Price", min_value=0.0)
            order_date = st.date_input("Order Date")
            payment_due = st.date_input("Payment Due Date")
            payment_status = st.selectbox("Payment Status", ["Pending", "Completed", "Overdue"])
            submit = st.form_submit_button("Submit Purchase")
            if submit:
                query = """
                    INSERT INTO Purchases (user_id, product_id, vendor_name, quantity_purchased, cost_price, order_date, payment_due, payment_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                execute_query(query, (user_id, product_id, vendor_name, quantity_purchased, cost_price, order_date, payment_due, payment_status))
                st.success("Purchase added successfully!")
                st.session_state["show_add_purchase"] = False
                st.rerun()

    # --- Add Sale Form ---
    if st.session_state.get("show_add_sale"):
        with st.form("add_sale_form"):
            st.subheader("Add Sale")
            product_id = st.number_input("Product ID", min_value=1)
            quantity_sold = st.number_input("Quantity Sold", min_value=1)
            selling_price = st.number_input("Selling Price", min_value=0.0)
            sale_date = st.date_input("Sale Date")
            shipped = st.selectbox("Shipped", ["Yes", "No"])
            payment_received = st.selectbox("Payment Received", ["Yes", "No"])
            submit = st.form_submit_button("Submit Sale")
            if submit:
                shipped_value = 1 if shipped == "Yes" else 0
                payment_received_value = 1 if payment_received == "Yes" else 0
                query = """
                    INSERT INTO Sales (user_id, product_id, quantity_sold, selling_price, sale_date, shipped, payment_received)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                execute_query(query, (user_id, product_id, quantity_sold, selling_price, sale_date, shipped_value, payment_received_value))
                st.success("Sale added successfully!")
                st.session_state["show_add_sale"] = False
                st.rerun()

    # --- Tips & Insights Card ---
    st.markdown("""
        <div class='tips-card'>
            <div class='tips-title'>💡 Tips & Insights</div>
            <ul style='margin:0 0 0 1.2rem;padding:0;'>
                <li>Use the sidebar to quickly navigate between Inventory, Sales, and Purchases modules.</li>
                <li>Keep your product stock updated to avoid missed sales opportunities.</li>
                <li>Analyze your sales and expenses regularly to maximize profit.</li>
                <li>Set reorder alerts for fast-moving products to prevent stockouts.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# --- Authentication ---
def show_auth():
    login_tab, register_tab = st.tabs(["🔐 Login", "📝 Register"])
    with login_tab:
        st.subheader("Login")
        username_or_email = st.text_input("Username or Email")
        password = st.text_input("Password", type="password", key="login_password")
        login_submit = st.button("Login")
        st.session_state["scroll_to_top"] = False
        if login_submit:
            success, user_id = login_user(username_or_email, password)
            if success:
                st.session_state["is_logged_in"] = True
                st.session_state["user_id"] = user_id
                st.session_state["scroll_to_top"] = True
                st.rerun()
                st.success("Login successful!")

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

# --- Main App Logic ---
if not st.session_state.get("is_logged_in", False):
    show_features()
    show_auth()
else:
    show_dashboard()
