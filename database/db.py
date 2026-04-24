import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_FILENAME = "bizmind.db"

# Create the SQLite engine
db_path = os.path.join(os.path.dirname(__file__), DB_FILENAME)
engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from database.models import Base
    # Create tables
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Initializing SQLAlchemy Database...")
    init_db()
    print("Database schema initialized successfully.")
