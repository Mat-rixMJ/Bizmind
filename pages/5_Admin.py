import streamlit as st
import pandas as pd
import bcrypt
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Admin Panel", page_icon="🛡️", layout="wide")

from modules.auth import enforce_login, require_admin, render_sidebar_user_block
enforce_login()
require_admin()
render_sidebar_user_block()

from database.db import SessionLocal
from database.models import User
from utils.sidebar import render_sidebar_chat

render_sidebar_chat(module_name="general")

st.title("🛡️ Admin Control Panel")
st.markdown("Manage users, roles, and system configuration.")

db = SessionLocal()
users = db.query(User).all()

st.subheader("👥 All Users")
if users:
    st.dataframe(pd.DataFrame([{"ID": u.id, "Username": u.username, "Role": u.role} for u in users]),
                 use_container_width=True, hide_index=True)
else:
    st.info("No users found.")

st.markdown("---")
col_add, col_role, col_del = st.columns(3)

with col_add:
    st.subheader("➕ Add New User")
    with st.form("add_user_form"):
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        new_role = st.selectbox("Role", ["standard", "admin"])
        if st.form_submit_button("Create User", use_container_width=True):
            if not new_username or not new_password:
                st.error("Username and Password are required.")
            elif db.query(User).filter(User.username == new_username).first():
                st.error(f"Username '{new_username}' already exists.")
            else:
                hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                db.add(User(username=new_username, password_hash=hashed, role=new_role))
                db.commit()
                st.success(f"User '{new_username}' created as {new_role}!")
                st.rerun()

with col_role:
    st.subheader("🔄 Change User Role")
    current_user = st.session_state.get("username")
    role_options = {u.username: u for u in users if u.username != current_user}
    with st.form("change_role_form"):
        if role_options:
            target_user = st.selectbox("Select User", list(role_options.keys()))
            new_role_val = st.selectbox("New Role", ["standard", "admin"])
            if st.form_submit_button("Update Role", use_container_width=True):
                role_options[target_user].role = new_role_val
                db.commit()
                st.success(f"'{target_user}' is now {new_role_val}!")
                st.rerun()
        else:
            st.info("No other users to manage.")
            st.form_submit_button("Update Role", disabled=True)

with col_del:
    st.subheader("❌ Delete User")
    del_options = {u.username: u for u in users if u.username != current_user}
    with st.form("delete_user_form"):
        if del_options:
            del_target = st.selectbox("Select User to Delete", list(del_options.keys()))
            st.warning("⚠️ This action cannot be undone.")
            if st.form_submit_button("Delete User", use_container_width=True):
                db.delete(del_options[del_target])
                db.commit()
                st.success(f"User '{del_target}' deleted.")
                st.rerun()
        else:
            st.info("No other users to delete.")
            st.form_submit_button("Delete User", disabled=True)

db.close()
