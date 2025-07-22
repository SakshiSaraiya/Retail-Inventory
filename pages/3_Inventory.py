import streamlit as st  
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db import get_connection, execute_query
from auth import check_login

# -------------------------
# Page Config and Authentication
# -------------------------
st.set_page_config(
    page_title="📦 Inventory Management | RetailPro",
    page_icon="📦",
    layout="wide"
)

check_login()
user_id = st.session_state.user_id

# -------------------------
# Professional Styling
# -------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .page-header {
        text-align: center;
        padding: 2rem 0;
        border-bottom: 1px solid #e1e8ed;
        margin-bottom: 2rem;
    }
    
    .page-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .page-subtitle {
        font-size: 1.1rem;
        color: #64748b;
        font-weight: 400;
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 2rem 1.5rem;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        border: 1px solid #f1f5f9;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        text-align: center;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.12);
    }
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.95rem;
        color: #64748b;
        font-weight: 500;
    }
    
    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e293b;
        margin: 2rem 0 1rem 0;
        position: relative;
        padding-left: 1rem;
    }
    
    .section-title::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 2px;
    }
    
    .form-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        border: 1px solid #f1f5f9;
        margin: 1.5rem 0;
    }
    
    .form-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .alert-card {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 1px solid #f87171;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
    }
    
    .alert-title {
        font-weight: 600;
        color: #dc2626;
        margin-bottom: 0.5rem;
    }
    
    .alert-content {
        color: #b91c1c;
        font-size: 0.9rem;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #f59e0b;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
    }
    
    .warning-title {
        font-weight: 600;
        color: #92400e;
        margin-bottom: 0.5rem;
    }
    
    .warning-content {
        color: #b45309;
        font-size: 0.9rem;
    }
    
    .success-card {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 1px solid #10b981;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
    }
    
    .success-title {
        font-weight: 600;
        color: #065f46;
        margin-bottom: 0.5rem;
    }
    
    .success-content {
        color: #047857;
        font-size: 0.9rem;
    }
    
    .data-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        border: 1px solid #f1f5f9;
        margin: 1.5rem 0;
    }
    
    .data-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f1f5f9;
    }
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# -------------------------
# Data Functions
# -------------------------
@st.cache_data(ttl=300)
def fetch_inventory_data(user_id):
    conn = get_connection()
    if not conn:
        return None, None, None, None
    
    # Get products with current stock
    products_df = pd.read_sql("""
        SELECT product_id, name, category, cost_price, selling_price, 
               stock_quantity, reorder_level, description
        FROM Products 
        WHERE user_id = %s
        ORDER BY name
    """, conn, params=(user_id,))
    
    # Calculate metrics
    total_products = len(products_df)
    total_value = (products_df['stock_quantity'] * products_df['cost_price']).sum() if not products_df.empty else 0
    low_stock_count = len(products_df[products_df['stock_quantity'] <= products_df['reorder_level']]) if not products_df.empty else 0
    out_of_stock_count = len(products_df[products_df['stock_quantity'] == 0]) if not products_df.empty else 0
    
    conn.close()
    
    return products_df, total_products, total_value, low_stock_count, out_of_stock_count

def add_product(user_id, name, category, cost_price, selling_price, stock_quantity, reorder_level, description):
    query = """
        INSERT INTO Products (user_id, name, category, cost_price, selling_price, 
                            stock_quantity, reorder_level, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    return execute_query(query, (user_id, name, category, cost_price, selling_price, 
                                stock_quantity, reorder_level, description))

def update_stock(product_id, new_quantity):
    query = "UPDATE Products SET stock_quantity = %s WHERE product_id = %s"
    return execute_query(query, (new_quantity, product_id))

# -------------------------
# Main Content
# -------------------------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="page-header">
        <h1 class="page-title">📦 Inventory Management</h1>
        <p class="page-subtitle">Monitor stock levels, add products, and manage your inventory efficiently</p>
    </div>
""", unsafe_allow_html=True)

