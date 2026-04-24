from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, constr, model_validator
from typing import Optional
from datetime import datetime

Base = declarative_base()

# --- SQLAlchemy Models ---

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default='standard') # 'admin' or 'standard'

class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String, nullable=False)
    category = Column(String)
    quantity = Column(Integer, default=0)
    unit_price = Column(Float)
    reorder_level = Column(Integer, default=10)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    sales = relationship("Sale", back_populates="product", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String)
    type = Column(String) # 'income' or 'expense'
    category = Column(String)
    description = Column(String)
    amount = Column(Float)
    status = Column(String, default='completed')

class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    description = Column(String)
    priority = Column(String) # 'low', 'medium', 'high'
    status = Column(String, default='open')
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)
    ai_response = Column(String, nullable=True)

class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('inventory.id'))
    product_name = Column(String)
    quantity_sold = Column(Integer)
    sale_price = Column(Float)
    sale_date = Column(String)
    
    product = relationship("Inventory", back_populates="sales")

# --- Pydantic Validation Schemas ---

class InventoryCreate(BaseModel):
    product_name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    quantity: int = Field(ge=0)
    unit_price: float = Field(ge=0.0)
    reorder_level: int = Field(ge=0)

class TransactionCreate(BaseModel):
    date: str
    type: str
    category: str = Field(min_length=1)
    description: str
    amount: float = Field(gt=0.0)
    
    @model_validator(mode='after')
    def validate_type(self):
        if self.type.lower() not in ['income', 'expense']:
            raise ValueError("Type must be either income or expense.")
        return self

class TicketCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    priority: str
    
    @model_validator(mode='after')
    def validate_priority(self):
        if self.priority.lower() not in ['low', 'medium', 'high']:
            raise ValueError("Priority must be low, medium, or high.")
        return self
