import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from db import get_connection, execute_query, fetch_data
from auth import check_login

# -------------------------
# Page Config and Authentication
# -------------------------
st.set_page_config(
    page_title="💰 Sales Management | RetailPro",
    page_icon="💰",
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
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
    
    .metric-change {
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .metric-change.positive {
        color: #059669;
    }
    
    .metric-change.negative {
        color: #dc2626;
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
    
    .chart-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        border: 1px solid #f1f5f9;
        margin: 1.5rem 0;
    }
    
    .chart-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f1f5f9;
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
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stDateInput > div > div > input {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div:focus-within,
    .stDateInput > div > div > input:focus {
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
def fetch_sales_data(user_id):
    conn = get_connection()
    if not conn:
        return None, None, None, None, None
    
    # Sales metrics
    cursor = conn.cursor()
    
    # Total sales
    cursor.execute("SELECT SUM(quantity_sold * selling_price) FROM Sales WHERE user_id = %s", (user_id,))
    total_revenue = cursor.fetchone()[0] or 0
    
    # Total units sold
    cursor.execute("SELECT SUM(quantity_sold) FROM Sales WHERE user_id = %s", (user_id,))
    total_units = cursor.fetchone()[0] or 0
    
    # Number of transactions
    cursor.execute("SELECT COUNT(*) FROM Sales WHERE user_id = %s", (user_id,))
    total_transactions = cursor.fetchone()[0] or 0
    
    # Today's sales
    cursor.execute("""
        SELECT SUM(quantity_sold * selling_price) 
        FROM Sales 
        WHERE user_id = %s AND DATE(sale_date) = CURDATE()
    """, (user_id,))
    today_sales = cursor.fetchone()[0] or 0
    
    # Sales data for charts
    sales_df = pd.read_sql("""
        SELECT s.sale_id, s.sale_date, s.quantity_sold, s.selling_price,
               s.quantity_sold * s.selling_price as total_amount,
               p.name as product_name, p.category
        FROM Sales s
        JOIN Products p ON s.product_id = p.product_id
        WHERE s.user_id = %s
        ORDER BY s.sale_date DESC
    """, conn, params=(user_id,))
    
    # Products available for sale
    products_df = pd.read_sql("""
        SELECT product_id, name, selling_price, stock_quantity
        FROM Products 
        WHERE user_id = %s AND stock_quantity > 0
        ORDER BY name
    """, conn, params=(user_id,))
    
    cursor.close()
    conn.close()
    
    return total_revenue, total_units, total_transactions, today_sales, sales_df, products_df

def record_sale(user_id, product_id, quantity_sold, selling_price, sale_date):
    query = """
        INSERT INTO Sales (user_id, product_id, quantity_sold, selling_price, sale_date)
        VALUES (%s, %s, %s, %s, %s)
    """
    success = execute_query(query, (user_id, product_id, quantity_sold, selling_price, sale_date))
    
    if success:
        # Update product stock
        update_query = """
            UPDATE Products 
            SET stock_quantity = stock_quantity - %s 
            WHERE product_id = %s AND user_id = %s
        """
        execute_query(update_query, (quantity_sold, product_id, user_id))
    
    return success

# -------------------------
# Main Content
# -------------------------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="page-header">
        <h1 class="page-title">💰 Sales Management</h1>
        <p class="page-subtitle">Track sales performance, record transactions, and analyze revenue trends</p>
    </div>
""", unsafe_allow_html=True)

# Fetch sales data
total_revenue, total_units, total_transactions, today_sales, sales_df, products_df = fetch_sales_data(user_id)

if total_revenue is not None:
    # Calculate additional metrics
    avg_transaction_value = total_revenue / total_transactions if total_transactions > 0 else 0
    
    # Yesterday's sales for comparison
    yesterday_sales = 0
    if not sales_df.empty:
        yesterday_date = (datetime.now() - timedelta(days=1)).date()
        yesterday_sales = sales_df[sales_df['sale_date'].dt.date == yesterday_date]['total_amount'].sum()
    
    daily_change = today_sales - yesterday_sales
    daily_change_percent = (daily_change / yesterday_sales * 100) if yesterday_sales > 0 else 0
    
    # Key Metrics
    st.markdown("""
        <div class="metrics-grid">
            <div class="metric-card">
                <span class="metric-icon">💰</span>
                <div class="metric-value">₹{:,.0f}</div>
                <div class="metric-label">Total Revenue</div>
            </div>
            <div class="metric-card">
                <span class="metric-icon">📦</span>
                <div class="metric-value">{:,}</div>
                <div class="metric-label">Units Sold</div>
            </div>
            <div class="metric-card">
                <span class="metric-icon">🧾</span>
                <div class="metric-value">{}</div>
                <div class="metric-label">Total Transactions</div>
            </div>
            <div class="metric-card">
                <span class="metric-icon">📊</span>
                <div class="metric-value">₹{:,.0f}</div>
                <div class="metric-label">Avg Transaction</div>
            </div>
            <div class="metric-card">
                <span class="metric-icon">📅</span>
                <div class="metric-value">₹{:,.0f}</div>
                <div class="metric-label">Today's Sales</div>
                <div class="metric-change {}">{}{:.1f}%</div>
            </div>
        </div>
    """.format(
        total_revenue,
        total_units,
        total_transactions,
        avg_transaction_value,
        today_sales,
        "positive" if daily_change >= 0 else "negative",
        "↗ " if daily_change >= 0 else "↘ ",
        abs(daily_change_percent)
    ), unsafe_allow_html=True)
    
    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["📊 Sales Analytics", "➕ Record Sale", "📋 Sales History"])
    
    with tab1:
        st.markdown('<h2 class="section-title">📈 Sales Performance Analytics</h2>', unsafe_allow_html=True)
        
        if not sales_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<h3 class="chart-title">Daily Sales Trend (Last 30 Days)</h3>', unsafe_allow_html=True)
                
                # Daily sales trend
                daily_sales = sales_df.copy()
                daily_sales['date'] = daily_sales['sale_date'].dt.date
                daily_sales_agg = daily_sales.groupby('date')['total_amount'].sum().reset_index()
                daily_sales_agg = daily_sales_agg.tail(30)  # Last 30 days
                
                fig_daily = px.line(
                    daily_sales_agg,
                    x='date',
                    y='total_amount',
                    title="",
                    color_discrete_sequence=['#667eea']
                )
                fig_daily.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_family="Inter",
                    xaxis_title="Date",
                    yaxis_title="Sales (₹)",
                    showlegend=False,
                    margin=dict(l=0, r=0, t=0, b=0)
                )
                fig_daily.update_traces(line_width=3)
                st.plotly_chart(fig_daily, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<h3 class="chart-title">Sales by Category</h3>', unsafe_allow_html=True)
                
                # Category-wise sales
                category_sales = sales_df.groupby('category')['total_amount'].sum().reset_index()
                
                fig_category = px.pie(
                    category_sales,
                    values='total_amount',
                    names='category',
                    title="",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_category.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_family="Inter",
                    showlegend=True,
                    margin=dict(l=0, r=0, t=0, b=0)
                )
                st.plotly_chart(fig_category, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Top performing products
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">Top Performing Products</h3>', unsafe_allow_html=True)
            
            product_performance = sales_df.groupby('product_name').agg({
                'total_amount': 'sum',
                'quantity_sold': 'sum'
            }).reset_index().sort_values('total_amount', ascending=False).head(10)
            
            fig_products = px.bar(
                product_performance,
                x='total_amount',
                y='product_name',
                orientation='h',
                title="",
                color='total_amount',
                color_continuous_scale='viridis'
            )
            fig_products.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter",
                xaxis_title="Revenue (₹)",
                yaxis_title="Product",
                showlegend=False,
                margin=dict(l=0, r=0, t=0, b=0),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_products, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No sales data available yet. Record your first sale to see analytics.")
    
    with tab2:
        st.markdown('<h2 class="section-title">➕ Record New Sale</h2>', unsafe_allow_html=True)
        
        if not products_df.empty:
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="form-title">Sale Transaction</h3>', unsafe_allow_html=True)
            
            with st.form("record_sale_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Product selection
                    product_options = dict(zip(products_df['name'], products_df['product_id']))
                    selected_product_name = st.selectbox("Select Product*", list(product_options.keys()))
                    
                    if selected_product_name:
                        selected_product = products_df[products_df['name'] == selected_product_name].iloc[0]
                        max_quantity = int(selected_product['stock_quantity'])
                        default_price = float(selected_product['selling_price'])
                        
                        st.info(f"Available Stock: **{max_quantity}** units")
                        
                        quantity_sold = st.number_input(
                            "Quantity Sold*", 
                            min_value=1, 
                            max_value=max_quantity,
                            step=1,
                            help=f"Maximum available: {max_quantity} units"
                        )
                        
                        selling_price = st.number_input(
                            "Selling Price per Unit (₹)*", 
                            min_value=0.01, 
                            value=default_price,
                            step=0.01, 
                            format="%.2f"
                        )
                
                with col2:
                    sale_date = st.date_input("Sale Date*", value=datetime.now().date())
                    
                    # Calculate totals
                    if 'quantity_sold' in locals() and 'selling_price' in locals():
                        total_amount = quantity_sold * selling_price
                        st.metric("Total Amount", f"₹{total_amount:,.2f}")
                        
                        if selling_price != default_price:
                            price_diff = selling_price - default_price
                            st.metric("Price Difference", f"₹{price_diff:,.2f}")
                
                submit_button = st.form_submit_button("💰 Record Sale", use_container_width=True)
                
                if submit_button:
                    if selected_product_name and quantity_sold > 0 and selling_price > 0:
                        product_id = product_options[selected_product_name]
                        success = record_sale(user_id, product_id, quantity_sold, selling_price, sale_date)
                        
                        if success:
                            st.markdown("""
                                <div class="success-card">
                                    <div class="success-title">✅ Sale Recorded!</div>
                                    <div class="success-content">Sale transaction recorded successfully. Stock updated.</div>
                                </div>
                            """, unsafe_allow_html=True)
                            st.rerun()
                        else:
                            st.error("❌ Failed to record sale. Please try again.")
                    else:
                        st.warning("⚠️ Please fill in all required fields.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ No products available for sale. Please add products to your inventory first.")
    
    with tab3:
        st.markdown('<h2 class="section-title">📋 Sales Transaction History</h2>', unsafe_allow_html=True)
        
        if not sales_df.empty:
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                date_range = st.date_input(
                    "Filter by Date Range",
                    value=[sales_df['sale_date'].min().date(), sales_df['sale_date'].max().date()],
                    help="Select start and end dates"
                )
            with col2:
                category_filter = st.selectbox(
                    "Filter by Category",
                    ["All Categories"] + list(sales_df['category'].unique())
                )
            with col3:
                product_filter = st.selectbox(
                    "Filter by Product",
                    ["All Products"] + list(sales_df['product_name'].unique())
                )
            
            # Apply filters
            filtered_sales = sales_df.copy()
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_sales = filtered_sales[
                    (filtered_sales['sale_date'].dt.date >= start_date) &
                    (filtered_sales['sale_date'].dt.date <= end_date)
                ]
            
            if category_filter != "All Categories":
                filtered_sales = filtered_sales[filtered_sales['category'] == category_filter]
            
            if product_filter != "All Products":
                filtered_sales = filtered_sales[filtered_sales['product_name'] == product_filter]
            
            # Display filtered data
            st.markdown('<div class="data-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="data-title">Sales Transactions</h3>', unsafe_allow_html=True)
            
            if not filtered_sales.empty:
                # Format for display
                display_df = filtered_sales.copy()
                display_df['Sale Date'] = display_df['sale_date'].dt.strftime('%Y-%m-%d')
                display_df['Unit Price'] = display_df['selling_price'].apply(lambda x: f"₹{x:,.2f}")
                display_df['Total Amount'] = display_df['total_amount'].apply(lambda x: f"₹{x:,.2f}")
                
                final_df = display_df[['Sale Date', 'product_name', 'category', 'quantity_sold', 'Unit Price', 'Total Amount']]
                final_df.columns = ['Date', 'Product', 'Category', 'Quantity', 'Unit Price', 'Total Amount']
                
                st.dataframe(final_df, use_container_width=True, hide_index=True)
                
                # Summary statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Records", len(filtered_sales))
                with col2:
                    st.metric("Total Revenue", f"₹{filtered_sales['total_amount'].sum():,.2f}")
                with col3:
                    st.metric("Total Units", f"{filtered_sales['quantity_sold'].sum():,}")
            else:
                st.info("No sales records found for the selected filters.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No sales history available. Record your first sale to see transaction history.")

else:
    st.error("❌ Unable to fetch sales data. Please check your database connection.")

st.markdown('</div>', unsafe_allow_html=True)
