import pandas as pd
from sqlalchemy.orm import Session
from database.models import Inventory, Transaction
from datetime import datetime
import io

# Common mappings for billing software
MAPPING_GUIDE = {
    'inventory': {
        'product_name': ['Item Name', 'Product Name', 'Product', 'Item', 'Particulars'],
        'category': ['Category', 'Group', 'Item Group'],
        'quantity': ['Stock', 'Quantity', 'Qty', 'Closing Stock', 'Available Stock'],
        'unit_price': ['Sales Price', 'Rate', 'Unit Price', 'Price'],
        'reorder_level': ['Reorder Level', 'Minimum Stock', 'Low Stock Alert']
    },
    'transactions': {
        'date': ['Date', 'Transaction Date', 'Voucher Date'],
        'type': ['Type', 'Transaction Type', 'Entry Type'],
        'category': ['Category', 'Account Group', 'Ledger'],
        'description': ['Description', 'Narration', 'Remarks'],
        'amount': ['Amount', 'Total', 'Value', 'Debit/Credit']
    }
}

def clean_currency(value):
    """Removes currency symbols, commas, and whitespace from a string."""
    if pd.isna(value) or value == "":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    
    # Remove 'INR', '₹', '$', and commas
    str_val = str(value).replace('INR', '').replace('₹', '').replace('$', '').replace(',', '').strip()
    try:
        return float(str_val)
    except ValueError:
        return 0.0

def auto_map_columns(df, target_type):
    """Attempt to map CSV columns to DB columns based on common names."""
    mapping = {}
    guide = MAPPING_GUIDE.get(target_type, {})
    
    for db_col, variations in guide.items():
        for col in df.columns:
            if col.strip() in variations or col.strip().lower() == db_col.lower():
                mapping[col] = db_col
                break
    return mapping

def import_data(file_bytes, file_type, target_table, db: Session):
    """
    Parses file (CSV/Excel) and injects into the specified table.
    """
    try:
        if file_type == 'csv':
            df = pd.read_csv(io.BytesIO(file_bytes))
        else:
            df = pd.read_excel(io.BytesIO(file_bytes))
            
        mapping = auto_map_columns(df, target_table)
        
        if not mapping:
            return False, "Could not automatically map columns. Please ensure your headers match common business terms."
        
        # Rename columns to match DB
        df = df.rename(columns=mapping)
        df = df[list(mapping.values())] # Only keep mapped columns
        
        # Clean numeric columns
        if 'unit_price' in df.columns:
            df['unit_price'] = df['unit_price'].apply(clean_currency)
        if 'amount' in df.columns:
            df['amount'] = df['amount'].apply(clean_currency)
        if 'quantity' in df.columns:
            df['quantity'] = df['quantity'].fillna(0).astype(int)
            
        count = 0
        for _, row in df.iterrows():
            data = row.to_dict()
            
            if target_table == 'inventory':
                obj = Inventory(**data)
            elif target_table == 'transactions':
                # Ensure date is string format as per model
                if 'date' in data and not isinstance(data['date'], str):
                    data['date'] = str(data['date'])
                obj = Transaction(**data)
            else:
                continue
                
            db.add(obj)
            count += 1
            
        db.commit()
        return True, f"Successfully imported {count} records into {target_table}."
        
    except Exception as e:
        db.rollback()
        return False, f"Import Error: {str(e)}"
