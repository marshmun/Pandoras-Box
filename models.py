"""
SQLAlchemy database models for multi-user, multi-business inventory app
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User account model"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    businesses = db.relationship('BusinessAccount', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class BusinessAccount(db.Model):
    """Business account model - each user can have multiple businesses"""
    __tablename__ = 'business_accounts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    business_name = db.Column(db.String(200), nullable=False)
    business_type = db.Column(db.String(50), nullable=False)  # 'snack_bar', 'service', 'retail', etc.
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('InventoryItem', backref='business', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='business', lazy=True, cascade='all, delete-orphan')
    income = db.relationship('IncomeEntry', backref='business', lazy=True, cascade='all, delete-orphan')
    shrinkage = db.relationship('Shrinkage', backref='business', lazy=True, cascade='all, delete-orphan')
    mileage = db.relationship('MileageLog', backref='business', lazy=True, cascade='all, delete-orphan')
    time_entries = db.relationship('TimeEntry', backref='business', lazy=True, cascade='all, delete-orphan')


class InventoryItem(db.Model):
    """Inventory item model"""
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = db.Column(db.String(36), db.ForeignKey('business_accounts.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(100))
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=0)
    unit_cost = db.Column(db.Float, default=0)
    selling_price = db.Column(db.Float, default=0)
    on_display = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='item', lazy=True, cascade='all, delete-orphan')
    shrinkage = db.relationship('Shrinkage', backref='item', lazy=True, cascade='all, delete-orphan')


class Transaction(db.Model):
    """Inventory transaction (add/remove stock)"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = db.Column(db.String(36), db.ForeignKey('inventory_items.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # 'stock_in', 'stock_out', 'adjustment'
    quantity = db.Column(db.Integer)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Shrinkage(db.Model):
    """Shrinkage/loss tracking"""
    __tablename__ = 'shrinkage'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = db.Column(db.String(36), db.ForeignKey('business_accounts.id'), nullable=False)
    item_id = db.Column(db.String(36), db.ForeignKey('inventory_items.id'), nullable=False)
    quantity = db.Column(db.Integer)
    reason = db.Column(db.String(200))  # 'damage', 'theft', 'expiration', etc.
    value = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Expense(db.Model):
    """Business expenses"""
    __tablename__ = 'expenses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = db.Column(db.String(36), db.ForeignKey('business_accounts.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))
    amount = db.Column(db.Float, nullable=False)
    item_id = db.Column(db.String(36), db.ForeignKey('inventory_items.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class IncomeEntry(db.Model):
    """Income/revenue tracking - for snack bars, retail, etc."""
    __tablename__ = 'income_entries'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = db.Column(db.String(36), db.ForeignKey('business_accounts.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))  # 'sales', 'service', 'other'
    amount = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer)  # Units sold
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MileageLog(db.Model):
    """Mileage tracking for service-based businesses"""
    __tablename__ = 'mileage_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = db.Column(db.String(36), db.ForeignKey('business_accounts.id'), nullable=False)
    employee_name = db.Column(db.String(100))
    start_odometer = db.Column(db.Float)
    end_odometer = db.Column(db.Float)
    miles = db.Column(db.Float)
    purpose = db.Column(db.String(255))
    rate_per_mile = db.Column(db.Float, default=0.585)  # IRS rate, configurable
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TimeEntry(db.Model):
    """Time tracking for service-based businesses"""
    __tablename__ = 'time_entries'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = db.Column(db.String(36), db.ForeignKey('business_accounts.id'), nullable=False)
    employee_name = db.Column(db.String(100))
    task_description = db.Column(db.String(255))
    hours = db.Column(db.Float)
    hourly_rate = db.Column(db.Float)
    date_worked = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
