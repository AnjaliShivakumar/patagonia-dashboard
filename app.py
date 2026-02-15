import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Patagonia BI Dashboard", layout="wide")

# --- 2. CLEAN CSS (Works in Light & Dark Mode) ---
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        background-color: rgba(0,0,0,0.03);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING ---
@st.cache_data
def load_data():
    df = pd.read_csv('Patagonia_Order (1).csv') 
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    df['Is_Returned'] = df['Return_Status'].apply(lambda x: 1 if x == 'Returned' else 0)
    df['Age_Group'] = pd.cut(df['Age'], bins=[18, 25, 35, 45, 60, 100], 
                             labels=['Gen Z', 'Young Adult', 'Adult', 'Middle Age', 'Senior'])
    return df

df_raw = load_data()

# --- 4. SIDEBAR FILTERS ---
st.sidebar.header("Dashboard Filters")
selected_mats = st.sidebar.multiselect("Select Materials", 
                                       options=df_raw['Material'].unique(), 
                                       default=df_raw['Material'].unique())
selected_gender = st.sidebar.radio("View by Gender", options=["All", "Male", "Female"])

# Filtering Logic
df = df_raw[df_raw['Material'].isin(selected_mats)]
if selected_gender != "All":
    df = df[df['Gender'] == selected_gender]

# --- 5. MAIN HEADER ---
st.title("🌲 Patagonia: Strategic Return Intelligence")
st.write("**Marketing Analytics CIA 3**")

# --- 6. KPI METRICS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${df['Total_Revenue ($)'].sum():,.0f}")
col2.metric("Return Rate", f"{(df['Is_Returned'].mean()*100):.2f}%")
col3.metric("Water Saved (L)", f"{df['Water_Usage (liters)'].sum():,.0f}")
col4.metric("Carbon Investment", f"${df['Carbon_Offset_Investment ($)'].sum():,.0f}")

st.divider()

# --- 7. TABS (Including the Simulator) ---
tab1, tab2, tab3, tab4 = st.tabs(["💰 Performance", "🌍 Eco-Metrics", "👥 Risk Analysis", "🔮 Prediction Simulator"])

with tab1:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Monthly Revenue Trend")
        df_time = df.groupby(df['Order_Date'].dt.to_period('M'))['Total_Revenue ($)'].sum().reset_index()
        df_time['Order_Date'] = df_time['Order_Date'].dt.to_timestamp()
        fig1 = px.area(df_time, x='Order_Date', y='Total_Revenue ($)', color_discrete_sequence=['#2E7D32'])
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        st.subheader("Return Status Split")
        fig2 = px.pie(df, names='Return_Status', hole=0.4, color_discrete_sequence=['#2E7D32', '#d9534f'])
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Sustainability vs. Return Risk")
    mat_data = df.groupby('Material').agg({'Percentage_Recycled_Material (%)':'mean', 'Is_Returned':'mean'}).reset_index()
    fig3 = px.scatter(mat_data, x='Percentage_Recycled_Material (%)', y='Is_Returned', 
                      size='Is_Returned', color='Material', title="Recycled % vs Return Rate")
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.subheader("Strategic Return Risk Heatmap (%)")
    risk_map = df.pivot_table(index='Age_Group', columns='Category_Name', values='Is_Returned', aggfunc='mean') * 100
    fig4 = px.imshow(risk_map, text_auto='.1f', color_continuous_scale='YlOrRd')
    st.plotly_chart(fig4, use_container_width=True)

with tab4:
    st.subheader("🔮 Return Risk 'What-If' Simulator")
    st.write("Adjust product specs to estimate return probability based on historical patterns.")
    
    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        s_price = st.slider("Product Price ($)", 40, 270, 150)
        s_rec = st.slider("Recycled Material Content (%)", 0, 100, 50)
    with sim_col2:
        s_feedback = st.select_slider("Expected Customer Feedback", 
                                      options=['Poor', 'Bad', 'Average', 'Good', 'Excellent'], 
                                      value='Good')
    
    # Simple logic based on notebook findings: 
    # High price and low feedback = High risk
    risk_score = 11.5 + (s_price / 50) 
    if s_feedback in ['Poor', 'Bad']: risk_score += 10
    if s_rec > 70: risk_score -= 3
    
    st.metric("Estimated Return Probability", f"{risk_score:.1f}%")
    if risk_score > 18:
        st.error("⚠️ High Risk: Suggest reviewing product description or sizing.")
    else:
        st.success("✅ Stable Risk: Predicted return rate is within normal limits.")

st.write("---")
st.caption("Patagonia BI Tool | Marketing Analytics Assignment | Feb 2025")
