import streamlit as st
import bcrypt
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import SessionLocal
from database.models import User

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def login(username, password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user and verify_password(password, user.password_hash):
            return user
        return None
    finally:
        db.close()

def render_login_form():
    # Centered, branded login layout
    st.markdown("""
    <style>
    .login-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .login-header h1 { font-size: 2.5rem; margin-bottom: 0; }
    .login-header p { color: #00C896; font-size: 1.1rem; margin-top: 0.25rem; }
    </style>
    <div class="login-header">
        <h1>🧠 BizMind</h1>
        <p>Enterprise AI Assistant — Secure Login</p>
    </div>
    """, unsafe_allow_html=True)
    
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("🚀 Access Dashboard", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    user = login(username, password)
                    if user:
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = user.username
                        st.session_state["role"] = user.role
                        st.success(f"Welcome back, {user.username}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Please contact your IT administrator.")
        
        st.markdown("""
        <div style="text-align:center; color:#888; font-size:0.8rem; margin-top:1rem;">
        Default: admin / admin123 &nbsp;|&nbsp; staff / staff123
        </div>
        """, unsafe_allow_html=True)

def enforce_login():
    if not st.session_state.get("authenticated", False):
        render_login_form()
        st.stop()

def require_admin():
    if st.session_state.get("role") != "admin":
        st.error("🔒 Unauthorized. Administrator access required for this module.")
        st.info("Please log in with an admin account to access this page.")
        st.stop()

def render_sidebar_user_block():
    """Renders user badge and logout button in sidebar."""
    username = st.session_state.get("username", "User")
    role = st.session_state.get("role", "standard")
    role_badge = "🛡️ Admin" if role == "admin" else "👤 Staff"
    role_color = "#00C896" if role == "admin" else "#FFA500"
    
    st.sidebar.markdown(f"""
    <div style="
        background: #1A1F2E;
        border: 1px solid {role_color};
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
    ">
        <div style="font-weight:bold; font-size:1rem;">🧠 BizMind</div>
        <div style="color:{role_color}; font-size:0.85rem;">{role_badge}: {username}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
