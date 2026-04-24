import pandas as pd
import os
import sys
from datetime import datetime

# Ensure we can import from database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import SessionLocal, engine
from database.models import Transaction, TransactionCreate
from pydantic import ValidationError

def get_accounting_summary():
    db = SessionLocal()
    try:
        current_month = datetime.now().strftime("%Y-%m")
        transactions = db.query(Transaction).all()
        
        income = sum(t.amount for t in transactions if t.type == 'income')
        expense = sum(t.amount for t in transactions if t.type == 'expense')
        
        month_income = sum(t.amount for t in transactions if t.type == 'income' and t.date.startswith(current_month))
        month_expense = sum(t.amount for t in transactions if t.type == 'expense' and t.date.startswith(current_month))
        
        return {
            "total_income": income,
            "total_expenses": expense,
            "net_profit": income - expense,
            "this_month_balance": month_income - month_expense
        }
    finally:
        db.close()

def get_transactions(type_filter="All", category_filter="All"):
    with engine.connect() as conn:
        query = "SELECT id, date, type, category, description, amount, status FROM transactions WHERE 1=1"
        params = []
        
        if type_filter != "All":
            query += " AND type = ?"
            params.append(type_filter.lower())
        if category_filter != "All":
            query += " AND category = ?"
            params.append(category_filter)
            
        query += " ORDER BY date DESC"
        df = pd.read_sql_query(query, conn, params=tuple(params))
        return df

def get_monthly_data():
    with engine.connect() as conn:
        df = pd.read_sql_query("SELECT date, type, amount FROM transactions", conn)
        if df.empty:
            return pd.DataFrame()
        df['month'] = df['date'].str[:7]
        aggregated = df.groupby(['month', 'type'])['amount'].sum().reset_index()
        pivot_df = aggregated.pivot(index='month', columns='type', values='amount').fillna(0).reset_index()
        if 'income' not in pivot_df.columns:
             pivot_df['income'] = 0.0
        if 'expense' not in pivot_df.columns:
             pivot_df['expense'] = 0.0
        return pivot_df

def add_transaction(date, t_type, category, desc, amount):
    try:
        validated_data = TransactionCreate(
            date=date, type=t_type, category=category,
            description=desc, amount=amount
        )
    except ValidationError as e:
        print(f"Validation Error: {e}")
        return False

    db = SessionLocal()
    try:
        t = Transaction(
            date=validated_data.date,
            type=validated_data.type.lower(),
            category=validated_data.category,
            description=validated_data.description,
            amount=validated_data.amount,
            status='completed'
        )
        db.add(t)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error adding transaction: {e}")
        return False
    finally:
        db.close()

def get_unique_categories():
    db = SessionLocal()
    try:
        cats = db.query(Transaction.category).distinct().all()
        return ["All"] + [c[0] for c in cats if c[0]]
    finally:
        db.close()
