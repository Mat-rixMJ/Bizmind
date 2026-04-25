from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import pandas as pd
import os
import sys

# Append current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db import engine

app = Flask(__name__)
app.secret_key = 'bizmind-secret-key-change-in-prod'

# Mock user for now or use the existing DB?
# Currently Streamlit uses modules/auth.py. Let's look at how that works.
# For now, let's create a dummy login.

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session['user_id'] = 1
        session['username'] = 'Admin'
        session['role'] = 'admin'
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Simple query to check user (from database)
        try:
            with engine.connect() as conn:
                user = pd.read_sql_query(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'", conn)
                if not user.empty:
                    session['user_id'] = int(user.iloc[0]['id'])
                    session['username'] = str(user.iloc[0]['username'])
                    session['role'] = str(user.iloc[0]['role'])
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid credentials')
        except Exception as e:
            flash(f'Database error: {e}')
            
    return "<h1>Login Page (To be styled)</h1><form method='post'><input name='username' placeholder='Username'><input name='password' type='password' placeholder='Password'><button>Login</button></form>"

@app.route('/')
@login_required
def dashboard():
    # Load stats
    try:
        with engine.connect() as conn:
            total_products = pd.read_sql_query("SELECT COUNT(*) as c FROM inventory", conn).iloc[0]['c']
            total_revenue = pd.read_sql_query("SELECT SUM(amount) as t FROM transactions WHERE type='income'", conn).iloc[0]['t']
            total_expense = pd.read_sql_query("SELECT SUM(amount) as t FROM transactions WHERE type='expense'", conn).iloc[0]['t']
            open_tickets = pd.read_sql_query("SELECT COUNT(*) as c FROM tickets WHERE status != 'resolved'", conn).iloc[0]['c']
    except Exception as e:
        total_products = total_revenue = total_expense = open_tickets = 0

    return render_template('dashboard.html', 
                           username=session.get('username'),
                           total_products=total_products,
                           total_revenue=total_revenue,
                           total_expense=total_expense,
                           open_tickets=open_tickets)

@app.route('/inventory')
@login_required
def inventory():
    # Load inventory items
    try:
        with engine.connect() as conn:
            products = pd.read_sql_query("SELECT * FROM inventory", conn).to_dict('records')
    except Exception as e:
        products = []

    return render_template('inventory.html', 
                           username=session.get('username'),
                           products=products)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
