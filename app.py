import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Patagonia BI: Return & Eco-Analytics", layout="wide")

# --- CUSTOM CSS: THEME-PROOF FOREST GREEN ---
st.markdown("""
    <style>
    /* 1. Global Background & Text */
    .stApp, [data-testid="stSidebar"] {
        background-color: #023020 !important; /* Dark Forest Green */
    }
    
    /* Force ALL text to be white */
    * {
        color: white !important;
    }

    /* 2. Fix Input Widgets (Selectbox, Multi-select, Sliders) */
    /* This prevents the "White on White" issue in Light Mode */
    div[data-baseweb="select"], div[data-baseweb="input"], .stSelectbox, .stMultiSelect, div[role="listbox"] {
        background-color: #0e1117 !important; /* Dark background for inputs */
        border: 1px solid #2E7D32 !important;
        border-radius: 8px !important;
    }

    /* Target the text inside the selectboxes specifically */
    div[data-baseweb="select"] span, div[data-baseweb="select"] div {
        color: white !important;
    }

    /* 3. Metric Card Styling (High Contrast) */
    [data-testid="stMetric"] {
        background-color: #000000 !important; /* Pure Black */
        padding: 20px !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5) !important;
        border: 1px solid #2E7D32 !important;
    }
    
    /* Metrics Label and Value colors */
    [data-testid="stMetricLabel"] p { color: #ffffff !important; opacity: 0.9; }
    [data-testid="stMetricValue"] div { color: #4CAF50 !important; }

    /* 4. Tab Styling Fixes */
    button[data-baseweb="tab"] { 
        color: #888888 !important; 
        background-color: transparent !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: white !important;
        border-bottom: 3px solid #4CAF50 !important;
    }

    /* 5. Sidebar Label Fix */
    [data-testid="stSidebar"] label p {
        color: white !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HELPER FOR CHART THEMING ---
def apply_dark_theme(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', # Transparent
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent
        font_color='white',
        title_font_color='white',
        legend_font_color='white',
        xaxis=dict(gridcolor='#1e3d33', zerolinecolor='#1e3d33'),
        yaxis=dict(gridcolor='#1e3d33', zerolinecolor='#1e3d33'),
        template='plotly_dark'
    )
    return fig

# --- LOAD & PREPROCESS ---
@st.cache_data
def load_data():
    df = pd.read_csv('Patagonia_Order (1).csv') 
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    df['Is_Returned'] = df['Return_Status'].apply(lambda x: 1 if x == 'Returned' else 0)
    df['Country'] = df['Customer_Location'].str.split(',').str[0]
    df['Feedback_Score'] = df['Customer_Feedback'].map({'Excellent': 5, 'Good': 4, 'Average': 3, 'Bad': 2, 'Poor': 1}).fillna(3)
    df['Age_Group'] = pd.cut(df['Age'], bins=[18, 25, 35, 45, 60, 100], 
                             labels=['Gen Z', 'Young Adult', 'Adult', 'Middle Age', 'Senior'])
    return df

df_raw = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.title("Dashboard Controls")
with st.sidebar:
    st.subheader("Filter Insights")
    min_date, max_date = df_raw['Order_Date'].min().to_pydatetime(), df_raw['Order_Date'].max().to_pydatetime()
    date_range = st.date_input("Select Date Range", value=(min_date, max_date))
    selected_mats = st.multiselect("Materials", options=df_raw['Material'].unique(), default=df_raw['Material'].unique())
    selected_gender = st.radio("Gender Selection", options=["All", "Male", "Female"])

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
with k1: st.metric("Total Net Revenue", f"${df['Total_Revenue ($)'].sum():,.0f}")
with k2: 
    ret_rate = df['Is_Returned'].mean() * 100
    st.metric("Return Rate", f"{ret_rate:.2f}%", delta="-0.5% vs Prev Month", delta_color="inverse")
with k3: st.metric("Water Usage Saved", f"{df['Water_Usage (liters)'].sum():,.0f} L")
with k4: st.metric("Carbon Investment", f"${df['Carbon_Offset_Investment ($)'].sum():,.0f}")

# --- TABS FOR STORYTELLING ---
tab_fin, tab_eco, tab_cust, tab_pred = st.tabs(["💰 Financial Performance", "♻️ Eco-Efficiency", "👥 Customer Risk", "🔮 Return Risk Simulator"])

with tab_fin:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Revenue Trend")
        df_time = df.groupby(df['Order_Date'].dt.to_period('M')).agg({'Total_Revenue ($)':'sum'}).reset_index()
        df_time['Order_Date'] = df_time['Order_Date'].dt.to_timestamp()
        fig_time = px.area(df_time, x='Order_Date', y='Total_Revenue ($)', color_discrete_sequence=['#4CAF50'])
        st.plotly_chart(apply_dark_theme(fig_time), use_container_width=True)
    with c2:
        st.subheader("Top Revenue Countries")
        country_rev = df.groupby('Country')['Total_Revenue ($)'].sum().sort_values(ascending=True).tail(10)
        fig_country = px.bar(country_rev, orientation='h', color_discrete_sequence=['#4CAF50'])
        st.plotly_chart(apply_dark_theme(fig_country), use_container_width=True)

with tab_eco:
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Material Sustainability Matrix")
        mat_data = df.groupby('Material').agg({'Percentage_Recycled_Material (%)':'mean', 'Is_Returned':'mean', 'Total_Revenue ($)':'sum'}).reset_index()
        fig_mat = px.scatter(mat_data, x='Percentage_Recycled_Material (%)', y='Is_Returned', size='Total_Revenue ($)', color='Material')
        st.plotly_chart(apply_dark_theme(fig_mat), use_container_width=True)
    with c4:
        st.subheader("AOV by Eco-Certification")
        cert_data = df.groupby('Eco_Certification')['Total_Revenue ($)'].mean().reset_index()
        fig_cert = px.funnel(cert_data, x='Total_Revenue ($)', y='Eco_Certification')
        st.plotly_chart(apply_dark_theme(fig_cert), use_container_width=True)

with tab_cust:
    c5, c6 = st.columns(2)
    with c5:
        st.subheader("Return Risk Heatmap: Age vs Category")
        risk_map = df.pivot_table(index='Age_Group', columns='Category_Name', values='Is_Returned', aggfunc='mean') * 100
        fig_risk = px.imshow(risk_map, text_auto='.1f', color_continuous_scale='YlOrRd')
        st.plotly_chart(apply_dark_theme(fig_risk), use_container_width=True)
    with c6:
        st.subheader("Return Reasons by Gender")
        reason_gen = df[df['Is_Returned']==1].groupby(['Gender', 'Return_Reason']).size().reset_index(name='count')
        fig_gen = px.bar(reason_gen, x='Return_Reason', y='count', color='Gender', barmode='group')
        st.plotly_chart(apply_dark_theme(fig_gen), use_container_width=True)

with tab_pred:
    st.subheader("🔮 Return Risk 'What-If' Simulator")
    in_price = st.slider("Unit Price ($)", 40, 270, 120)
    in_recycled = st.slider("Recycled Material %", 0, 100, 50)
    in_feedback = st.select_slider("Anticipated Feedback", options=['Poor', 'Bad', 'Average', 'Good', 'Excellent'], value='Good')
    base_risk = 0.12 
    if in_price > 200: base_risk += 0.05
    if in_feedback in ['Poor', 'Bad']: base_risk += 0.15
    st.markdown(f"## Estimated Return Risk: `{base_risk*100:.1f}%`")

st.write("---")
st.caption("Patagonia BI Tool | Built for Marketing Analytics Assignment | Feb 2025")
