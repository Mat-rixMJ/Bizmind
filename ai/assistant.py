import os
import requests
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5")
OLLAMA_URL = "http://localhost:11434/api/chat"

from database.db import engine

def execute_read_query(query):
    """Executes a SQL SELECT query dynamically and returns results."""
    try:
        with engine.connect() as conn:
            if not query.strip().upper().startswith("SELECT"):
                return "Error: Only SELECT queries are permitted."
            df = pd.read_sql_query(query, conn)
            return df.to_csv(index=False)
    except Exception as e:
        return f"Database Error: {e}"

def get_assistant_response(user_input, module_name="general", chat_history=None):
    if chat_history is None:
         chat_history = []
         
    # 1. Ask Ollama to generate a SQL query if needed
    sql_prompt = f"""
    You are an intelligent business database agent. The user is asking: "{user_input}"
    Based on the following SQLite schema, write ONE raw SQL 'SELECT' query to answer their question. 
    If a query isn't needed (e.g. general greeting), just reply 'NO_QUERY'.
    Only output the pure SQL query or 'NO_QUERY', nothing else.
    
    Schema:
    CREATE TABLE inventory (id INTEGER, product_name VARCHAR, category VARCHAR, quantity INTEGER, unit_price FLOAT, reorder_level INTEGER);
    CREATE TABLE transactions (id INTEGER, date VARCHAR, type VARCHAR, category VARCHAR, description VARCHAR, amount FLOAT);
    CREATE TABLE tickets (id INTEGER, title VARCHAR, description VARCHAR, priority VARCHAR, status VARCHAR);
    CREATE TABLE sales (id INTEGER, product_name VARCHAR, quantity_sold INTEGER, sale_price FLOAT, sale_date VARCHAR);
    """
    
    payload_sql = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": sql_prompt}],
        "stream": False
    }
    
    try:
        resp = requests.post(OLLAMA_URL, json=payload_sql, timeout=30)
        if resp.status_code == 200:
            query = resp.json().get("message", {}).get("content", "").strip()
            # Clean up markdown if model outputs it
            if query.startswith("```sql"): query = query[6:]
            if query.startswith("```"): query = query[3:]
            if query.endswith("```"): query = query[:-3]
            query = query.strip()
            
            db_context = "No database data needed."
            if "NO_QUERY" not in query and query.upper().startswith("SELECT"):
                db_context = execute_read_query(query)
            
            # 2. Final response generation
            final_prompt = f"""
            You are BizMind, the AI assistant for business operations.
            The user asked: "{user_input}"
            
            Here is the live data retrieved from the database to answer their question:
            {db_context}
            
            Provide a helpful, precise, and conversational answer based only on this data. Do not show the SQL query to the user.
            """
            
            messages = [{"role": "system", "content": "You are BizMind."}] + chat_history + [{"role": "user", "content": final_prompt}]
            
            payload_final = {
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False
            }
            res_final = requests.post(OLLAMA_URL, json=payload_final, timeout=30)
            if res_final.status_code == 200:
                answer = res_final.json().get("message", {}).get("content", "")
                return answer.strip()
            else:
                 return "Error getting final response."
        return "Internal system issue with local AI."
    except Exception as e:
        return f"AI connection error: {e}"
