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
    st.title("BizMind Version 2.0")
    st.subheader("Secure Enterprise Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Access Dashboard")
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                user = login(username, password)
                if user:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = user.username
                    st.session_state["role"] = user.role
                    st.success(f"Welcome back, {user.username}! Redirecting...")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please contact IT.")

def enforce_login():
    if not st.session_state.get("authenticated", False):
        render_login_form()
        st.stop()

def require_admin():
    if st.session_state.get("role") != "admin":
        st.error("Unauthorized. Administrator access required for this module.")
        st.stop()
