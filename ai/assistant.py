import os
import requests
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5")
OLLAMA_URL = "http://localhost:11434/api/chat"

from database.db import engine
from utils.logger import get_logger
logger = get_logger("ai.assistant")

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
    current_date = datetime.now().strftime("%Y-%m-%d")
    sql_prompt = f"""
    You are a strict SQL-only agent for a SQLite database. 
    User Question: "{user_input}"
    TODAY'S DATE: {current_date}
    
    TABLES:
    - inventory (id, product_name, category, quantity, unit_price, reorder_level) [NOTE: NO date/time column here, represents CURRENT stock only]
    - transactions (id, date, type, category, description, amount) [Use for history/dates]
    - tickets (id, title, description, priority, status)
    - sales (id, product_name, quantity_sold, sale_price, sale_date) [Use for sales history]
    
    KNOWN CATEGORIES: Electronics, Phones, Laptops, Components, Audio, Networking
    
    QUERY RULES:
    1. Output ONLY a valid SQLite SELECT query.
    2. STRING MATCHING: SQLite is CASE-SENSITIVE. Use `LIKE` for text.
    3. FUZZY MAPPING: 
       - "inoventry", "stock", "itms" -> `inventory`
       - "expences", "expns" -> `transactions` where type='expense'
       - "profet", "proft" -> `transactions` logic
    4. NO HALLUCINATION: Do NOT use columns like 'quantity_date', 'status' or 'timestamp' in the `inventory` table.
    5. DATE FILTERING: Use `strftime('%Y', date)` or `date LIKE '2026-%'`.
    6. REVENUE vs SALES: 
       - Use `transactions` table for total COMPANY REVENUE.
       - Use `sales` table for PRODUCT/CATEGORY trends.
    7. EXAMPLES:
       - "sales by category": SELECT i.category, SUM(s.quantity_sold * s.sale_price) as total FROM sales s JOIN inventory i ON s.product_name = i.product_name GROUP BY i.category ORDER BY total DESC;
       - "how many items": SELECT COUNT(*) FROM inventory;
    8. GREETINGS: If just 'hi', output 'NO_QUERY'.
    """
    
    payload_sql = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": sql_prompt}],
        "stream": False,
        "options": {"temperature": 0}
    }
    
    try:
        resp = requests.post(OLLAMA_URL, json=payload_sql, timeout=60)
        query = ""
        if resp.status_code == 200:
            query_raw = resp.json().get("message", {}).get("content", "").strip()
            # Clean up: strip markdown, extra tags, and everything after the first ';'
            query = query_raw.replace("```sql", "").replace("```", "").strip()
            if ";" in query: query = query.split(";")[0] + ";"
            
            db_context = ""
            # Better check for SELECT in any part of the first 20 chars
            is_select = "SELECT" in query[:20].upper()
            
            if "NO_QUERY" not in query.upper() and is_select:
                try:
                    with engine.connect() as conn:
                        df = pd.read_sql_query(query, conn)
                        if df.empty:
                            db_context = "The database search returned zero results."
                        else:
                            # Using markdown table for better model grounding
                            db_context = "### Database Results:\n" + df.to_markdown(index=False)
                    logger.info(f"AI Query Success: {query}")
                except Exception as e:
                    db_context = f"Database Error: {e}"
                    logger.error(f"AI Query Failed: {e}")
            else:
                db_context = "General conversational query. No database lookup performed."

            # 2. Final response generation - THE GROUNDING STEP
            final_prompt = f"""
            You are BizMind, a professional business analyst assistant.
            User Question: "{user_input}"
            
            REFERENCE DATA FROM DATABASE:
            {db_context}
            
            STRICT INSTRUCTIONS:
            1. Use ONLY the 'REFERENCE DATA' provided above to answer.
            2. CURRENCY vs QUANTITY: 
               - Use the Rupee symbol (₹) ONLY for financial amounts (Price, Revenue, Expense, Amount).
               - Do NOT use currency symbols for counts, quantities, or IDs (e.g., "20 items", NOT "₹20 items").
            3. If the data indicates 'zero results' or an Error, state that you couldn't find the records.
            4. NEVER make up data.
            5. Keep your answer professional and concise.
            """
            
            messages = [{"role": "system", "content": "You are a grounded business assistant."}] + chat_history + [{"role": "user", "content": final_prompt}]
            
            payload_final = {
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.1}
            }
            res_final = requests.post(OLLAMA_URL, json=payload_final, timeout=60)
            if res_final.status_code == 200:
                answer = res_final.json().get("message", {}).get("content", "")
                return answer.strip()
            else:
                return "I'm having trouble reflecting on the data right now."
        return "The AI system is temporarily unavailable."
    except Exception as e:
        logger.error(f"AI connection error: {e}")
        return "I encountered a system error while processing the AI response."
