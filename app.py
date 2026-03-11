import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
from streamlit_mic_recorder import speech_to_text # type: ignore

# 1. PAGE CONFIG
st.set_page_config(page_title="Kirana Pro | Secure AI", layout="wide", page_icon="🏪")

# --- CUSTOM CSS (Login & Layout) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .login-card {
        background: linear-gradient(145deg, #1e2129, #16191f);
        padding: 40px; border-radius: 20px; border: 1px solid #333;
        text-align: center; margin-bottom: 20px;
    }
    .voice-container {
        position: fixed; bottom: 30px; right: 30px; z-index: 1000;
        background: #1a1c24; padding: 10px; border-radius: 50px; border: 1px solid #00ffcc;
    }
    [data-testid="stMetric"] { background-color: #1a1c24; padding: 15px; border-radius: 12px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# 2. SESSION STATE
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. LOGIN PAGE ---
if not st.session_state.logged_in:
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="login-card"><h1 style="color: #00ffcc;">🏪 Kirana Pro</h1><p style="color: #888;">Secure Retail Intelligence</p></div>', unsafe_allow_html=True)
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Unlock Dashboard 🚀", use_container_width=True):
            if user == "admin" and pw == "kirana123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
    st.stop()

# --- 4. DATA ENGINE ---
@st.cache_data
def load_data():
    file_path = "data/mock_data.csv"
    if not os.path.exists(file_path):
        st.error("CSV Missing!")
        st.stop()
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip().str.replace('ï»¿', '').str.replace('﻿', '')
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()
latest_date = df['date'].max()
latest_df = df[df['date'] == latest_date]

# --- 5. AI LOGIC (DATA-ACCURATE) ---
def process_query(query):
    query = query.lower()
    low_items = latest_df[latest_df['status'] == 'RESTOCK']['item_name'].tolist()
    if any(x in query for x in ["low", "restock", "khatam"]):
        return f"Sir, current stock reports show {', '.join(low_items)} are low." if low_items else "All stock levels are currently stable."
    elif "popular" in query or "demand" in query:
        top_item = latest_df.loc[latest_df['predicted_demand'].idxmax()]['item_name']
        return f"The item with the highest predicted demand is {top_item}."
    return "I am analyzing that. You can check the specific trends in the dashboard charts."

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🤖 Kirana AI Chat")
    for m in st.session_state.messages[-4:]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    
    if chat_prompt := st.chat_input("Ask about stock..."):
        st.session_state.messages.append({"role": "user", "content": chat_prompt})
        st.session_state.messages.append({"role": "assistant", "content": process_query(chat_prompt)})
        st.rerun()

    st.divider()
    if st.button("Logout 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- 7. MAIN DASHBOARD ---
st.title("📈 Shop Intelligence Dashboard")

# Top Metrics
m1, m2, m3 = st.columns(3)
m1.metric("Items Monitored", len(latest_df))
m2.metric("Low Stock Alerts", len(latest_df[latest_df['status'] == 'RESTOCK']))
m3.metric("Shop Health", f"{int(((len(latest_df)-len(latest_df[latest_df['status'] == 'RESTOCK']))/len(latest_df))*89)}%")

st.divider()

# --- LAYOUT: PICKER LEFT, GRAPH RIGHT ---
col_picker, col_graph = st.columns([1, 2.5])

with col_picker:
    st.subheader("Select Item")
    item_choice = st.selectbox("Search Product:", df['item_name'].unique())
    item_now = latest_df[latest_df['item_name'] == item_choice].iloc[0]
    
    # Quick Info Cards
    st.info(f"**Current Stock:** {item_now['current_stock']} units")
    st.info(f"**Status:** {item_now['status']}")

with col_graph:
    item_history = df[df['item_name'] == item_choice].sort_values('date')
    fig = px.area(item_history, x='date', y=['current_stock', 'predicted_demand'], 
                  title=f"Demand Forecast: {item_choice}",
                  color_discrete_map={"current_stock": "#00ffcc", "predicted_demand": "#ff4b4b"},
                  template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- LAYOUT: FULL TABLE BELOW ---
st.subheader("📋 Full Inventory Master List")

def style_status(val):
    color = '#4f1b1b' if val == 'RESTOCK' else '#1b4f2e'
    return f'background-color: {color}; color: white; font-weight: bold; border-radius: 4px;'

styled_df = latest_df[['item_name', 'current_stock', 'status']].style.applymap(style_status, subset=['status'])
st.dataframe(styled_df, use_container_width=True, hide_index=True)

# --- 8. FLOATING VOICE ASSISTANT ---
st.markdown('<div class="voice-container">', unsafe_allow_html=True)
v_text = speech_to_text(language='en', start_prompt="🎙️ Voice", stop_prompt="Stop", key='v_btn')
st.markdown('</div>', unsafe_allow_html=True)

if v_text:
    st.session_state.messages.append({"role": "user", "content": v_text})
    st.session_state.messages.append({"role": "assistant", "content": process_query(v_text)})
    st.rerun()