# Fetch inventory data
products_df, total_products, total_value, low_stock_count, out_of_stock_count = fetch_inventory_data(user_id)

if products_df is not None:
    # Key Metrics
    st.markdown("""
        <div class="metrics-grid">
            <div class="metric-card">
                <span class="metric-icon">📦</span>
                <div class="metric-value">{}</div>
                <div class="metric-label">Total Products</div>
            </div>
            <div class="metric-card">
                <span class="metric-icon">💵</span>
                <div class="metric-value">₹{:,.0f}</div>
                <div class="metric-label">Inventory Value</div>
            </div>
            <div class="metric-card">
                <span class="metric-icon">⚠️</span>
                <div class="metric-value">{}</div>
                <div class="metric-label">Low Stock Items</div>
            </div>
            <div class="metric-card">
                <span class="metric-icon">🚫</span>
                <div class="metric-value">{}</div>
                <div class="metric-label">Out of Stock</div>
            </div>
        </div>
    """.format(total_products, total_value, low_stock_count, out_of_stock_count), unsafe_allow_html=True)
    
    # Alerts
    if out_of_stock_count > 0:
        st.markdown(f"""
            <div class="alert-card">
                <div class="alert-title">🚫 Critical Alert</div>
                <div class="alert-content">{out_of_stock_count} products are completely out of stock!</div>
            </div>
        """, unsafe_allow_html=True)
    
    if low_stock_count > 0:
        st.markdown(f"""
            <div class="warning-card">
                <div class="warning-title">⚠️ Stock Warning</div>
                <div class="warning-content">{low_stock_count} products are running low on stock.</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["📊 View Inventory", "➕ Add Product", "🔄 Update Stock"])
    
    with tab1:
        st.markdown('<h2 class="section-title">📊 Current Inventory</h2>', unsafe_allow_html=True)
        
        if not products_df.empty:
            # Add search and filter options
            col1, col2 = st.columns([2, 1])
            with col1:
                search_term = st.text_input("🔍 Search products", placeholder="Enter product name or category...")
            with col2:
                category_filter = st.selectbox("Filter by Category", 
                                             ["All Categories"] + list(products_df['category'].unique()) if 'category' in products_df.columns else ["All Categories"])
            
            # Filter data
            filtered_df = products_df.copy()
            if search_term:
                filtered_df = filtered_df[filtered_df['name'].str.contains(search_term, case=False, na=False)]
            if category_filter != "All Categories":
                filtered_df = filtered_df[filtered_df['category'] == category_filter]
            
            # Display inventory table
            st.markdown('<div class="data-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="data-title">Product Inventory</h3>', unsafe_allow_html=True)
            
            if not filtered_df.empty:
                # Format for display
                display_df = filtered_df.copy()
                display_df['Cost Price'] = display_df['cost_price'].apply(lambda x: f"₹{x:,.2f}")
                display_df['Selling Price'] = display_df['selling_price'].apply(lambda x: f"₹{x:,.2f}")
                display_df['Stock Value'] = (display_df['stock_quantity'] * display_df['cost_price']).apply(lambda x: f"₹{x:,.2f}")
                
                # Add status column
                def get_status(row):
                    if row['stock_quantity'] == 0:
                        return "🚫 Out of Stock"
                    elif row['stock_quantity'] <= row['reorder_level']:
                        return "⚠️ Low Stock"
                    else:
                        return "✅ In Stock"
                
                display_df['Status'] = display_df.apply(get_status, axis=1)
                
                # Select columns to display
                display_columns = ['name', 'category', 'stock_quantity', 'reorder_level', 
                                 'Cost Price', 'Selling Price', 'Stock Value', 'Status']
                final_df = display_df[display_columns]
                final_df.columns = ['Product Name', 'Category', 'Current Stock', 'Reorder Level', 
                                  'Cost Price', 'Selling Price', 'Stock Value', 'Status']
                
                st.dataframe(final_df, use_container_width=True, hide_index=True)
                
                # Stock level visualization
                if len(filtered_df) <= 20:  # Only show chart for reasonable number of products
                    st.markdown('<h3 class="data-title">Stock Levels Visualization</h3>', unsafe_allow_html=True)
                    
                    fig = px.bar(
                        filtered_df, 
                        x='name', 
                        y='stock_quantity',
                        color='stock_quantity',
                        color_continuous_scale='RdYlGn',
                        title="",
                        labels={'stock_quantity': 'Stock Quantity', 'name': 'Product'}
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_family="Inter",
                        xaxis_tickangle=-45,
                        margin=dict(l=0, r=0, t=0, b=0),
                        coloraxis_showscale=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No products found matching your search criteria.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No products in inventory. Add your first product using the 'Add Product' tab.")
    
    with tab2:
        st.markdown('<h2 class="section-title">➕ Add New Product</h2>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="form-title">Product Information</h3>', unsafe_allow_html=True)
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Product Name*", placeholder="Enter product name")
                category = st.text_input("Category*", placeholder="e.g., Electronics, Clothing")
                cost_price = st.number_input("Cost Price (₹)*", min_value=0.0, step=0.01, format="%.2f")
                selling_price = st.number_input("Selling Price (₹)*", min_value=0.0, step=0.01, format="%.2f")
            
            with col2:
                stock_quantity = st.number_input("Initial Stock Quantity*", min_value=0, step=1)
                reorder_level = st.number_input("Reorder Level*", min_value=0, step=1, 
                                               help="Stock level at which you want to be alerted")
                description = st.text_area("Description", placeholder="Enter product description (optional)")
            
            submit_button = st.form_submit_button("🛍️ Add Product", use_container_width=True)
            
            if submit_button:
                if name and category and cost_price >= 0 and selling_price >= 0:
                    success = add_product(user_id, name, category, cost_price, selling_price, 
                                        stock_quantity, reorder_level, description)
                    if success:
                        st.markdown("""
                            <div class="success-card">
                                <div class="success-title">✅ Success!</div>
                                <div class="success-content">Product added successfully to inventory.</div>
                            </div>
                        """, unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.error("❌ Failed to add product. Please try again.")
                else:
                    st.warning("⚠️ Please fill in all required fields.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<h2 class="section-title">🔄 Update Stock Quantities</h2>', unsafe_allow_html=True)
        
        if not products_df.empty:
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="form-title">Stock Management</h3>', unsafe_allow_html=True)
            
            # Select product
            product_names = dict(zip(products_df['name'], products_df['product_id']))
            selected_product_name = st.selectbox("Select Product", list(product_names.keys()))
            
            if selected_product_name:
                selected_product_id = product_names[selected_product_name]
                current_stock = products_df[products_df['product_id'] == selected_product_id]['stock_quantity'].iloc[0]
                reorder_level = products_df[products_df['product_id'] == selected_product_id]['reorder_level'].iloc[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"Current Stock: **{current_stock}** units")
                with col2:
                    st.info(f"Reorder Level: **{reorder_level}** units")
                
                # Update stock
                with st.form("update_stock_form"):
                    new_quantity = st.number_input("New Stock Quantity", 
                                                 min_value=0, 
                                                 value=int(current_stock), 
                                                 step=1)
                    
                    reason = st.selectbox("Reason for Update", 
                                        ["Stock Adjustment", "New Purchase", "Stock Return", "Damage/Loss", "Other"])
                    
                    update_button = st.form_submit_button("🔄 Update Stock", use_container_width=True)
                    
                    if update_button:
                        success = update_stock(selected_product_id, new_quantity)
                        if success:
                            st.markdown("""
                                <div class="success-card">
                                    <div class="success-title">✅ Stock Updated!</div>
                                    <div class="success-content">Stock quantity updated successfully.</div>
                                </div>
                            """, unsafe_allow_html=True)
                            st.rerun()
                        else:
                            st.error("❌ Failed to update stock. Please try again.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No products available. Add products first to manage stock.")

else:
    st.error("❌ Unable to fetch inventory data. Please check your database connection.")

st.markdown('</div>', unsafe_allow_html=True)
