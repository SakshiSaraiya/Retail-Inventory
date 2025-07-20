import streamlit as st
import pandas as pd
from db import execute_query
from auth import check_login

# --------------------------
# Check if user is logged in
# --------------------------
check_login()
user_id = st.session_state.user_id

st.set_page_config(page_title="Upload Data", layout="wide")
st.markdown("<h2 style='color:#0F172A'>Upload Data</h2>", unsafe_allow_html=True)


# --------------------------
# Function to insert uploaded data into SQL
# --------------------------
def handle_csv_upload(label, table_name, required_columns):
    uploaded_file = st.file_uploader(f"Choose a {label} file", type=["csv"], key=label)
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)

            # Validate required columns
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                st.error(f"Missing columns: {', '.join(missing_cols)}")
                return

            df['user_id'] = user_id  # Add user ID

            # Insert rows into database
            for _, row in df.iterrows():
                cols = ", ".join(row.index)
                vals = tuple(row.values)
                placeholders = ", ".join(["%s"] * len(row))
                query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
                execute_query(query, vals)

            st.success(f"{label} uploaded successfully!")

        except Exception as e:
            st.error(f"Error uploading {label} data: {str(e)}")

# --------------------------
# Function to download sample CSVs
# --------------------------
def get_csv_download_button(label, df, filename):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f" Download Sample {label} CSV",
        data=csv,
        file_name=filename,
        mime='text/csv',
        use_container_width=True
    )

# --------------------------
# PRODUCT SECTION
# --------------------------
st.subheader("Upload or Enter Product Data")

product_sample = pd.DataFrame({
    "NAME": ["T-shirt"],
    "category": ["Clothing"],
    "cost_price": [200.0],
    "selling_price": [300.0],
    "stock": [50]
})
get_csv_download_button("Product", product_sample, "sample_products.csv")
handle_csv_upload("Product", "products", ["NAME", "category", "cost_price", "selling_price", "stock"])

with st.expander("➕ Add Product Manually"):
    with st.form("product_form"):
        name = st.text_input("Product Name")
        category = st.text_input("Category")
        cost_price = st.number_input("Cost Price", min_value=0.0)
        selling_price = st.number_input("Selling Price", min_value=0.0)
        stock = st.number_input("Stock", min_value=0)
        submit = st.form_submit_button("Add Product")
        if submit:
            query = """
                INSERT INTO Products (user_id, NAME, category, cost_price, selling_price, stock)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            execute_query(query, (user_id, name, category, cost_price, selling_price, stock))
            st.success("Product added successfully!")
st.markdown("</div>", unsafe_allow_html=True)

# --------------------------
# PURCHASE SECTION
# --------------------------
st.subheader(" Upload or Enter Purchase Data")

purchase_sample = pd.DataFrame({
    "product_id": [1],
    "vendor_name": ["Vendor A"],
    "quantity_purchased": [100],
    "cost_price": [150.0],
    "order_date": ["2025-07-20"],
    "payment_due": ["2025-08-01"],
    "payment_status": ["Pending"]
})
get_csv_download_button("Purchase", purchase_sample, "sample_purchases.csv")
handle_csv_upload("Purchase", "purchases",
                  ["product_id", "vendor_name", "quantity_purchased", "cost_price", "order_date", "payment_due", "payment_status"])

with st.expander("➕ Add Purchase Manually"):
    with st.form("purchase_form"):
        product_id = st.number_input("Product ID", min_value=1)
        vendor_name = st.text_input("Vendor Name")
        quantity_purchased = st.number_input("Quantity Purchased", min_value=1)
        cost_price = st.number_input("Cost Price", min_value=0.0)
        order_date = st.date_input("Order Date")
        payment_due = st.date_input("Payment Due Date")
        payment_status = st.selectbox("Payment Status", ["Pending", "Completed","Overdue"])
        submit = st.form_submit_button("Add Purchase")
        if submit:
            query = """
                INSERT INTO Purchases (user_id, product_id, vendor_name, quantity_purchased, cost_price, order_date, payment_due, payment_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            execute_query(query, (user_id, product_id, vendor_name, quantity_purchased, cost_price, order_date, payment_due, payment_status))
            st.success("Purchase added successfully!")
st.markdown("</div>", unsafe_allow_html=True)

# --------------------------
# SALES SECTION
# --------------------------
st.subheader(" Upload or Enter Sales Data")

sales_sample = pd.DataFrame({
    "product_id": [1],
    "quantity_sold": [10],
    "selling_price": [300.0],
    "sale_date": ["2025-07-20"],
    "shipped": ["Yes"],
    "payment_received": ["Yes"]
})
get_csv_download_button("Sales", sales_sample, "sample_sales.csv")
handle_csv_upload("Sales", "sales",
                  ["product_id", "quantity_sold", "selling_price", "sale_date", "shipped", "payment_received"])

with st.expander("➕ Add Sale Manually"):
    with st.form("sales_form"):
        product_id = st.number_input("Product ID", min_value=1, key="sale_pid")
        quantity_sold = st.number_input("Quantity Sold", min_value=1)
        selling_price = st.number_input("Selling Price", min_value=0.0)
        sale_date = st.date_input("Sale Date")
        shipped = st.selectbox("Shipped", ["Yes", "No"])
        payment_received = st.selectbox("Payment Received", ["Yes", "No"])
        submit = st.form_submit_button("Add Sale")
        if submit:
            query = """
                INSERT INTO Sales (user_id, product_id, quantity_sold, selling_price, sale_date, shipped, payment_received)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            execute_query(query, (user_id, product_id, quantity_sold, selling_price, sale_date, shipped, payment_received))
            st.success("Sale added successfully!")


# --------------------------
# Custom Styling
# --------------------------
st.markdown("""
<style>
   [data-testid="stSidebar"] {
        background-color: #0F172A !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    .stDownloadButton>button {
        background-color: #0F172A;
        color: white;
    }
    .card {
        background-color: white;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)
