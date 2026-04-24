import streamlit as st
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Support Helpdesk", page_icon="🤝", layout="wide")

from modules.auth import enforce_login, render_sidebar_user_block
enforce_login()
render_sidebar_user_block()

from modules.helpdesk import get_helpdesk_summary, get_tickets, add_ticket, update_ticket_status
from utils.sidebar import render_sidebar_chat

render_sidebar_chat(module_name="helpdesk")

st.title("🤝 Support Helpdesk")
st.markdown("Manage support tickets and deploy AI-automated first responses.")

summary = get_helpdesk_summary()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Open Tickets", summary['open'])
c2.metric("In Progress", summary['in_progress'])
c3.metric("Resolved", summary['resolved'])
c4.metric("🚨 High Priority (Active)", summary['high_priority'])

st.markdown("---")

col_form, col_list = st.columns([1, 2])

with col_form:
    st.subheader("🎫 Create New Ticket")
    st.markdown("Describe your issue below. Our AI will attempt to generate an immediate solution!")
    with st.form("add_ticket_form"):
        t_title = st.text_input("Issue Title")
        t_desc = st.text_area("Issue Description")
        t_prior = st.selectbox("Priority Level", ["low", "medium", "high"])
        if st.form_submit_button("Submit Ticket"):
            if t_title and t_desc:
                with st.spinner("AI is analyzing your issue..."):
                    success = add_ticket(t_title, t_desc, t_prior)
                if success:
                    st.success("Ticket created and AI response generated!")
                    st.rerun()
                else:
                    st.error("Failed to create ticket.")
            else:
                st.warning("Please fill in both the title and description.")

with col_list:
    st.subheader("🔍 Search Tickets")
    search_q = st.text_input("Search by keyword...", placeholder="e.g. Printer, Login")
    df_tickets = get_tickets(search_q)

    if not df_tickets.empty:
        st.write(f"Showing **{len(df_tickets)}** ticket(s).")
        for idx, row in df_tickets.iterrows():
            status_icon = "🟢" if row['status'] == 'resolved' else ("🟡" if row['status'] == 'in-progress' else "🔴")
            header = f"{status_icon} [#{row['id']}] {row['title']} (Priority: {str(row['priority']).upper()})"
            with st.expander(header):
                st.markdown(f"**Submitted:** {row['created_at']}")
                if row['status'] == 'resolved' and row['resolved_at']:
                    st.markdown(f"**Resolved:** {row['resolved_at']}")
                st.markdown(f"**Description:**\n{row['description']}")
                if row['ai_response']:
                    st.info(f"🤖 **AI Auto-Response / Solution:**\n\n{row['ai_response']}")
                status_options = ["open", "in-progress", "resolved"]
                curr_idx = status_options.index(row['status']) if row['status'] in status_options else 0
                new_status = st.selectbox("Update Status:", status_options, index=curr_idx, key=f"status_{row['id']}")
                if st.button("Save Status", key=f"btn_{row['id']}"):
                    if new_status != row['status']:
                        if update_ticket_status(row['id'], new_status):
                            st.success(f"Ticket #{row['id']} marked as {new_status}!")
                            st.rerun()
                    else:
                        st.warning("Status is unchanged.")
    else:
        st.info("No tickets found.")
