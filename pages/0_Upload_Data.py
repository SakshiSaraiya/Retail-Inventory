import streamlit as st
from db import fetch_data, execute_query

st.set_page_config(page_title="📤 Upload Data", layout="wide")

if "user_id" not in st.session_state or not st.session_state.user_id:
    st.warning("Please log in to access the upload functionality.")
    st.stop()

st.title("📤 Upload Data")

# ---------- CSS Styling ----------
st.markdown("""
    <style>
    .card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        margin-bottom: 2rem;
    }
    h3 {
        color: #0F172A;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


# ---------- Upload Product ----------
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Add New Product")
    with st.form("product_form"):
        product_name = st.text_input("Product Name")
        category = st.text_input("Category")
        unit_price = st.number_input("Unit Price", min_value=0.0, step=0.01)
        stock_quantity = st.number_input("Initial Stock Quantity", min_value=0)

        submit_product = st.form_submit_button("Add Product")
        if submit_product:
            query = """
                INSERT INTO products (product_name, category, unit_price, stock_quantity)
                VALUES (%s, %s, %s, %s)
            """
            success = execute_query(query, (product_name, category, unit_price, stock_quantity))
            if success:
                st.success("✅ Product added successfully!")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Upload Purchase ----------
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Add New Purchase")
    with st.form("purchase_form"):
        # Get product options from DB
        products = fetch_data("SELECT product_id, product_name FROM products")
        product_options = {f"{p['product_name']} (ID: {p['product_id']})": p['product_id'] for p in products}

        selected_product = st.selectbox("Select Product", list(product_options.keys()))
        product_id = product_options[selected_product]

        quantity = st.number_input("Quantity Purchased", min_value=1)
        purchase_price = st.number_input("Purchase Price per Unit", min_value=0.0, step=0.01)
        purchase_date = st.date_input("Purchase Date")
        vendor_name = st.text_input("Vendor Name")

        submit_purchase = st.form_submit_button("Add Purchase")
        if submit_purchase:
            query = """
                INSERT INTO purchases (product_id, quantity_purchased, purchase_price, purchase_date, vendor_name)
                VALUES (%s, %s, %s, %s, %s)
            """
            success = execute_query(query, (product_id, quantity, purchase_price, purchase_date, vendor_name))
            if success:
                st.success("✅ Purchase record added successfully!")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Upload Sale ----------
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Add New Sale")
    with st.form("sales_form"):
        # Get product options again
        products = fetch_data("SELECT product_id, product_name FROM products")
        product_options = {f"{p['product_name']} (ID: {p['product_id']})": p['product_id'] for p in products}

        selected_product = st.selectbox("Select Product for Sale", list(product_options.keys()))
        product_id = product_options[selected_product]

        quantity = st.number_input("Quantity Sold", min_value=1)
        sale_price = st.number_input("Sale Price per Unit", min_value=0.0, step=0.01)
        sales_date = st.date_input("Sales Date")

        submit_sale = st.form_submit_button("Add Sale")
        if submit_sale:
            query = """
                INSERT INTO sales (product_id, quantity_sold, sale_price, sales_date)
                VALUES (%s, %s, %s, %s)
            """
            success = execute_query(query, (product_id, quantity, sale_price, sales_date))
            if success:
                st.success("✅ Sale record added successfully!")
    st.markdown("</div>", unsafe_allow_html=True)
