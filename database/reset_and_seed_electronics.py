import random
import os
import sys
from datetime import datetime, timedelta
import bcrypt

# Ensure we can import from database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import SessionLocal, init_db
from database.models import User, Inventory, Transaction, Sale, Ticket

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_electronics_company():
    db = SessionLocal()
    
    # 1. Users
    print("Resetting Users...")
    db.query(User).delete()
    users = [
        User(username="admin", password_hash=hash_password("admin123"), role="admin"),
        User(username="staff", password_hash=hash_password("staff123"), role="standard")
    ]
    db.add_all(users)
    db.commit()

    # 2. Inventory (Electronic Specialist)
    print("Resetting Inventory (Electronics)...")
    db.query(Inventory).delete()
    products_data = [
        # Laptops
        ("Dell XPS 13", "Laptops", 15, 110000.0, 5),
        ("MacBook Air M2", "Laptops", 10, 95000.0, 3),
        ("Asus ROG Zephyrus", "Laptops", 8, 145000.0, 2),
        ("HP Spectre x360", "Laptops", 12, 125000.0, 4),
        # Smartphones
        ("iPhone 15 Pro", "Phones", 20, 134000.0, 5),
        ("Samsung Galaxy S24 Ultra", "Phones", 15, 129000.0, 5),
        ("OnePlus 12", "Phones", 25, 64000.0, 10),
        ("Google Pixel 8 Pro", "Phones", 10, 105000.0, 3),
        # Monitors & Peripherals
        ("LG 27\" 4K Monitor", "Peripherals", 12, 35000.0, 5),
        ("Samsung Odyssey G7", "Peripherals", 5, 55000.0, 2),
        ("Logitech MX Master 3S", "Accessories", 30, 9500.0, 10),
        ("Keychron Q1 Keyboard", "Accessories", 15, 14000.0, 5),
        ("Sony WH-1000XM5", "Audio", 18, 29000.0, 5),
        ("AirPods Pro 2", "Audio", 40, 24000.0, 10),
        # Components
        ("NVIDIA RTX 4080", "Components", 4, 115000.0, 2),
        ("AMD Ryzen 9 7950X", "Components", 10, 58000.0, 3),
        ("Corsair 32GB RAM Kit", "Components", 25, 12000.0, 10),
        ("Samsung 990 Pro 2TB", "Components", 30, 18000.0, 8),
        # Networking
        ("TP-Link Archer AX6000", "Networking", 12, 22000.0, 5),
        ("Netgear Orbi Mesh System", "Networking", 5, 45000.0, 2)
    ]
    
    inventory_items = []
    for p in products_data:
        item = Inventory(
            product_name=p[0], category=p[1], quantity=p[2], 
            unit_price=p[3], reorder_level=p[4]
        )
        db.add(item)
        inventory_items.append(item)
    db.commit()

    # 3. Transactions (1 Year History)
    print("Generating 1 Year Transaction History...")
    db.query(Transaction).delete()
    
    start_date = datetime.now() - timedelta(days=365)
    transactions = []
    
    # Monthly Fixed Expenses
    for i in range(12):
        month_date = start_date + timedelta(days=30 * i)
        date_str = month_date.strftime("%Y-%m-%d")
        
        # Rent
        transactions.append(Transaction(date=date_str, type="expense", category="Rent", description="Office & Warehouse Rent", amount=85000.0))
        # Salaries
        transactions.append(Transaction(date=date_str, type="expense", category="Salaries", description="Staff Salaries - 5 employees", amount=245000.0))
        # Utilities
        transactions.append(Transaction(date=date_str, type="expense", category="Utilities", description="Electricity & Water", amount=12000.0))
        # Marketing
        transactions.append(Transaction(date=date_str, type="expense", category="Marketing", description="Google/FB Ad Spend", amount=35000.0))

    # Daily Variable Transactions (Sales & Purchase)
    for d in range(365):
        current_day = start_date + timedelta(days=d)
        date_str = current_day.strftime("%Y-%m-%d")
        
        # Random Sales (Income)
        if random.random() > 0.2: # 80% chance of a sale day
            num_sales = random.randint(1, 4)
            for _ in range(num_sales):
                amount = round(random.uniform(5000, 150000), 2)
                transactions.append(Transaction(
                    date=date_str, type="income", category="Sales Revenue", 
                    description=f"Direct Customer Sale - TRX-{random.randint(1000,9999)}", 
                    amount=amount
                ))
        
        # Random Inventory Purchase (Expense)
        if random.random() > 0.9: # 10% chance of restock expense
            amount = round(random.uniform(50000, 500000), 2)
            transactions.append(Transaction(
                date=date_str, type="expense", category="Inventory Purchase", 
                description=f"Wholesale Restock - Invoice #{random.randint(500,5000)}", 
                amount=amount
            ))

    db.add_all(transactions)
    db.commit()

    # 4. Sales Records (Connected to Inventory)
    print("Generating Detailed Sales History...")
    db.query(Sale).delete()
    sales = []
    for _ in range(250): # 250 individual sale entries
        item = random.choice(inventory_items)
        qty_sold = random.randint(1, 2)
        sale_date = (start_date + timedelta(days=random.randint(0, 364))).strftime("%Y-%m-%d")
        s = Sale(
            product_id=item.id,
            product_name=item.product_name,
            quantity_sold=qty_sold,
            sale_price=item.unit_price * 1.15, # 15% Markup
            sale_date=sale_date
        )
        sales.append(s)
    db.add_all(sales)
    db.commit()

    print("Seeding Helpdesk Tickets...")
    db.query(Ticket).delete()
    tickets_data = [
        ("XPS 13 Battery Issue", "Customer reporting battery drain on new laptop.", "high", "open"),
        ("Monitor Pixel Defect", "Return request for LG Monitor (Dead pixels).", "medium", "in-progress"),
        ("Bulk Order Inquiry", "Corporate client asking for quote on 20 Keychrons.", "low", "resolved"),
        ("OnePlus 12 Delivery Delayed", "Customer angry about shipment delay.", "high", "open"),
        ("Technical Support: Mesh Setup", "Client needs help setting up Netgear Orbi.", "medium", "resolved")
    ]
    for t in tickets_data:
        db.add(Ticket(title=t[0], description=t[1], priority=t[2], status=t[3]))
    db.commit()

    db.close()
    print("Database successfully reset with 1 Year of Electronic Company Data!")

if __name__ == "__main__":
    seed_electronics_company()
