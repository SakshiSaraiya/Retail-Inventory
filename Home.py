import streamlit as st  
from auth import register_user, login_user
import time

# --- Page Config ---
st.set_page_config(
    page_title="Home | RetailPro Management",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded" if st.session_state.get("is_logged_in", False) else "collapsed"
)

# --- Session State ---
if "is_logged_in" not in st.session_state:
    st.session_state["is_logged_in"] = False
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

# --- Professional Styling ---
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
        padding: 3rem;
        margin: 2rem auto;
        max-width: 1200px;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .hero-section {
        text-align: center;
        padding: 2rem 0 3rem 0;
        border-bottom: 1px solid #e1e8ed;
        margin-bottom: 3rem;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: #64748b;
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto 2rem auto;
        line-height: 1.6;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.4);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 500;
    }
    
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
    }
    
    .feature-card {
        background: white;
        padding: 2.5rem 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        border: 1px solid #f1f5f9;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.12);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1.5rem;
        display: block;
    }
    
    .feature-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1rem;
    }
    
    .feature-description {
        color: #64748b;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .auth-container {
        background: white;
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        margin: 2rem 0;
    }
    
    .auth-tabs {
        display: flex;
        background: #f8fafc;
        border-radius: 12px;
        padding: 0.5rem;
        margin-bottom: 2rem;
    }
    
    .auth-tab {
        flex: 1;
        padding: 1rem;
        text-align: center;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 600;
        color: #64748b;
    }
    
    .auth-tab.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    .form-label {
        display: block;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
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
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3) !important;
    }
    
    .nav-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
    }
    
    .nav-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        border: 1px solid #f1f5f9;
        transition: all 0.3s ease;
        text-decoration: none;
    }
    
    .nav-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.12);
        text-decoration: none;
    }
    
    .nav-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .nav-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .nav-description {
        color: #64748b;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .section-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        text-align: center;
        margin: 3rem 0 2rem 0;
        position: relative;
    }
    
    .section-title::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 4px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 2px;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    .sidebar-logo {
        text-align: center;
        padding: 2rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1rem;
    }
    
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stSelectbox > div > div {
        border-radius: 12px !important;
    }
    
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Main Content ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Hero Section
st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">RetailPro Management</h1>
        <p class="hero-subtitle">
            Transform your retail business with our comprehensive management platform. 
            Get real-time insights, optimize inventory, and boost profitability.
        </p>
    </div>
""", unsafe_allow_html=True)

# Stats Section (Mock data for demo)
st.markdown("""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">98%</div>
            <div class="stat-label">Inventory Accuracy</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">↑24%</div>
            <div class="stat-label">Revenue Growth</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">15min</div>
            <div class="stat-label">Setup Time</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Real-time Monitoring</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Authentication Section
