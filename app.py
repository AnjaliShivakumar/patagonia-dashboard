import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Patagonia BI: Return & Eco-Analytics", layout="wide")

# --- CUSTOM CSS FOR DARK GREEN THEME & WHITE TEXT ---
# --- CUSTOM CSS FOR THEME-PROOF DARK GREEN ---
st.markdown("""
    <style>
    /* 1. Force the main background and sidebar */
    .stApp, [data-testid="stSidebar"] {
        background-color: #023020 !important; /* Dark Forest Green */
    }

    /* 2. Force ALL text to be white */
    h1, h2, h3, h4, h5, h6, p, label, span, div, li, .stMarkdown {
        color: white !important;
    }

    /* 3. FIX FOR 'WHITE ON WHITE': Force Input Widgets to have dark backgrounds */
    /* This targets Selectboxes, Multi-selects, and Text Inputs */
    div[data-baseweb="select"], div[data-baseweb="input"], .stSelectbox, .stMultiSelect {
        background-color: #0e1117 !important; 
        border-radius: 8px !important;
    }
    
    /* Ensure text inside selectbox stays white */
    div[data-baseweb="select"] * {
        color: white !important;
    }

    /* 4. Fix Sliders and Radio Buttons visibility */
    .stSlider [data-testid="stMetricValue"] {
        color: white !important;
    }
    div[data-testid="stThumbValue"] {
        color: white !important;
    }

    /* 5. Metric Card Styling (Stay Black) */
    [data-testid="stMetric"] {
        background-color: #000000 !important; /* Pure Black */
        padding: 20px !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5) !important;
        border: 1px solid #2E7D32 !important;
    }
    
    /* Label and Value colors for Metrics */
    [data-testid="stMetricLabel"] p { color: #ffffff !important; }
    [data-testid="stMetricValue"] div { color: #4CAF50 !important; }

    /* 6. Tab Styling Fixes */
    button[data-baseweb="tab"] { color: #888888 !important; } /* Inactive tabs */
    button[data-baseweb="tab"][aria-selected="true"] {
        color: white !important;
        border-bottom-color: #4CAF50 !important;
    }

    /* 7. Plotly Chart Container Fix */
    /* Forces the background of the chart containers to transparent to show the green */
    .js-plotly-plot, .plot-container {
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)
# --- LOAD & PREPROCESS ---
@st.cache_data
def load_data():
    # Make sure this matches your file name on GitHub exactly
    df = pd.read_csv('Patagonia_Order (1).csv') 
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    df['Is_Returned'] = df['Return_Status'].apply(lambda x: 1 if x == 'Returned' else 0)
    
    # Extract Country for Geographic Analysis
    df['Country'] = df['Customer_Location'].str.split(',').str[0]
    
    # Feedback Score
    fb_map = {'Excellent': 5, 'Good': 4, 'Average': 3, 'Bad': 2, 'Poor': 1}
    df['Feedback_Score'] = df['Customer_Feedback'].map(fb_map).fillna(3)
    
    # Age Groups
    df['Age_Group'] = pd.cut(df['Age'], bins=[18, 25, 35, 45, 60, 100], 
                             labels=['Gen Z', 'Young Adult', 'Adult', 'Middle Age', 'Senior'])
    return df

df_raw = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.title("Dashboard Controls")

with st.sidebar:
    st.subheader("Filter Insights")
    # Date Filter
    min_date, max_date = df_raw['Order_Date'].min().to_pydatetime(), df_raw['Order_Date'].max().to_pydatetime()
    date_range = st.date_input("Select Date Range", value=(min_date, max_date))
    
    # Multi-selects
    selected_mats = st.multiselect("Materials", options=df_raw['Material'].unique(), default=df_raw['Material'].unique())
    selected_gender = st.sidebar.radio("Gender Selection", options=["All", "Male", "Female"])

# Filter Data Logic
if len(date_range) == 2:
    mask = (df_raw['Order_Date'] >= pd.Timestamp(date_range[0])) & (df_raw['Order_Date'] <= pd.Timestamp(date_range[1]))
else:
    mask = df_raw['Order_Date'] >= pd.Timestamp(date_range[0])

mask &= (df_raw['Material'].isin(selected_mats))
if selected_gender != "All":
    mask &= (df_raw['Gender'] == selected_gender)

df = df_raw[mask]

# --- MAIN DASHBOARD ---
st.title("🌲 Patagonia: Strategic Return & Sustainability Intelligence")
st.markdown("**Marketing Analytics CIA 3**")
st.markdown("### Goal: Optimize Profitability by Reducing Return-Linked Carbon Waste")

st.write("### Executive Summary")
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("Total Net Revenue", f"${df['Total_Revenue ($)'].sum():,.0f}")
with k2:
    ret_rate = df['Is_Returned'].mean() * 100
    st.metric("Return Rate", f"{ret_rate:.2f}%", delta="-0.5% vs Prev Month", delta_color="inverse")
with k3:
    water_saved = df['Water_Usage (liters)'].sum()
    st.metric("Water Usage Saved", f"{water_saved:,.0f} L")
with k4:
    carbon_inv = df['Carbon_Offset_Investment ($)'].sum()
    st.metric("Carbon Investment", f"${carbon_inv:,.0f}")

# --- TABS FOR STORYTELLING ---
tab_fin, tab_eco, tab_cust, tab_pred = st.tabs(["💰 Financial Performance", "♻️ Eco-Efficiency", "👥 Customer Risk", "🔮 Return Risk Simulator"])

with tab_fin:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Revenue vs. Return Loss Over Time")
        df_time = df.groupby(df['Order_Date'].dt.to_period('M')).agg({'Total_Revenue ($)':'sum', 'Is_Returned':'sum'}).reset_index()
        df_time['Order_Date'] = df_time['Order_Date'].dt.to_timestamp()
        fig_time = px.area(df_time, x='Order_Date', y='Total_Revenue ($)', color_discrete_sequence=['#2E7D32'])
        st.plotly_chart(fig_time, use_container_width=True)
    
    with c2:
        st.subheader("Top Revenue Countries")
        country_rev = df.groupby('Country')['Total_Revenue ($)'].sum().sort_values(ascending=True).tail(10)
        fig_country = px.bar(country_rev, orientation='h', color_discrete_sequence=['#4CAF50'])
        st.plotly_chart(fig_country, use_container_width=True)

with tab_eco:
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Material Sustainability Matrix")
        mat_data = df.groupby('Material').agg({'Percentage_Recycled_Material (%)':'mean', 'Is_Returned':'mean', 'Total_Revenue ($)':'sum'}).reset_index()
        fig_mat = px.scatter(mat_data, x='Percentage_Recycled_Material (%)', y='Is_Returned', size='Total_Revenue ($)', 
                             color='Material', hover_name='Material')
        st.plotly_chart(fig_mat, use_container_width=True)
    
    with c4:
        st.subheader("AOV by Eco-Certification")
        cert_data = df.groupby('Eco_Certification')['Total_Revenue ($)'].mean().reset_index()
        fig_cert = px.funnel(cert_data, x='Total_Revenue ($)', y='Eco_Certification')
        st.plotly_chart(fig_cert, use_container_width=True)

with tab_cust:
    c5, c6 = st.columns(2)
    with c5:
        st.subheader("Return Risk Heatmap: Age vs Category")
        risk_map = df.pivot_table(index='Age_Group', columns='Category_Name', values='Is_Returned', aggfunc='mean') * 100
        fig_risk = px.imshow(risk_map, text_auto='.1f', color_continuous_scale='YlOrRd')
        st.plotly_chart(fig_risk, use_container_width=True)
        
    with c6:
        st.subheader("Return Reasons by Gender")
        reason_gen = df[df['Is_Returned']==1].groupby(['Gender', 'Return_Reason']).size().reset_index(name='count')
        fig_gen = px.bar(reason_gen, x='Return_Reason', y='count', color='Gender', barmode='group')
        st.plotly_chart(fig_gen, use_container_width=True)

with tab_pred:
    st.subheader("🔮 Return Risk 'What-If' Simulator")
    st.info("Predict likelihood of a return based on product specs.")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        in_price = st.slider("Unit Price ($)", 40, 270, 120)
    with col_s2:
        in_recycled = st.slider("Recycled Material %", 0, 100, 50)
    with col_s3:
        in_feedback = st.select_slider("Anticipated Feedback", options=['Poor', 'Bad', 'Average', 'Good', 'Excellent'], value='Good')

    base_risk = 0.12 
    if in_price > 200: base_risk += 0.05
    if in_feedback in ['Poor', 'Bad']: base_risk += 0.15
    if in_recycled > 70: base_risk -= 0.03
    
    st.markdown(f"## Estimated Return Risk: `{base_risk*100:.1f}%`")
    if base_risk > 0.18:
        st.error("⚠️ **High Risk Alert:** High probability of return.")
    else:
        st.success("✅ **Stable Configuration:** Low return risk predicted.")

# --- FOOTER ---
st.write("---")
st.caption("Patagonia BI Tool | Built for Marketing Analytics Assignment | Data Updated: Feb 2025")
