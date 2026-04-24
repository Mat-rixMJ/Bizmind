import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import os
import sys

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Must be first Streamlit call
st.set_page_config(
    page_title="BizMind AI Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

from modules.auth import enforce_login, render_sidebar_user_block
enforce_login()
render_sidebar_user_block()

from database.db import engine
from utils.sidebar import render_sidebar_chat

# Sidebar chat
render_sidebar_chat(module_name="general")

# -- Main Dashboard --
st.title("🧠 Welcome to BizMind AI Assistant")
st.markdown(f"Hello, **{st.session_state.get('username', 'User')}**! Your all-in-one platform for business operations.")

col1, col2 = st.columns(2)
with col1:
    st.info("📦 **Inventory Management**\n\nTrack stock levels, monitor reorder alerts, and manage products.")
    st.warning("🤝 **Helpdesk System**\n\nCreate support tickets with instant AI-generated solutions.")
with col2:
    st.success("💰 **Accounting & Finance** *(Admin Only)*\n\nLog income and expenses, measure monthly profitability.")
    st.error("📊 **Data Analytics** *(Admin Only)*\n\nVisualize revenue trends, best sellers, and business KPIs.")

st.header("📈 Live Quick Stats")
try:
    with engine.connect() as conn:
        total_products = pd.read_sql_query("SELECT COUNT(*) as c FROM inventory", conn).iloc[0]['c']
        total_revenue = pd.read_sql_query("SELECT SUM(amount) as t FROM transactions WHERE type='income'", conn).iloc[0]['t']
        total_expense = pd.read_sql_query("SELECT SUM(amount) as t FROM transactions WHERE type='expense'", conn).iloc[0]['t']
        open_tickets = pd.read_sql_query("SELECT COUNT(*) as c FROM tickets WHERE status != 'resolved'", conn).iloc[0]['c']
        low_stock = pd.read_sql_query("SELECT COUNT(*) as c FROM inventory WHERE quantity <= reorder_level", conn).iloc[0]['c']

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Products", f"{total_products}")
    c2.metric("Total Revenue", f"₹{total_revenue:,.2f}" if total_revenue else "₹0.00")
    c3.metric("Total Expenses", f"₹{total_expense:,.2f}" if total_expense else "₹0.00")
    c4.metric("Active Tickets", f"{open_tickets}")
    c5.metric("⚠️ Low Stock", f"{low_stock}", delta=f"-{low_stock}" if low_stock > 0 else None, delta_color="inverse")
except Exception as e:
    st.error(f"Could not load quick stats: {e}")

st.markdown("---")
st.markdown("👈 **Get started by selecting a module from the sidebar navigation menu.**")
