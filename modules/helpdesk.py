import pandas as pd
import requests
import os
import sys

# Ensure we can import from database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import SessionLocal, engine
from database.models import Ticket, TicketCreate
from ai.assistant import OLLAMA_URL, OLLAMA_MODEL
from pydantic import ValidationError
from utils.logger import get_logger
logger = get_logger("modules.helpdesk")

def get_helpdesk_summary():
    """Returns key metrics for the helpdesk dashboard via SQLAlchemy."""
    db = SessionLocal()
    try:
        total = db.query(Ticket).count()
        open_t = db.query(Ticket).filter(Ticket.status == 'open').count()
        in_prog = db.query(Ticket).filter(Ticket.status == 'in-progress').count()
        critical = db.query(Ticket).filter(Ticket.status != 'resolved', Ticket.priority == 'high').count()
        resolved = db.query(Ticket).filter(Ticket.status == 'resolved').count()
        
        return {
            "total_tickets": total,
            "open": open_t,
            "in_progress": in_prog,
            "high_priority": critical,
            "resolved": resolved,
            # backward-compat aliases
            "open_tickets": open_t,
            "critical_tickets": critical,
            "resolved_tickets": resolved
        }
    finally:
        db.close()

def get_tickets(search_query=""):
    """Returns a pandas DataFrame of tickets matching the search via SQLAlchemy engine."""
    with engine.connect() as conn:
        query = "SELECT id, title, description, priority, status, created_at, resolved_at, ai_response FROM tickets"
        params = []
        if search_query:
            query += " WHERE title LIKE ? OR description LIKE ?"
            params.extend([f"%{search_query}%", f"%{search_query}%"])
        query += " ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 END, created_at DESC"
        
        df = pd.read_sql_query(query, conn, params=tuple(params))
        return df

def generate_ai_ticket_response(title, description):
    """Hits the local Ollama LLM to generate an immediate suggested fix."""
    prompt = f"A user submitted a new support ticket.\nTitle: '{title}'\nDescription: '{description}'\n\nProvide a very brief, professional first-response solution or troubleshooting step. Do not ask questions, just provide the helpful advice."
    
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful IT/Operations helpdesk assistant."},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=20)
        if response.status_code == 200:
            content = response.json().get("message", {}).get("content", "Our team will look into this shortly.")
            return content.strip()
        return "Internal system issue: Our human team will review your ticket shortly against priority."
    except Exception as e:
        return "Our human team will review your ticket shortly. (AI auto-response temporarily unavailable)"

def add_ticket(title, description, priority):
    """Adds a new support ticket via ORM and auto-generates AI response."""
    try:
        # Validate data
        validated_data = TicketCreate(
            title=title, description=description, priority=priority
        )
    except ValidationError as e:
        print(f"Validation Error: {e}")
        return False

    # Get immediate AI diagnostic 
    ai_response = generate_ai_ticket_response(validated_data.title, validated_data.description)
    
    db = SessionLocal()
    try:
        ticket = Ticket(
            title=validated_data.title,
            description=validated_data.description,
            priority=validated_data.priority.lower(),
            status='open',
            ai_response=ai_response
        )
        db.add(ticket)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding ticket: {e}")
        return False
    finally:
        db.close()

def update_ticket_status(ticket_id, new_status):
    """Updates the status of a specific ticket using SQLAlchemy."""
    db = SessionLocal()
    try:
        from sqlalchemy.sql import func
        t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if t:
            t.status = new_status
            if new_status == 'resolved':
                t.resolved_at = func.now()
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating ticket status: {e}")
        return False
    finally:
        db.close()
