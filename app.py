import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="APL Logistics Dashboard",
    page_icon="📦",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM CSS (POWER BI STYLE)
# ---------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

.metric-card {
    background-color: #1C1F26;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 0px 15px rgba(0,0,0,0.4);
}

h1, h2, h3 {
    color: white;
}

[data-testid="stSidebar"] {
    background-color: #161A23;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("processed_apl_logistics.csv")
    return df

df = load_data()

# ---------------------------------------------------
# DATA PREPROCESSING
# ---------------------------------------------------

df['Profit Margin %'] = (
    df['Order Profit Per Order'] / df['Sales']
) * 100

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

st.sidebar.title("📌 Dashboard Filters")

market_filter = st.sidebar.multiselect(
    "Select Market",
    df['Market'].unique(),
    default=df['Market'].unique()
)

category_filter = st.sidebar.multiselect(
    "Select Category",
    df['Category Name'].unique(),
    default=df['Category Name'].unique()
)

segment_filter = st.sidebar.multiselect(
    "Customer Segment",
    df['Customer Segment'].unique(),
    default=df['Customer Segment'].unique()
)

shipping_filter = st.sidebar.multiselect(
    "Shipping Mode",
    df['Shipping Mode'].unique(),
    default=df['Shipping Mode'].unique()
)

# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------

filtered_df = df[
    (df['Market'].isin(market_filter)) &
    (df['Category Name'].isin(category_filter)) &
    (df['Customer Segment'].isin(segment_filter)) &
    (df['Shipping Mode'].isin(shipping_filter))
]

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Order Profit Per Order'].sum()
total_orders = filtered_df.shape[0]
profit_margin = (total_profit / total_sales) * 100

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💰 Total Revenue", f"${total_sales:,.0f}")

with col2:
    st.metric("📈 Total Profit", f"${total_profit:,.0f}")

with col3:
    st.metric("📦 Total Orders", f"{total_orders:,}")

with col4:
    st.metric("📊 Profit Margin", f"{profit_margin:.2f}%")

st.markdown("---")

# ---------------------------------------------------
# REVENUE VS PROFIT
# ---------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    revenue_profit = pd.DataFrame({
        'Metric': ['Revenue', 'Profit'],
        'Value': [total_sales, total_profit]
    })

    fig = px.bar(
        revenue_profit,
        x='Metric',
        y='Value',
        color='Metric',
        title='Revenue vs Profit'
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:

    market_analysis = filtered_df.groupby('Market').agg({
        'Sales': 'sum',
        'Order Profit Per Order': 'sum'
    }).reset_index()

    fig = px.pie(
        market_analysis,
        names='Market',
        values='Sales',
        title='Market Revenue Contribution'
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# CATEGORY ANALYSIS
# ---------------------------------------------------

st.subheader("📦 Product & Category Performance")

category_analysis = filtered_df.groupby('Category Name').agg({
    'Sales': 'sum',
    'Order Profit Per Order': 'sum'
}).reset_index()

category_analysis['Margin %'] = (
    category_analysis['Order Profit Per Order']
    / category_analysis['Sales']
) * 100

col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
        category_analysis.sort_values(
            by='Order Profit Per Order',
            ascending=False
        ),
        x='Category Name',
        y='Order Profit Per Order',
        color='Margin %',
        title='Category Profitability'
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:

    fig = px.scatter(
        category_analysis,
        x='Sales',
        y='Order Profit Per Order',
        size='Margin %',
        color='Margin %',
        hover_name='Category Name',
        title='Sales vs Profit Analysis'
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# CUSTOMER ANALYSIS
# ---------------------------------------------------

st.subheader("👥 Customer Value Dashboard")

customer_analysis = filtered_df.groupby('Customer Id').agg({
    'Sales': 'sum',
    'Order Profit Per Order': 'sum'
}).reset_index()

top_customers = customer_analysis.sort_values(
    by='Order Profit Per Order',
    ascending=False
).head(10)

bottom_customers = customer_analysis.sort_values(
    by='Order Profit Per Order',
    ascending=True
).head(10)

col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
        top_customers,
        x='Customer Id',
        y='Order Profit Per Order',
        title='Top 10 Customers by Profit',
        color='Order Profit Per Order'
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:

    fig = px.bar(
        bottom_customers,
        x='Customer Id',
        y='Order Profit Per Order',
        title='Bottom 10 Customers by Profit',
        color='Order Profit Per Order'
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# CUSTOMER SEGMENT
# ---------------------------------------------------

segment_analysis = filtered_df.groupby('Customer Segment').agg({
    'Sales': 'sum',
    'Order Profit Per Order': 'sum'
}).reset_index()

fig = px.sunburst(
    segment_analysis,
    path=['Customer Segment'],
    values='Sales',
    color='Order Profit Per Order',
    title='Customer Segment Contribution'
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# DISCOUNT IMPACT ANALYZER
# ---------------------------------------------------

st.subheader("🏷️ Discount Impact Analyzer")

col1, col2 = st.columns(2)

with col1:

    fig = px.scatter(
        filtered_df,
        x='Order Item Discount Rate',
        y='Profit Margin %',
        color='Profit Margin %',
        title='Discount vs Profit Margin'
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:

    fig = px.histogram(
        filtered_df,
        x='Order Item Discount Rate',
        nbins=30,
        title='Discount Distribution'
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# WHAT-IF ANALYSIS
# ---------------------------------------------------

st.subheader("🧠 What-If Discount Scenario")

discount_slider = st.slider(
    "Select Discount Threshold %",
    0,
    50,
    20
)

scenario_df = filtered_df[
    filtered_df['Order Item Discount Rate'] * 100 < discount_slider
]

scenario_profit = scenario_df['Order Profit Per Order'].sum()

st.success(
    f"Estimated Profit if discounts stay below "
    f"{discount_slider}% : ${scenario_profit:,.0f}"
)

# ---------------------------------------------------
# SHIPPING ANALYSIS
# ---------------------------------------------------

st.subheader("🚚 Shipping Performance")

shipping_analysis = filtered_df.groupby('Shipping Mode').agg({
    'Days for shipping (real)': 'mean',
    'Order Profit Per Order': 'mean'
}).reset_index()

fig = px.area(
    shipping_analysis,
    x='Shipping Mode',
    y='Order Profit Per Order',
    title='Shipping Mode Profitability'
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# REGION HEATMAP
# ---------------------------------------------------

st.subheader("🌍 Regional Profit Heatmap")

region_analysis = filtered_df.groupby(
    ['Market', 'Category Name']
).agg({
    'Order Profit Per Order': 'sum'
}).reset_index()

pivot_table = region_analysis.pivot(
    index='Market',
    columns='Category Name',
    values='Order Profit Per Order'
)

fig = px.imshow(
    pivot_table,
    aspect="auto",
    title='Market vs Category Profitability'
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# SALES TREND
# ---------------------------------------------------

st.subheader("📈 Revenue Trend")

if 'order date (DateOrders)' in filtered_df.columns:

    filtered_df['order date (DateOrders)'] = pd.to_datetime(
        filtered_df['order date (DateOrders)']
    )

    trend = filtered_df.groupby(
        filtered_df['order date (DateOrders)'].dt.to_period('M')
    )['Sales'].sum().reset_index()

    trend['order date (DateOrders)'] = trend[
        'order date (DateOrders)'
    ].astype(str)

    fig = px.line(
        trend,
        x='order date (DateOrders)',
        y='Sales',
        title='Monthly Revenue Trend'
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# RAW DATA
# ---------------------------------------------------

st.subheader("📄 Raw Data")

st.dataframe(filtered_df)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown("---")

st.markdown("""
<center>
<h4>APL Logistics Profitability Intelligence Dashboard</h4>
<p>Built using Streamlit | Power BI Style Analytics</p>
</center>
""", unsafe_allow_html=True)