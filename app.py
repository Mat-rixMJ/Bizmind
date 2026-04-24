import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import os
import sys

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set page config for wide layout across the entire app
st.set_page_config(
    page_title="BizMind AI Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

from modules.auth import enforce_login
enforce_login()

from database.db import get_connection
from ai.assistant import get_assistant_response

# -- Shared Sidebar Chat Component (to be used across pages) --
def render_sidebar_chat(module_name="general"):
    """
    Renders a persistent chat interface in the Streamlit sidebar.
    Keeps chat history in st.session_state based on the module.
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"💬 Chat with BizMind ({module_name.capitalize()})")
    
    state_key = f"chat_history_{module_name}"
    if state_key not in st.session_state:
        st.session_state[state_key] = []
        
    # Display chat history for this module
    chat_container = st.sidebar.container(height=300)
    with chat_container:
        for msg in st.session_state[state_key]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
    # Chat input
    user_input = st.sidebar.chat_input("Ask me anything...")
    if user_input:
        # Append user msg to UI
        st.session_state[state_key].append({"role": "user", "content": user_input})
        with chat_container:
            with st.chat_message("user"):
                st.write(user_input)
                
            # Fetch AI Response using local Ollama
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # We pass the prior history to keep conversational context
                    resp = get_assistant_response(user_input, module_name, chat_history=st.session_state[state_key][:-1])
                    st.write(resp)
                    
        # Append assistant msg to history
        st.session_state[state_key].append({"role": "assistant", "content": resp})

# -- Main Page UI --
def main():
    st.title("🧠 Welcome to BizMind AI Assistant")
    st.markdown("Your all-in-one platform for business operations, powered by intelligent local AI.")
    
    # Overview Cards
    col1, col2 = st.columns(2)
    with col1:
        st.info("📦 **Inventory Management**\n\nTrack stock levels, monitor reorder benchmarks, and manage your products.")
        st.warning("🤝 **Helpdesk System**\n\nMonitor support tickets and let AI generate first-response solutions instantly.")
    with col2:
        st.success("💰 **Accounting & Finance**\n\nLog income and expenses effortlessly, and measure your monthly profitability.")
        st.error("📊 **Data Analytics**\n\nVisualize revenue trends, best sellers, and crucial business KPI metrics.")

    # Quick Stats Overview
    st.header("📈 Live Quick Stats")
    
    from database.db import engine
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            total_products = pd.read_sql_query("SELECT COUNT(*) as c FROM inventory", conn).iloc[0]['c']
            total_revenue = pd.read_sql_query("SELECT SUM(amount) as t FROM transactions WHERE type='income'", conn).iloc[0]['t']
            total_expense = pd.read_sql_query("SELECT SUM(amount) as t FROM transactions WHERE type='expense'", conn).iloc[0]['t']
            open_tickets = pd.read_sql_query("SELECT COUNT(*) as c FROM tickets WHERE status != 'resolved'", conn).iloc[0]['c']
        
        scol1, scol2, scol3, scol4 = st.columns(4)
        scol1.metric("Total Products", f"{total_products}")
        scol2.metric("Total Revenue", f"₹{total_revenue:,.2f}" if total_revenue else "₹0.00")
        scol3.metric("Total Expenses", f"₹{total_expense:,.2f}" if total_expense else "₹0.00")
        scol4.metric("Active Tickets", f"{open_tickets}")
    except Exception as e:
        st.error(f"Could not load quick stats: {e}")
        
    st.markdown("---")
    st.markdown("👈 **Get started by selecting a module from the sidebar navigation menu.**")
    
    # Render the persistent sidebar chat
    # We pass 'analytics' or just 'home' - here we use 'home' context which won't load any specific huge table
    # But for a general overview, 'analytics' pulls both sales and products. Let's use 'analytics' context for home.
    render_sidebar_chat(module_name="analytics")

if __name__ == "__main__":
    main()
