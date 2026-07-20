import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="Sales & Revenue Dashboard", layout="wide")

st.title("📊 Sales & Revenue Analysis Dashboard")
st.markdown("Upload your sales data to analyze KPIs, trends, and top products.")

# --- DATA LOADING ---
@st.cache_data
def get_sample_data():
    """Generates mock data if no file is uploaded."""
    data = {
        "Date": pd.date_range(start="2026-01-01", periods=100, freq="D"),
        "Product": ["Laptop", "Smartphone", "Tablet", "Headphones", "Smartwatch"] * 20,
        "Region": ["North", "South", "East", "West"] * 25,
        "Quantity": [2, 1, 5, 3, 2] * 20,
        "Revenue": [2400, 800, 1500, 300, 500] * 20
    }
    return pd.DataFrame(data)

# File Uploader
uploaded_file = st.sidebar.file_uploader("Upload your Excel or CSV file", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.sidebar.success("File uploaded successfully!")
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")
        df = get_sample_data()
else:
    st.sidebar.info("Using built-in sample data. Upload your own file to customize.")
    df = get_sample_data()

# Ensure Date column is datetime type if it exists
date_cols = [col for col in df.columns if 'date' in col.lower()]
if date_cols:
    df[date_cols[0]] = pd.to_datetime(df[date_cols[0]])
    df = df.sort_values(by=date_cols[0])

# --- SIDEBAR FILTERS (SLICERS) ---
st.sidebar.header("Filter Options")

# Product Filter
product_col = [col for col in df.columns if 'product' in col.lower()]
if product_col:
    products = st.sidebar.multiselect("Select Products", options=df[product_col[0]].unique(), default=df[product_col[0]].unique())
    df = df[df[product_col[0]].isin(products)]

# Region Filter (If applicable)
region_col = [col for col in df.columns if 'region' in col.lower()]
if region_col:
    regions = st.sidebar.multiselect("Select Region", options=df[region_col[0]].unique(), default=df[region_col[0]].unique())
    df = df[df[region_col[0]].isin(regions)]

# --- BUSINESS LOGIC / METRICS ---
# Dynamically detect revenue and quantity columns
rev_col = [col for col in df.columns if 'revenue' in col.lower() or 'sales' in col.lower() or 'amount' in col.lower()][0]
qty_col = [col for col in df.columns if 'qty' in col.lower() or 'quantity' in col.lower() or 'units' in col.lower()][0]

total_revenue = df[rev_col].sum()
total_units = df[qty_col].sum()
avg_order_value = total_revenue / len(df) if len(df) > 0 else 0

# --- KPI DISPLAY ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="💰 Total Revenue", value=f"${total_revenue:,.2f}")
with col2:
    st.metric(label="📦 Units Sold", value=f"{total_units:,}")
with col3:
    st.metric(label="📈 Avg Order Value", value=f"${avg_order_value:,.2f}")

st.markdown("---")

# --- VISUALIZATIONS ---
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("📅 Revenue Trend Over Time")
    if date_cols:
        # Aggregate by date to keep chart clean
        trend_df = df.groupby(date_cols[0])[rev_col].sum().reset_index()
        fig_trend = px.line(trend_df, x=date_cols[0], y=rev_col, labels={rev_col: "Revenue"}, template="plotly_white")
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Add a 'Date' column to your file to view timeline trends.")

with row1_col2:
    st.subheader("🏆 Top Performing Products")
    if product_col:
        prod_df = df.groupby(product_col[0])[rev_col].sum().reset_index().sort_values(by=rev_col, ascending=False)
        fig_prod = px.bar(prod_df, x=product_col[0], y=rev_col, color=product_col[0], labels={rev_col: "Revenue"}, template="plotly_white")
        st.plotly_chart(fig_prod, use_container_width=True)
    else:
        st.info("Add a 'Product' column to view product breakdowns.")

# --- DATA VIEW ---
st.subheader("📋 Filtered Raw Data Summary")
st.dataframe(df, use_container_width=True)