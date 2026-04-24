import random
import os
import sys
from datetime import datetime, timedelta
import bcrypt

# Ensure we can import from database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import SessionLocal, init_db
from database.models import User, Inventory, Transaction, Sale, Ticket

def generate_random_date(start_days_ago=90):
    now = datetime.now()
    random_days = random.randint(0, start_days_ago)
    random_date = now - timedelta(days=random_days)
    return random_date.strftime("%Y-%m-%d")

def generate_random_datetime(start_days_ago=90):
    now = datetime.now()
    random_days = random.randint(0, start_days_ago)
    random_date = now - timedelta(days=random_days)
    return random_date

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_database():
    db = SessionLocal()
    
    # Check if empty
    if db.query(User).count() > 0:
        print("Database already contains data. Skipping seed operation.")
        db.close()
        return

    print("Seeding Users...")
    users = [
        User(username="admin", password_hash=hash_password("admin123"), role="admin"),
        User(username="staff", password_hash=hash_password("staff123"), role="standard")
    ]
    db.add_all(users)
    db.commit()

    print("Seeding Inventory...")
    products_data = [
        ("Dell XPS 15", "Electronics", 25, 120000.0, 10),
        ("MacBook Pro", "Electronics", 5, 150000.0, 10),
        ("ThinkPad T14", "Electronics", 12, 95000.0, 10),
        ("Ergonomic Chair", "Furniture", 8, 15000.0, 5),
        ("Standing Desk", "Furniture", 3, 35000.0, 5),
        ("Office Desk", "Furniture", 10, 12000.0, 5),
        ("Printer Paper A4", "Office Supplies", 100, 500.0, 30),
        ("HP LaserJet Printer", "Electronics", 4, 25000.0, 5),
        ("Wireless Mouse", "Electronics", 45, 1500.0, 20),
        ("Mechanical Keyboard", "Electronics", 15, 4500.0, 10),
        ("Whiteboard", "Office Supplies", 12, 3000.0, 5),
        ("Markers Set", "Office Supplies", 50, 400.0, 15),
        ("Filing Cabinet", "Furniture", 7, 8500.0, 3),
        ("Coffee Machine", "Electronics", 2, 45000.0, 2),
        ("Desk Lamp", "Furniture", 20, 1200.0, 10)
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

    print("Seeding Transactions...")
    categories = ["Sales Revenue", "Rent", "Salaries", "Utilities", "Marketing", "Software Subs"]
    transactions = []
    for i in range(30):
        t_type = "income" if random.random() > 0.6 else "expense"
        category = "Sales Revenue" if t_type == "income" else random.choice(categories[1:])
        amount = round(random.uniform(500, 50000), 2)
        if category in ["Salaries", "Rent"]:
             amount = round(random.uniform(30000, 80000), 2)
        t = Transaction(
            date=generate_random_date(90),
            type=t_type,
            category=category,
            description=f"Record for {category} #{i+1}",
            amount=amount,
            status="completed"
        )
        transactions.append(t)
    db.add_all(transactions)
    db.commit()

    print("Seeding Sales...")
    sales = []
    for _ in range(50):
        item = random.choice(inventory_items)
        qty_sold = random.randint(1, 5)
        s = Sale(
            product_id=item.id,
            product_name=item.product_name,
            quantity_sold=qty_sold,
            sale_price=item.unit_price,
            sale_date=generate_random_date(90)
        )
        sales.append(s)
    db.add_all(sales)
    db.commit()

    print("Seeding Tickets...")
    tickets_data = [
        ("Printer Jam on 3rd Floor", "The HP LaserJet printer won't print.", "high", "open", None, None),
        ("Login issues with Accounting Portal", "User cannot reset password.", "medium", "in-progress", None, None),
        ("Need a new keyboard", "My key is sticking.", "low", "resolved", generate_random_datetime(2), "Please place an order."),
        ("Wi-Fi drops frequently", "Guest Wi-Fi network drops connection.", "high", "open", None, None),
        ("Aircon too cold", "Meeting room A is freezing.", "low", "resolved", generate_random_datetime(28), "Thermostat adjusted.")
    ]
    
    tickets = []
    for idx, t in enumerate(tickets_data):
        created = generate_random_datetime(30)
        tkt = Ticket(
            title=t[0],
            description=t[1],
            priority=t[2],
            status=t[3],
            created_at=created,
            resolved_at=t[4],
            ai_response=t[5]
        )
        tickets.append(tkt)
    db.add_all(tickets)
    db.commit()

    db.close()
    print("Database seeded successfully with ORM models.")

if __name__ == "__main__":
    
    # We must drop the existing raw SQLite tables because schema mismatch occurs if autoincrement etc. are different
    # Or simply deleting bizmind.db is safer
    db_path = os.path.join(os.path.dirname(__file__), "bizmind.db")
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("Deleted old bizmind.db to recreate via ORM.")
        except Exception as e:
            print(f"Could not delete old db: {e}")
            
    print("Initializing Database tables via SQLAlchemy...")
    init_db()
    seed_database()
