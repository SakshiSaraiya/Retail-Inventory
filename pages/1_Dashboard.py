import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from db import get_connection
from auth import check_login
import datetime

# -------------------------------
# Page Config and Authentication
# -------------------------------
st.set_page_config(
    page_title="📊 Analytics Dashboard | RetailPro",
    page_icon="📊",
    layout="wide"
)

check_login()
user_id = st.session_state.user_id

# -------------------------------
# Professional Styling
# -------------------------------
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
    
    .dashboard-header {
        text-align: center;
        padding: 2rem 0;
        border-bottom: 1px solid #e1e8ed;
        margin-bottom: 2rem;
    }
    
    .dashboard-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .dashboard-subtitle {
        font-size: 1.1rem;
        color: #64748b;
        font-weight: 400;
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
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
    
    .insights-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .insight-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        border: 1px solid #f1f5f9;
    }
    
    .insight-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1rem;
    }
    
    .insight-content {
        color: #64748b;
        line-height: 1.6;
    }
    
    .alert-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #f59e0b;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
    }
    
    .alert-title {
        font-weight: 600;
        color: #92400e;
        margin-bottom: 0.5rem;
    }
    
    .alert-content {
        color: #b45309;
        font-size: 0.9rem;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Data Fetching Functions
# -------------------------------
@st.cache_data(ttl=300)
def fetch_dashboard_data(user_id):
    conn = get_connection()
    if not conn:
        return None, None, None, None, None, None
    
    # Basic metrics
    cursor = conn.cursor()
    
    # Total products
    cursor.execute("SELECT COUNT(*) FROM Products WHERE user_id = %s", (user_id,))
    total_products = cursor.fetchone()[0]
    
    # Total sales
    cursor.execute("SELECT SUM(quantity_sold * selling_price) FROM Sales WHERE user_id = %s", (user_id,))
    total_sales = cursor.fetchone()[0] or 0
    
    # Total expenses
    cursor.execute("SELECT SUM(amount) FROM Expenses WHERE user_id = %s", (user_id,))
    total_expenses = cursor.fetchone()[0] or 0
    
    # Low stock items
    cursor.execute("SELECT COUNT(*) FROM Products WHERE user_id = %s AND stock_quantity <= reorder_level", (user_id,))
    low_stock_count = cursor.fetchone()[0]
    
    # Sales data for charts
    sales_df = pd.read_sql("""
        SELECT DATE(sale_date) as date, SUM(quantity_sold * selling_price) as daily_sales,
               SUM(quantity_sold) as daily_quantity
        FROM Sales 
        WHERE user_id = %s AND sale_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY DATE(sale_date)
        ORDER BY date
    """, conn, params=(user_id,))
    
    # Top products
    top_products_df = pd.read_sql("""
        SELECT p.name, SUM(s.quantity_sold) as total_sold, 
               SUM(s.quantity_sold * s.selling_price) as total_revenue
        FROM Sales s
        JOIN Products p ON s.product_id = p.product_id
        WHERE s.user_id = %s
        GROUP BY p.product_id, p.name
        ORDER BY total_revenue DESC
        LIMIT 10
    """, conn, params=(user_id,))
    
    cursor.close()
    conn.close()
    
    return total_products, total_sales, total_expenses, low_stock_count, sales_df, top_products_df

# -------------------------------
# Main Dashboard Content
# -------------------------------
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="dashboard-header">
        <h1 class="dashboard-title">📊 Analytics Dashboard</h1>
        <p class="dashboard-subtitle">Real-time insights into your retail business performance</p>
    </div>
""", unsafe_allow_html=True)

# Fetch data
total_products, total_sales, total_expenses, low_stock_count, sales_df, top_products_df = fetch_dashboard_data(user_id)

if total_products is not None:
    # Key Metrics
    profit = total_sales - total_expenses
    profit_margin = (profit / total_sales * 100) if total_sales > 0 else 0
    
    # Metrics Grid
    st.markdown("""
        <div class="metrics-grid">
            <div class="metric-card">
                <span class="metric-icon">🛍️</span>
                <div class="metric-value">{}</div>
                <div class="metric-label">Total Products</div>
            </div>
            <div class="metric-card">
                <span class="metric-icon">💰</span>
                <div class="metric-value">₹{:,.0f}</div>
                <div class="metric-label">Total Sales</div>
                <div class="metric-change positive">↗ This month</div>
            </div>
            <div class="metric-card">
                <span class="metric-icon">📉</span>
                <div class="metric-value">₹{:,.0f}</div>
                <div class="metric-label">Total Expenses</div>
            </div>
            <div class="metric-card">
                <span class="metric-icon">📈</span>
                <div class="metric-value">₹{:,.0f}</div>
                <div class="metric-label">Net Profit</div>
                <div class="metric-change {}">{}{}%</div>
            </div>
        </div>
    """.format(
        total_products,
        total_sales,
        total_expenses,
        profit,
        "positive" if profit >= 0 else "negative",
        "↗ " if profit >= 0 else "↘ ",
        f"{profit_margin:.1f}"
    ), unsafe_allow_html=True)
    
    # Alerts
    if low_stock_count > 0:
        st.markdown(f"""
            <div class="alert-card">
                <div class="alert-title">⚠️ Inventory Alert</div>
                <div class="alert-content">{low_stock_count} products are running low on stock and need reordering.</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Charts Section
    if not sales_df.empty:
        st.markdown('<h2 class="section-title">📈 Sales Performance</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">Daily Sales Trend (Last 30 Days)</h3>', unsafe_allow_html=True)
            
            fig_sales = px.line(
                sales_df, 
                x='date', 
                y='daily_sales',
                title="",
                color_discrete_sequence=['#667eea']
            )
            fig_sales.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter",
                xaxis_title="Date",
                yaxis_title="Sales (₹)",
                showlegend=False,
                margin=dict(l=0, r=0, t=0, b=0)
            )
            fig_sales.update_traces(line_width=3)
            st.plotly_chart(fig_sales, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">Daily Quantity Sold</h3>', unsafe_allow_html=True)
            
            fig_qty = px.bar(
                sales_df, 
                x='date', 
                y='daily_quantity',
                title="",
                color_discrete_sequence=['#764ba2']
            )
            fig_qty.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter",
                xaxis_title="Date",
                yaxis_title="Quantity Sold",
                showlegend=False,
                margin=dict(l=0, r=0, t=0, b=0)
            )
            st.plotly_chart(fig_qty, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Top Products Section
    if not top_products_df.empty:
        st.markdown('<h2 class="section-title">🏆 Top Performing Products</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">Top 10 Products by Revenue</h3>', unsafe_allow_html=True)
            
            fig_products = px.bar(
                top_products_df.head(10), 
                x='total_revenue', 
                y='name',
                orientation='h',
                title="",
                color='total_revenue',
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
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">Product Performance Table</h3>', unsafe_allow_html=True)
            
            # Format the dataframe for display
            display_df = top_products_df.head(8).copy()
            display_df['total_revenue'] = display_df['total_revenue'].apply(lambda x: f"₹{x:,.0f}")
            display_df.columns = ['Product Name', 'Units Sold', 'Revenue']
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Business Insights
    st.markdown('<h2 class="section-title">💡 Business Insights</h2>', unsafe_allow_html=True)
    
    # Calculate insights
    avg_daily_sales = sales_df['daily_sales'].mean() if not sales_df.empty else 0
    best_day_sales = sales_df.loc[sales_df['daily_sales'].idxmax()] if not sales_df.empty else None
    
    st.markdown("""
        <div class="insights-grid">
            <div class="insight-card">
                <h4 class="insight-title">📊 Performance Summary</h4>
                <div class="insight-content">
                    Your business generated <strong>₹{:,.0f}</strong> in sales with a profit margin of <strong>{:.1f}%</strong>. 
                    You have <strong>{}</strong> products in your inventory.
                </div>
            </div>
            <div class="insight-card">
                <h4 class="insight-title">🎯 Key Recommendations</h4>
                <div class="insight-content">
                    {} Focus on promoting top-performing products and consider restocking items that are running low.
                    Monitor daily sales trends to optimize your inventory management.
                </div>
            </div>
            <div class="insight-card">
                <h4 class="insight-title">📈 Growth Opportunities</h4>
                <div class="insight-content">
                    Average daily sales: <strong>₹{:,.0f}</strong>. 
                    Consider expanding your best-selling product categories and analyzing customer preferences for future growth.
                </div>
            </div>
        </div>
    """.format(
        total_sales,
        profit_margin,
        total_products,
        f"⚠️ {low_stock_count} items need restocking. " if low_stock_count > 0 else "",
        avg_daily_sales
    ), unsafe_allow_html=True)

else:
    st.error("❌ Unable to fetch dashboard data. Please check your database connection.")

st.markdown('</div>', unsafe_allow_html=True)

# Quick Actions
st.markdown('<h2 class="section-title">⚡ Quick Actions</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📦 View Inventory", use_container_width=True):
        st.switch_page("pages/3_Inventory.py")

with col2:
    if st.button("🛒 Add Purchase", use_container_width=True):
        st.switch_page("pages/2_Purchases.py")

with col3:
    if st.button("💰 Record Sale", use_container_width=True):
        st.switch_page("pages/4_Sales.py")

with col4:
    if st.button("📋 Add Expense", use_container_width=True):
        st.switch_page("pages/5_Expenses.py")

