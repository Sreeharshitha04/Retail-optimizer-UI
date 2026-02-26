import streamlit as st
import pandas as pd
import plotly.express as px

# Setup the page
st.set_page_config(page_title="Retail Optimizer V0", layout="wide")

# Sidebar for Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Inventory Dashboard", "AI Insights"])

# Load Mock Data
df = pd.read_csv("data/mock_data.csv")

if page == "Inventory Dashboard":
    st.title("📊 Inventory Dashboard")
    
    # Simple Chart using the Mock Data
    fig = px.bar(df, x="item_name", y=["current_stock", "predicted_demand"], barmode="group")
    st.plotly_chart(fig, use_container_width=True)

elif page == "AI Insights":
    st.title("💬 AI Market Assistant")
    st.chat_input("Ask about your stock (slang welcome!)")