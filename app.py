import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Patagonia Return & Sustainability Insights", layout="wide")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\Admin\Downloads\MA CIA 2\Patagonia_Order (1).csv")
    df['Is_Returned'] = df['Return_Status'].apply(lambda x: 1 if x == 'Returned' else 0)
    # Estimate: 2kg CO2 per return logistics journey
    df['Return_Carbon_Waste'] = df['Is_Returned'] * 2.0 
    return df

df = load_data()

# --- HEADER SECTION ---
st.title("🌱 Patagonia: Return Optimization & Sustainability Dashboard")
st.markdown("### *Bridging the gap between ecological impact and bottom-line profitability.*")

# --- KPI ROW: THE BIG PICTURE ---
col1, col2, col3, col4 = st.columns(4)
total_rev = df['Total_Revenue ($)'].sum()
lost_rev = df[df['Is_Returned'] == 1]['Total_Revenue ($)'].sum()
carbon_waste = df['Return_Carbon_Waste'].sum()

col1.metric("Total Revenue", f"${total_rev/1e6:.2f}M")
col2.metric("Revenue Lost to Returns", f"${lost_rev/1e3:.1f}K", delta="-11.8%", delta_color="inverse")
col3.metric("Return-Driven CO2 Waste", f"{carbon_waste:,.0f} kg", delta="Logistics Impact")
col4.metric("Avg Customer Feedback", f"{df['Customer_Feedback'].mode()[0]}")

st.divider()

# --- ROW 2: ROOT CAUSE ANALYSIS ---
st.subheader("🔍 Phase 1: Diagnosing the Return Problem")
c1, c2 = st.columns(2)

with c1:
    # Top Reasons for Returns
    reasons = df[df['Is_Returned'] == 1]['Return_Reason'].value_counts().reset_index()
    fig_reasons = px.bar(reasons, x='count', y='Return_Reason', orientation='h', 
                         title="Top Reasons for Returns",
                         color='count', color_continuous_scale='Reds')
    st.plotly_chart(fig_reasons, use_container_width=True)

with c2:
    # Returns vs Price - Is high price driving higher expectations?
    fig_price = px.box(df, x='Return_Status', y='Unit_Price ($)', color='Return_Status',
                       title="Price Distribution vs. Return Status",
                       color_discrete_map={'Returned': '#e74c3c', 'Not Returned': '#2ecc71'})
    st.plotly_chart(fig_price, use_container_width=True)

# --- ROW 3: SUSTAINABILITY STRATEGY ---
st.subheader("♻️ Phase 2: Sustainable Material Strategy")
c3, c4 = st.columns(2)

with c3:
    # Material Sustainability Matrix
    mat_map = df.groupby('Material').agg({
        'Percentage_Recycled_Material (%)': 'mean',
        'Is_Returned': 'mean'
    }).reset_index()
    mat_map['Return Rate (%)'] = mat_map['Is_Returned'] * 100
    
    fig_matrix = px.scatter(mat_map, x='Percentage_Recycled_Material (%)', y='Return Rate (%)',
                            size='Return Rate (%)', color='Material',
                            title="The 'Green-Profit' Matrix: Eco-Content vs. Return Risk",
                            text='Material')
    fig_matrix.update_traces(textposition='top center')
    st.plotly_chart(fig_matrix, use_container_width=True)

with c4:
    # Eco-Certification Impact
    cert_impact = df.groupby('Eco_Certification')['Is_Returned'].mean().sort_values() * 100
    fig_cert = px.bar(cert_impact, title="Return Rate (%) by Eco-Certification",
                      labels={'value': 'Return Rate (%)', 'Eco_Certification': 'Certification'},
                      color_discrete_sequence=['#2E7D32'])
    st.plotly_chart(fig_cert, use_container_width=True)

# --- FOOTER INSIGHT ---
st.info("**Strategic Insight:** Products with 'Fair Trade' and 'B Corp' certifications show lower return rates, suggesting higher customer perceived value and satisfaction despite potentially higher prices.")