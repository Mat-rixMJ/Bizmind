import pandas as pd
import os
import sys

# Ensure we can import from database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import SessionLocal, engine

def get_sales_data(start_date=None, end_date=None):
    with engine.connect() as conn:
        query = '''
            SELECT s.id, s.product_id, s.product_name, s.quantity_sold, 
                   s.sale_price, s.sale_date, i.category
            FROM sales s
            LEFT JOIN inventory i ON s.product_id = i.id
            WHERE 1=1
        '''
        params = []
        if start_date:
            query += " AND s.sale_date >= ?"
            params.append(start_date.strftime("%Y-%m-%d"))
        if end_date:
            query += " AND s.sale_date <= ?"
            params.append(end_date.strftime("%Y-%m-%d"))
            
        df = pd.read_sql_query(query, conn, params=tuple(params))
        df['total_revenue'] = df['quantity_sold'] * df['sale_price']
        return df

def get_analytics_summary(df):
    if df.empty:
        return {"total_revenue": 0.0, "units_sold": 0, "avg_order_value": 0.0, "best_seller": "N/A"}
        
    total_rev = df['total_revenue'].sum()
    total_units = df['quantity_sold'].sum()
    avg_order = total_rev / len(df) if len(df) > 0 else 0
    product_sales = df.groupby('product_name')['quantity_sold'].sum()
    best_seller = product_sales.idxmax() if not product_sales.empty else "N/A"
    
    return {
        "total_revenue": float(total_rev),
        "units_sold": int(total_units),
        "avg_order_value": float(avg_order),
        "best_seller": str(best_seller)
    }

def process_trend_data(df, time_group='Daily'):
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df['sale_date'] = pd.to_datetime(df['sale_date'])
    
    if time_group == 'Daily':
        df['period'] = df['sale_date'].dt.date
    elif time_group == 'Weekly':
        df['period'] = df['sale_date'].dt.to_period('W').apply(lambda r: r.start_time.date())
    elif time_group == 'Monthly':
        df['period'] = df['sale_date'].dt.to_period('M').apply(lambda r: r.start_time.date())
        
    trend = df.groupby('period')['total_revenue'].sum().reset_index()
    trend = trend.sort_values('period')
    trend['period'] = trend['period'].astype(str)
    return trend

def get_top_products_data(df):
    if df.empty:
        return pd.DataFrame()
    top = df.groupby('product_name')['total_revenue'].sum().reset_index()
    top = top.sort_values('total_revenue', ascending=False).head(5)
    return top

def get_category_sales(df):
    if df.empty:
        return pd.DataFrame()
    df['category'] = df['category'].fillna('Unknown')
    cat = df.groupby('category')['total_revenue'].sum().reset_index()
    return cat
