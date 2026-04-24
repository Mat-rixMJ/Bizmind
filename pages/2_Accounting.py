import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Accounting & Finance", page_icon="💰", layout="wide")

from modules.auth import enforce_login, require_admin, render_sidebar_user_block
enforce_login()
require_admin()
render_sidebar_user_block()

from modules.accounting import get_accounting_summary, get_transactions, get_monthly_data, add_transaction, get_unique_categories
from utils.sidebar import render_sidebar_chat

render_sidebar_chat(module_name="accounting")

st.title("💰 Accounting & Finance")

summary = get_accounting_summary()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Income", f"₹{summary['total_income']:,.2f}")
c2.metric("Total Expenses", f"₹{summary['total_expenses']:,.2f}")
profit_icon = "🟢" if summary['net_profit'] >= 0 else "🔴"
c3.metric("Net Profit", f"{profit_icon} ₹{summary['net_profit']:,.2f}")
month_color = "normal" if summary['this_month_balance'] >= 0 else "inverse"
c4.metric("This Month's Balance", f"₹{summary['this_month_balance']:,.2f}", delta_color=month_color)

st.markdown("---")

col_chart, col_form = st.columns([2, 1])

with col_chart:
    st.subheader("📊 Income vs Expense (Monthly)")
    monthly_df = get_monthly_data()
    if not monthly_df.empty:
        fig = px.bar(monthly_df, x='month', y=['income', 'expense'],
                     barmode='group',
                     color_discrete_map={'income': '#00C896', 'expense': '#ff4b4b'},
                     labels={'value': 'Amount (₹)', 'month': 'Month', 'variable': 'Type'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data to plot charts.")

with col_form:
    st.subheader("➕ Add Transaction")
    with st.form("add_transaction_form"):
        t_date = st.date_input("Date")
        t_type = st.selectbox("Type", options=["Income", "Expense"])
        t_cat = st.text_input("Category (e.g. Rent, Sales)")
        t_desc = st.text_input("Description")
        t_amount = st.number_input("Amount (₹)", min_value=1.0, value=100.0, format="%.2f")
        if st.form_submit_button("Record Transaction"):
            if t_cat and t_desc:
                success = add_transaction(t_date.strftime("%Y-%m-%d"), t_type, t_cat, t_desc, t_amount)
                if success:
                    st.success("Transaction recorded!")
                    st.rerun()
                else:
                    st.error("Error saving transaction.")
            else:
                st.warning("Category and Description are required.")

st.markdown("---")
st.subheader("📜 Transaction History")

f_col1, f_col2 = st.columns(2)
type_opt = f_col1.selectbox("Filter by Type", options=["All", "Income", "Expense"])
cat_options = get_unique_categories()
cat_opt = f_col2.selectbox("Filter by Category", options=cat_options)

df_tx = get_transactions(type_filter=type_opt, category_filter=cat_opt)

if not df_tx.empty:
    st.dataframe(df_tx, use_container_width=True, hide_index=True)
    csv_data = df_tx.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Transactions as CSV", data=csv_data, file_name='transactions_report.csv', mime='text/csv')
else:
    st.info("No transactions found based on current filters.")

st.markdown("---")
st.subheader("🧾 Profit & Loss Summary")
if summary['net_profit'] > 0:
    st.success(f"**Business is operating at a PROFIT.** Total Net Earnings: ₹{summary['net_profit']:,.2f}")
elif summary['net_profit'] < 0:
    st.error(f"**Business is operating at a LOSS.** Total Net Deficit: ₹{summary['net_profit']:,.2f}")
else:
    st.info("Business is breaking even.")
