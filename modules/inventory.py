import pandas as pd
import os
import sys

# Ensure we can import from database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import SessionLocal, engine
from database.models import Inventory, InventoryCreate
from pydantic import ValidationError

def get_inventory_summary():
    """Returns key metrics for the inventory dashboard using SQLAlchemy."""
    db = SessionLocal()
    try:
        total = db.query(Inventory).count()
        low = db.query(Inventory).filter(Inventory.quantity <= Inventory.reorder_level).count()
        
        # Calculate total stock value via Python or SQL
        items = db.query(Inventory).all()
        stock_val = sum(item.quantity * item.unit_price for item in items if item.unit_price)
        
        categories = len(set(item.category for item in items if item.category))
        
        return {
            "total_products": total,
            "low_stock_items": low,
            "total_stock_value": float(stock_val),
            "categories_count": categories
        }
    finally:
        db.close()

def get_all_products():
    """Returns a pandas DataFrame of all products in inventory via SQLAlchemy engine."""
    with engine.connect() as conn:
        df = pd.read_sql_query("SELECT id, product_name, category, quantity, unit_price, reorder_level, last_updated FROM inventory ORDER BY quantity ASC", conn)
        return df

def add_product(name, category, qty, price, reorder_level):
    """Adds a new product, validating data with Pydantic and saving via SQLAlchemy."""
    try:
        # Validate data
        validated_data = InventoryCreate(
            product_name=name, category=category, quantity=qty,
            unit_price=price, reorder_level=reorder_level
        )
    except ValidationError as e:
        print(f"Validation Error: {e}")
        return False

    db = SessionLocal()
    try:
        new_item = Inventory(
            product_name=validated_data.product_name,
            category=validated_data.category,
            quantity=validated_data.quantity,
            unit_price=validated_data.unit_price,
            reorder_level=validated_data.reorder_level
        )
        db.add(new_item)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error adding product: {e}")
        return False
    finally:
        db.close()

def update_stock(product_id, new_quantity):
    """Updates stock quantity conditionally via SQLAlchemy."""
    if new_quantity < 0:
        return False # simple constraint check

    db = SessionLocal()
    try:
        item = db.query(Inventory).filter(Inventory.id == product_id).first()
        if item:
            item.quantity = new_quantity
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error updating stock: {e}")
        return False
    finally:
        db.close()

def delete_product(product_id):
    """Deletes a product via SQLAlchemy."""
    db = SessionLocal()
    try:
        item = db.query(Inventory).filter(Inventory.id == product_id).first()
        if item:
            db.delete(item)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting product: {e}")
        return False
    finally:
        db.close()
