import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import os
import sys

# Ensure project structure runs correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.auth import enforce_login, require_admin
enforce_login()
require_admin()

from modules.analytics import (
    get_sales_data, get_analytics_summary, 
    process_trend_data, get_top_products_data, get_category_sales
)
from app import render_sidebar_chat

# Page Config
st.set_page_config(page_title="Data Analytics", page_icon="📊", layout="wide")

# Sidebar Chat
render_sidebar_chat(module_name="analytics")

st.title("📊 Data Analytics Dashboard")
st.markdown("Track your sales performance and revenue trends over time.")

# --- Global Date Filter ---
st.markdown("### 📅 Filter Data")
col_start, col_end, col_group = st.columns(3)

# Default to last 90 days
default_start = datetime.now().date() - timedelta(days=90)
start_date = col_start.date_input("Start Date", value=default_start)
end_date = col_end.date_input("End Date", value=datetime.now().date())
time_group = col_group.selectbox("Chart Aggregation", ["Daily", "Weekly", "Monthly"])

# Fetch base dataframe filtered by date
df_sales = get_sales_data(start_date, end_date)

st.markdown("---")

# --- KPI Cards ---
summary = get_analytics_summary(df_sales)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"₹{summary['total_revenue']:,.2f}")
c2.metric("Units Sold", summary['units_sold'])
c3.metric("Avg Order Value", f"₹{summary['avg_order_value']:,.2f}")
c4.metric("🏆 Best Seller", summary['best_seller'])

st.markdown("---")

# --- Visualizations ---
if df_sales.empty:
    st.warning("No sales data available for the selected date range.")
else:
    # 1. Trend Line Chart
    st.subheader(f"📈 Revenue Trend ({time_group})")
    trend_df = process_trend_data(df_sales, time_group)
    fig_trend = px.line(trend_df, x='period', y='total_revenue', markers=True,
                        labels={'total_revenue': 'Revenue (₹)', 'period': 'Date'})
    fig_trend.update_traces(line_color='#1f77b4', line_width=3)
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Bottom Row: Bar chart and Pie chart
    col_bar, col_pie = st.columns(2)
    
    # 2. Top 5 Products Bar Chart
    with col_bar:
        st.subheader("🔥 Top 5 Products by Revenue")
        top_df = get_top_products_data(df_sales)
        fig_bar = px.bar(top_df, x='total_revenue', y='product_name', orientation='h',
                         labels={'total_revenue': 'Revenue (₹)', 'product_name': ''},
                         color='total_revenue', color_continuous_scale='Blues')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)
        
    # 3. Sales by Category Pie Chart
    with col_pie:
        st.subheader("🍕 Sales by Category")
        cat_df = get_category_sales(df_sales)
        fig_pie = px.pie(cat_df, values='total_revenue', names='category',
                         hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)
