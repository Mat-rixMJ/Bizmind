import streamlit as st
import pandas as pd
import os
import sys

# Ensure project structure runs correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.auth import enforce_login
enforce_login()

from modules.inventory import get_inventory_summary, get_all_products, add_product, update_stock, delete_product
from app import render_sidebar_chat

# Page Config
st.set_page_config(page_title="Inventory Management", page_icon="📦", layout="wide")

# Sidebar Chat
render_sidebar_chat(module_name="inventory")

st.title("📦 Inventory Management")

# Fetch Data
summary = get_inventory_summary()
df_products = get_all_products()

# --- Alerts ---
if summary['low_stock_items'] > 0:
    st.error(f"⚠️ Alert: You have {summary['low_stock_items']} item(s) currently at or below reorder level!")

# --- KPI Cards ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Products", summary['total_products'])
c2.metric("Low Stock Items", summary['low_stock_items'])
c3.metric("Total Stock Value", f"₹{summary['total_stock_value']:,.2f}")
c4.metric("Categories", summary['categories_count'])

st.markdown("---")

# --- Inventory Table ---
st.subheader("Current Stock Levels")

def highlight_stock(row):
    """Applies color to rows where quantity <= reorder_level"""
    if row['quantity'] <= row['reorder_level']:
        return ['background-color: #ffcccc; color: black'] * len(row) # Red alert
    else:
        return ['background-color: #ccffcc; color: black'] * len(row) # Green healthy

if not df_products.empty:
    st.dataframe(
        df_products.style.apply(highlight_stock, axis=1), 
        use_container_width=True, 
        hide_index=True
    )
else:
    st.info("No products found in the inventory.")

st.markdown("---")

# --- Action Forms ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("➕ Add New Product")
    with st.form("add_product_form"):
        p_name = st.text_input("Product Name")
        p_cat = st.text_input("Category")
        
        c_qty, c_price = st.columns(2)
        p_qty = c_qty.number_input("Initial Quantity", min_value=0, value=0)
        p_price = c_price.number_input("Unit Price (₹)", min_value=0.0, value=0.0, format="%.2f")
        
        p_reorder = st.number_input("Reorder Level Alert", min_value=1, value=10)
        
        submit_add = st.form_submit_button("Add Product")
        if submit_add:
            if p_name and p_cat:
                success = add_product(p_name, p_cat, p_qty, p_price, p_reorder)
                if success:
                    st.success(f"Added {p_name} successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add product. Check logs.")
            else:
                st.warning("Please fill out name and category.")

with col2:
    st.subheader("🔄 Manage Stock")
    
    if not df_products.empty:
        # Create a dictionary for mapping friendly names to IDs
        product_options = {f"{row['product_name']} (ID: {row['id']})": row['id'] for idx, row in df_products.iterrows()}
        
        with st.form("update_stock_form"):
            selected_p = st.selectbox("Select Product to Update", options=list(product_options.keys()))
            selected_id = product_options[selected_p]
            
            # Find current quantity to show as default
            current_qty = int(df_products[df_products['id'] == selected_id]['quantity'].iloc[0])
            
            new_qty = st.number_input("New Quantity", min_value=0, value=current_qty)
            
            submit_update = st.form_submit_button("Update Quantity")
            if submit_update:
                success = update_stock(selected_id, new_qty)
                if success:
                    st.success("Stock updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update stock.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("❌ Delete Product")
        
        with st.form("delete_product_form"):
            selected_del_p = st.selectbox("Select Product to Delete", options=list(product_options.keys()), key="del_select")
            del_id = product_options[selected_del_p]
            
            submit_delete = st.form_submit_button("Delete Product")
            if submit_delete:
                success = delete_product(del_id)
                if success:
                    st.success("Product deleted successfully!")
                    st.rerun()
                else:
                    st.error("Could not delete product. It may be linked to existing sales records.")
    else:
        st.info("Add products to manage them.")
