import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Patagonia BI: Return & Eco-Analytics", layout="wide")

# --- THEME STABILIZER CSS ---
st.markdown("""
    <style>
    /* Force the main background to a stable light grey so dark cards always look good */
    .stApp {
        background-color: #f8f9fa !important;
    }

    /* Target the Metric Cards specifically */
    [data-testid="stMetric"] {
        background-color: #1a1c23 !important; /* Deep Navy/Black */
        padding: 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        border: 1px solid #e0e0e0 !important;
    }

    /* Force Label Text to be White/Light */
    [data-testid="stMetricLabel"] p {
        color: #adb5bd !important; /* Subtle grey-white */
        font-size: 14px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }

    /* Force Metric Value to be Bright Green */
    [data-testid="stMetricValue"] div {
        color: #2ecc71 !important; 
        font-weight: 700 !important;
    }

    /* Style the sidebar to match the professional look */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Fix for wonky tab text */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 16px !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    df = pd.read_csv('Patagonia_Order (1).csv')
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    df['Is_Returned'] = df['Return_Status'].apply(lambda x: 1 if x == 'Returned' else 0)
    df['Country'] = df['Customer_Location'].str.split(',').str[0]
    df['Age_Group'] = pd.cut(df['Age'], bins=[18, 25, 35, 45, 60, 100], 
                             labels=['Gen Z', 'Young Adult', 'Adult', 'Middle Age', 'Senior'])
    return df

df_raw = load_data()

# --- FILTERS ---
with st.sidebar:
    st.title("🎛️ BI Controls")
    mats = st.multiselect("Filter Materials", options=df_raw['Material'].unique(), default=df_raw['Material'].unique())
    gender = st.radio("Gender Perspective", options=["All", "Male", "Female"])

# Filtering logic
df = df_raw[df_raw['Material'].isin(mats)]
if gender != "All":
    df = df[df['Gender'] == gender]

# --- DASHBOARD HEADER ---
st.title("🌲 Patagonia: Sustainability & Return Intelligence")
st.caption("Marketing Analytics CIA 3 | Profitability & Eco-Impact Tracking")

# --- KPI SECTION ---
st.write("### Business Health Snapshot")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Net Revenue", f"${df['Total_Revenue ($)'].sum():,.0f}")
k2.metric("Return Rate", f"{(df['Is_Returned'].mean()*100):.2f}%", delta="-0.5% vs Target", delta_color="inverse")
k3.metric("Water Saved (Est)", f"{df['Water_Usage (liters)'].sum():,.0f} L")
k4.metric("Carbon Offset", f"${df['Carbon_Offset_Investment ($)'].sum():,.0f}")

st.divider()

# --- INTERACTIVE TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Financial Trends", "🌍 Eco-Strategy", "🔮 Risk Simulator"])

# GLOBAL CHART SETTINGS
# Using 'plotly_white' ensures the charts look good on our forced light background
chart_theme = "plotly_white"

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Revenue Trend")
        rev_trend = df.groupby(df['Order_Date'].dt.to_period('M'))['Total_Revenue ($)'].sum().reset_index()
        rev_trend['Order_Date'] = rev_trend['Order_Date'].dt.to_timestamp()
        fig1 = px.line(rev_trend, x='Order_Date', y='Total_Revenue ($)', template=chart_theme, color_discrete_sequence=['#2E7D32'])
        st.plotly_chart(fig1, use_container_width=True)
    with col_b:
        st.subheader("Returns by Category")
        cat_ret = df.groupby('Category_Name')['Is_Returned'].mean().reset_index()
        fig2 = px.bar(cat_ret, x='Category_Name', y='Is_Returned', template=chart_theme, color='Is_Returned', color_continuous_scale='Reds')
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Material Sustainability Matrix")
    mat_risk = df.groupby('Material').agg({'Percentage_Recycled_Material (%)':'mean', 'Is_Returned':'mean'}).reset_index()
    fig3 = px.scatter(mat_risk, x='Percentage_Recycled_Material (%)', y='Is_Returned', 
                      size='Is_Returned', color='Material', template=chart_theme)
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.subheader("Return Prediction Simulator")
    st.info("Adjust values to see how product specs affect return probability.")
    p_price = st.slider("Product Price ($)", 40, 300, 150)
    p_rec = st.slider("Recycled Content (%)", 0, 100, 50)
    
    # Mock-up math logic from your notebook
    risk = 0.11 + (p_price/2000) - (p_rec/1000)
    st.metric("Predicted Return Risk", f"{risk*100:.1f}%")