if not st.session_state["is_logged_in"]:
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    # Create tabs for login/register
    login_tab, register_tab = st.tabs(["🔐 Sign In", "📝 Create Account"])
    
    with login_tab:
        st.markdown("### Welcome Back")
        st.markdown("Sign in to access your retail management dashboard")
        
        with st.form("login_form"):
            username_or_email = st.text_input("Email or Username", placeholder="Enter your email or username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                login_submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if login_submit:
                if username_or_email and password:
                    with st.spinner("Signing you in..."):
                        time.sleep(1)  # Simulate loading
                        success, user_id = login_user(username_or_email, password)
                        if success:
                            st.session_state["is_logged_in"] = True
                            st.session_state["user_id"] = user_id
                            st.success("✅ Welcome back! Redirecting to dashboard...")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials. Please check your email/username and password.")
                else:
                    st.warning("⚠️ Please fill in all fields.")

    with register_tab:
        st.markdown("### Join RetailPro")
        st.markdown("Create your account and start managing your retail business today")
        
        with st.form("register_form"):
            new_username = st.text_input("Username", placeholder="Choose a unique username")
            new_email = st.text_input("Email", placeholder="Enter your email address")
            new_password = st.text_input("Password", type="password", placeholder="Create a strong password")
            
            register_submit = st.form_submit_button("Create Account", use_container_width=True)
            
            if register_submit:
                if new_username and new_email and new_password:
                    if len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters long.")
                    else:
                        with st.spinner("Creating your account..."):
                            time.sleep(1)  # Simulate loading
                            success, message = register_user(new_username, new_email, new_password)
                            if success:
                                st.success("✅ Account created successfully! Please sign in.")
                                time.sleep(1)
                            else:
                                st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Please fill in all fields.")
    
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Dashboard Navigation for logged-in users
    st.markdown('<h2 class="section-title">Dashboard Navigation</h2>', unsafe_allow_html=True)
    
    # Navigation Grid
    st.markdown("""
        <div class="nav-grid">
            <a href="/1_Dashboard" target="_self" class="nav-card">
                <span class="nav-icon">📊</span>
                <div class="nav-title">Analytics Dashboard</div>
                <div class="nav-description">View comprehensive business analytics and key performance indicators</div>
            </a>
            
            <a href="/3_Inventory" target="_self" class="nav-card">
                <span class="nav-icon">📦</span>
                <div class="nav-title">Inventory Management</div>
                <div class="nav-description">Track stock levels, manage products, and set reorder alerts</div>
            </a>
            
            <a href="/2_Purchases" target="_self" class="nav-card">
                <span class="nav-icon">🛒</span>
                <div class="nav-title">Purchase Orders</div>
                <div class="nav-description">Manage supplier relationships and purchase transactions</div>
            </a>
            
            <a href="/4_Sales" target="_self" class="nav-card">
                <span class="nav-icon">💰</span>
                <div class="nav-title">Sales Analytics</div>
                <div class="nav-description">Monitor sales performance and revenue trends</div>
            </a>
            
            <a href="/5_Expenses" target="_self" class="nav-card">
                <span class="nav-icon">📋</span>
                <div class="nav-title">Expense Tracking</div>
                <div class="nav-description">Manage and categorize business expenses</div>
            </a>
            
            <a href="/0_Finance _Dashboard" target="_self" class="nav-card">
                <span class="nav-icon">💹</span>
                <div class="nav-title">Financial Overview</div>
                <div class="nav-description">Complete financial dashboard with profit analysis</div>
            </a>
        </div>
    """, unsafe_allow_html=True)
    
    # Logout Section
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state["is_logged_in"] = False
            st.session_state["user_id"] = None
            st.success("You have been signed out successfully!")
            time.sleep(1)
            st.rerun()

# Features Section (visible to all users)
st.markdown('<h2 class="section-title">Platform Features</h2>', unsafe_allow_html=True)

st.markdown("""
    <div class="features-grid">
        <div class="feature-card">
            <span class="feature-icon">🎯</span>
            <h4 class="feature-title">Smart Inventory Control</h4>
            <p class="feature-description">
                AI-powered inventory management with automated reorder points, 
                stock optimization, and demand forecasting.
            </p>
        </div>
        
        <div class="feature-card">
            <span class="feature-icon">📈</span>
            <h4 class="feature-title">Advanced Analytics</h4>
            <p class="feature-description">
                Real-time dashboards with interactive charts, sales trends, 
                profit analysis, and business intelligence insights.
            </p>
        </div>
        
        <div class="feature-card">
            <span class="feature-icon">🔒</span>
            <h4 class="feature-title">Secure & Reliable</h4>
            <p class="feature-description">
                Enterprise-grade security with encrypted data storage, 
                user authentication, and regular automated backups.
            </p>
        </div>
        
        <div class="feature-card">
            <span class="feature-icon">📱</span>
            <h4 class="feature-title">Mobile Responsive</h4>
            <p class="feature-description">
                Access your dashboard anywhere with our responsive design 
                that works perfectly on desktop, tablet, and mobile devices.
            </p>
        </div>
        
        <div class="feature-card">
            <span class="feature-icon">⚡</span>
            <h4 class="feature-title">Real-time Updates</h4>
            <p class="feature-description">
                Get instant notifications for low stock, new orders, 
                and important business events as they happen.
            </p>
        </div>
        
        <div class="feature-card">
            <span class="feature-icon">🎨</span>
            <h4 class="feature-title">Customizable Interface</h4>
            <p class="feature-description">
                Personalize your dashboard layout, create custom reports, 
                and configure the interface to match your workflow.
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #64748b; padding: 2rem 0;">
        <p><strong>RetailPro Management</strong> • Streamline your retail operations with confidence</p>
        <p style="font-size: 0.9rem;">© 2024 RetailPro. Built with ❤️ for modern retailers.</p>
    </div>
""", unsafe_allow_html=True)



