import streamlit as st
import pandas as pd
from db import get_connection
from datetime import date
import plotly.express as px
from auth import check_login


# --- Page Config ---
st.set_page_config(
    page_title="Expense Management",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -------------------------
# Authentication Check
# -------------------------
check_login()
user_id = st.session_state.user_id

# --- Custom Styling ---
st.markdown("""
    <style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
    }
    [data-testid="stSidebar"] * {
        color: #F1F5F9 !important;
    }

    /* Main background */
    .block-container {
        background-color: #F8FAFC;
        padding: 2rem;
    }

    /* Headings and text */
    h1, h2, h3, label, p, .stText, .stMarkdown, div {
        color: #0F172A !important;
    }

    /* Input widgets */
    .stTextInput, .stNumberInput, .stDateInput, .stSelectbox, .stTextArea, .stFileUploader, .stDataFrame {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }

    input, textarea, select {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        padding: 0.5rem;
    }

    /* Metric Cards */
    .metric-card {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
        color: #1E293B;
    }

    /* Add Button */
    .add-expense-btn {
        background-color: #eaf1fb;
        color: #0F172A;
        font-weight: 600;
        border: 2px solid #0F172A;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-size: 1.5rem;
        cursor: pointer;
        transition: background-color 0.3s ease;
        margin-bottom: 1rem;
    }
    .add-expense-btn:hover {
        background-color: #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<h1>Expense Management</h1>", unsafe_allow_html=True)

# --- DB Connection ---
conn = get_connection()
cursor = conn.cursor()

# --- Add Expenses Section (Expander) ---
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
with st.expander("➕ Add Expense", expanded=False):
    with st.form("expense_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            expense_date = st.date_input("Expense Date", value=date.today())
        with col2:
            category = st.selectbox("Category", ["Rent", "Salary", "Utilities", "Marketing", "Transport", "Misc"])
        with col3:
            expense_type = st.selectbox("Type", ["Fixed", "Variable"])
        amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
        description = st.text_input("Optional Description")
        submit = st.form_submit_button("Add Expense")
        if submit:
            try:
                cursor.execute("""
                    INSERT INTO Expenses (user_id, expense_date, category,TYPE, amount, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (user_id, expense_date, category, expense_type, amount, description))
                conn.commit()
                st.success("Expense added successfully.")
            except Exception as e:
                st.error(f"Error: {e}")
st.markdown("</div>", unsafe_allow_html=True)

# --- Upload from CSV (Expander) ---
st.markdown("<div class='section-card'>", unsafe_allow_html=True)
with st.expander("📤 Upload Expenses from CSV", expanded=False):
    sample_csv = pd.DataFrame({
        "date": ["2025-07-01"],
        "category": ["Marketing"],
        "expense_type": ["Variable"],
        "amount": [5000],
        "description": ["Social Media Campaign"]
    })
    st.markdown("Sample Format:")
    st.dataframe(sample_csv, use_container_width=True)
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file:
    try:
        df_upload = pd.read_csv(uploaded_file)
        df_upload["date"] = pd.to_datetime(df_upload["date"]).dt.date
        for _, row in df_upload.iterrows():
            cursor.execute("""
                INSERT INTO Expenses (user_id, expense_date, category, TYPE, amount, description)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (user_id, row["date"], row["category"], row["expense_type"], row["amount"], row["description"]))
        conn.commit()
        st.success("Expenses uploaded successfully.")
    except Exception as e:
        st.error(f"Error uploading file: {e}")
st.markdown("</div>", unsafe_allow_html=True)

# --- Expense Data & Insights ---
try:
    df = pd.read_sql(f"""
        SELECT expense_date, category, TYPE, amount, description
        FROM Expenses
        WHERE user_id = {user_id}
        ORDER BY expense_date DESC
    """, conn)
    df["expense_date"] = pd.to_datetime(df["expense_date"]).dt.date

    # --- Raw Data Table with Edit/Delete (toggle) ---
    show_raw = st.checkbox("Show Raw Data Table (Edit/Delete)")
    if show_raw:
        st.markdown("<h4 style='margin-top:2.5rem;'>Expense Records (Raw Data)</h4>", unsafe_allow_html=True)
        raw_df = df.copy()
        st.dataframe(raw_df, use_container_width=True)
        st.markdown("<b>Edit or Delete an Expense Record:</b>", unsafe_allow_html=True)
        selected_idx = st.selectbox("Select Row to Edit/Delete", raw_df.index)
        action = st.radio("Action", ["Edit", "Delete"], key="expense_action")
        if action == "Edit":
            row = raw_df.loc[selected_idx]
            with st.form("edit_expense_form"):
                st.write("Edit the fields and click Save:")
                expense_date = st.date_input("Expense Date", value=row['expense_date'])
                category = st.text_input("Category", value=row['category'])
                expense_type = st.selectbox("Type", ["Fixed", "Variable"], index=["Fixed", "Variable"].index(row['TYPE']) if row['TYPE'] in ["Fixed", "Variable"] else 0)
                amount = st.number_input("Amount (₹)", min_value=0.0, value=float(row['amount']))
                description = st.text_input("Description", value=row['description'])
                submit = st.form_submit_button("Save Changes")
                if submit:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE Expenses SET expense_date=%s, category=%s, TYPE=%s, amount=%s, description=%s
                        WHERE user_id=%s AND expense_date=%s AND category=%s AND TYPE=%s AND amount=%s AND description=%s
                    """, (expense_date, category, expense_type, amount, description, user_id, row['expense_date'], row['category'], row['TYPE'], row['amount'], row['description']))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success("Expense record updated!")
                    st.rerun()
        elif action == "Delete":
            if st.button("Delete This Record", key="delete_expense_btn", help="Delete this record", use_container_width=True):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM Expenses WHERE user_id=%s AND expense_date=%s AND category=%s AND TYPE=%s AND amount=%s AND description=%s
                """, (user_id, row['expense_date'], row['category'], row['TYPE'], row['amount'], row['description']))
                conn.commit()
                cursor.close()
                conn.close()
                st.success("Expense record deleted!")
                st.rerun()

    # --- KPI Cards (Sales-Style, 4 Even Cards, Centered Title, st.columns layout, ₹ and value truly side by side) ---
    st.markdown("""
    <style>
    .kpi-section-title {
        font-size: 1.45rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 2.2rem;
        letter-spacing: 0.5px;
        text-align: center;
    }
    .kpi-card-light {
        background: #fff;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.10);
        padding: 1.5rem 1.2rem 1.2rem 1.2rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-width: 180px;
        max-width: 200px;
        min-height: 90px;
        margin-bottom: 0;
        position: relative;
        top: -60px;
    }
    .kpi-card-light .kpi-label {
        font-size: 1.1rem;
        color: #334155;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    .kpi-card-light .kpi-value {
        font-size: 2rem;
        font-weight: 600;
        color: #000 !important;
        display: inline;
        margin-top: 0;
        white-space: nowrap;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("<div style='max-width:1100px;margin:0 auto 2.5rem auto;'>", unsafe_allow_html=True)
    st.markdown("<div class='kpi-section-title'style='text-align:left;position:relative;margin-bottom:4.5rem;'>Key Metrics</div>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    total_exp = df['amount'].sum()
    fixed_exp = df[df['TYPE']=='Fixed']['amount'].sum()
    var_exp = df[df['TYPE']=='Variable']['amount'].sum()
    max_exp = df['amount'].max() if not df.empty else 0
    with k1:
        st.markdown(f"""
            <div class='kpi-card-light'>
                <div class='kpi-label'>Total Expenses</div>
                <span class='kpi-value'>₹ {total_exp:,.2f}</span>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
            <div class='kpi-card-light'>
                <div class='kpi-label'>Fixed Costs</div>
                <span class='kpi-value'>₹ {fixed_exp:,.2f}</span>
            </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
            <div class='kpi-card-light'>
                <div class='kpi-label'>Variable Costs</div>
                <span class='kpi-value'>₹ {var_exp:,.2f}</span>
            </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
            <div class='kpi-card-light'>
                <div class='kpi-label'>Max Expense</div>
                <span class='kpi-value'>₹ {max_exp:,.2f}</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Expense Breakdown Donut Chart ---
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:500'>Expense Breakdown by Category</div>", unsafe_allow_html=True)
    cat_df = df.groupby('category')["amount"].sum().reset_index().sort_values(by="amount", ascending=False)
    fig_donut = px.pie(cat_df, names='category', values='amount', hole=0.45, color_discrete_sequence=[
        "#A3C4F3", "#FFB7B2", "#B5EAD7", "#FFDAC1", "#E2F0CB",
        "#C7CEEA", "#FFFACD", "#FFD6E0", "#D4A5A5", "#B5B2C2"],)
    fig_donut.update_traces(textinfo='percent+label')
    fig_donut.update_layout(showlegend=True, template='plotly_white')
    st.plotly_chart(fig_donut, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Top Categories Table ---
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:500'>Top Expense Categories</div>", unsafe_allow_html=True)
    styled_cat = cat_df.style.background_gradient(cmap='Blues', subset=['amount'])
    st.dataframe(styled_cat, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Recent Expenses Card ---
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:500'>Recent Expenses</div>", unsafe_allow_html=True)
    st.dataframe(df.head(5)[["expense_date", "category", "TYPE", "amount", "description"]], use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Expense Anomalies ---
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:500'>Expense Anomalies</div>", unsafe_allow_html=True)
    anomaly_df = pd.DataFrame()
    for cat in cat_df['category']:
        cat_amounts = df[df['category'] == cat]['amount']
        mean = cat_amounts.mean()
        std = cat_amounts.std()
        anomalies = df[(df['category'] == cat) & (df['amount'] > mean + 2*std)]
        anomaly_df = pd.concat([anomaly_df, anomalies])
    if not anomaly_df.empty:
        st.dataframe(anomaly_df[["expense_date", "category", "amount", "description"]], use_container_width=True)
    else:
        st.info("No anomalies detected (expenses > 2 std above category mean).")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Download Expenses Report ---
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:500'>Download Expenses Report</div>", unsafe_allow_html=True)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "expenses_report.csv", "text/csv", key="download_expenses")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Monthly Expense Trend (Bar Chart) ---
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'<h1 style='font-size:2.0rem;color:#0F172A;font-weight:500'>Monthly Expense Trend</div>", unsafe_allow_html=True)
    df["month"] = pd.to_datetime(df["expense_date"]).dt.to_period("M").astype(str)
    monthly_chart = df.groupby(["month", "TYPE"])["amount"].sum().reset_index()
    fig = px.bar(
        monthly_chart,
        x="month",
        y="amount",
        color="TYPE",
        barmode="group",
        text_auto='.2s'
    )
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color='black',
        xaxis=dict(showgrid=False, title="Month", tickfont=dict(color='black')),
        yaxis=dict(showgrid=False, title="Amount (₹)", tickfont=dict(color='black')),
        legend_title_text="Expense Type",
        title_font=dict(color='black', size=18)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.warning(f"No data or error loading data: {e}")
