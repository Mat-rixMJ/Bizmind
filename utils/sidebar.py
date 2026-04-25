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
    Renders a premium floating chat bubble in the bottom-right corner.
    """
    # 1. Inject Premium Floating CSS (Fixed Positioning & Layout)
    st.markdown("""
        <style>
        /* Force the popover to the fixed bottom-right viewport position */
        div[data-testid="stPopover"] {
            position: fixed !important;
            bottom: 30px !important;
            right: 30px !important;
            left: auto !important;
            top: auto !important;
            width: 65px !important;
            height: 65px !important;
            z-index: 999999 !important;
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
        }

        /* Premium Floating Action Button (FAB) Styling */
        button[data-testid="stPopoverButton"] {
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%) !important;
            color: white !important;
            border-radius: 50% !important;
            width: 65px !important;
            height: 65px !important;
            min-width: 65px !important;
            min-height: 65px !important;
            box-shadow: 0px 8px 25px rgba(0, 123, 255, 0.4) !important;
            border: 2px solid rgba(255, 255, 255, 0.1) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 0 !important;
            margin: 0 !important;
            transition: all 0.3s ease !important;
        }

        button[data-testid="stPopoverButton"]:hover {
            transform: scale(1.1) rotate(5deg) !important;
            box-shadow: 0px 12px 30px rgba(0, 123, 255, 0.5) !important;
        }

        /* Hide the default Streamlit label, arrow, and carrot */
        button[data-testid="stPopoverButton"] p,
        button[data-testid="stPopoverButton"] div:nth-child(2),
        button[data-testid="stPopoverButton"] svg {
            display: none !important;
        }

        /* Center the icon container */
        button[data-testid="stPopoverButton"] div:first-child {
            margin: 0 !important;
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }

        /* Remove the bar background from the parent container and collapse it */
        .stElementContainer:has(div[data-testid="stPopover"]) {
            background: transparent !important;
            width: 0 !important;
            height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            position: absolute !important;
        }

        /* Premium Chat Window Styling */
        div[data-testid="stPopoverBody"] {
            width: 400px !important;
            height: 550px !important;
            border-radius: 20px !important;
            padding: 0 !important;
            background-color: #ffffff !important;
            color: #1e1e1e !important; /* Force dark text color */
            box-shadow: 0px 15px 50px rgba(0,0,0,0.2) !important;
            border: 1px solid rgba(0,0,0,0.1) !important;
            overflow-y: auto !important; /* Allow scrolling */
        }
        /* Ensure chat messages inside have dark text */
        div[data-testid="stPopoverBody"] [data-testid="stChatMessage"] {
            background-color: #f8f9fa !important;
            color: #1e1e1e !important;
            border: 1px solid #e9ecef !important;
        }
        div[data-testid="stPopoverBody"] p, div[data-testid="stPopoverBody"] span {
            color: #1e1e1e !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # 2. Render the Bubble (Popover)
    with st.popover("💬"):
        st.markdown("""
            <div style='background: #007bff; padding: 15px; color: white; margin: -20px -20px 10px -20px; border-radius: 15px 15px 0 0;'>
                <h3 style='margin:0; color:white;'>💬 BizMind AI</h3>
                <small style='color: rgba(255,255,255,0.8);'>Business Assistant</small>
            </div>
        """, unsafe_allow_html=True)
        
        if "global_chat" not in st.session_state:
            st.session_state["global_chat"] = []

        # Render History (Directly in popover to avoid 'black box' container issues)
        for msg in st.session_state["global_chat"]:
            with st.chat_message(msg["role"]):
                st.markdown(f"<span style='color: #1e1e1e;'>{msg['content']}</span>", unsafe_allow_html=True)

        # Chat Input (Moved slightly to ensure it stays in viewport)
        user_input = st.chat_input("Ask about your business...")
        
        if user_input:
            st.session_state["global_chat"].append({"role": "user", "content": user_input})
            # We don't use nested containers here to ensure visibility
            with st.chat_message("user"):
                st.markdown(f"<span style='color: #1e1e1e;'>{user_input}</span>", unsafe_allow_html=True)
            
            with st.chat_message("assistant"):
                with st.spinner("Processing..."):
                    history_window = st.session_state["global_chat"][-10:]
                    resp = get_assistant_response(user_input, module_name, chat_history=history_window[:-1])
                    st.markdown(f"<span style='color: #1e1e1e;'>{resp}</span>", unsafe_allow_html=True)
            
            st.session_state["global_chat"].append({"role": "assistant", "content": resp})
            st.rerun()
