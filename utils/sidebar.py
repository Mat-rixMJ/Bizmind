"""
Standalone sidebar chat component.
Imported by all pages — does NOT import app.py to avoid circular execution.
"""
import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.assistant import get_assistant_response

def render_sidebar_chat(module_name="general"):
    """
    Renders a persistent unified chat in the sidebar.
    All pages share a single global chat history preserved across navigation.
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("💬 BizMind AI Chat")

    if "global_chat" not in st.session_state:
        st.session_state["global_chat"] = []

    chat_container = st.sidebar.container(height=280)
    with chat_container:
        for msg in st.session_state["global_chat"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    user_input = st.sidebar.chat_input("Ask me anything about your business...")
    if user_input:
        st.session_state["global_chat"].append({"role": "user", "content": user_input})
        with chat_container:
            with st.chat_message("user"):
                st.write(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    history_window = st.session_state["global_chat"][-10:]
                    resp = get_assistant_response(user_input, module_name, chat_history=history_window[:-1])
                    st.write(resp)
        st.session_state["global_chat"].append({"role": "assistant", "content": resp})
