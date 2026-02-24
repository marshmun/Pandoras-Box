import sqlite3
import os
from datetime import datetime
from pathlib import Path

class InventoryDatabase:
    def __init__(self, db_path="inventory.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sku TEXT UNIQUE,
                category TEXT,
                quantity INTEGER DEFAULT 0,
                unit_cost REAL,
                selling_price REAL,
                on_display INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Transactions table (for inventory movements)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                transaction_type TEXT,
                quantity INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        ''')
        
        # Shrinkage table (for tracking losses)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shrinkage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                quantity INTEGER,
                reason TEXT,
                value REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        ''')
        
        # Expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                category TEXT,
                amount REAL NOT NULL,
                item_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Item operations
    def add_item(self, name, sku=None, category=None, unit_cost=0, selling_price=0):
        """Add a new item to inventory"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO items (name, sku, category, unit_cost, selling_price)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, sku, category, unit_cost, selling_price))
        conn.commit()
        item_id = cursor.lastrowid
        conn.close()
        return item_id
    
    def get_all_items(self):
        """Get all items"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM items ORDER BY name')
        items = cursor.fetchall()
        conn.close()
        return items
    
    def update_quantity(self, item_id, quantity_change, transaction_type="adjustment"):
        """Update item quantity and log transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Update quantity
        cursor.execute('''
            UPDATE items SET quantity = quantity + ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (quantity_change, item_id))
        
        # Log transaction
        cursor.execute('''
            INSERT INTO transactions (item_id, transaction_type, quantity)
            VALUES (?, ?, ?)
        ''', (item_id, transaction_type, quantity_change))
        
        conn.commit()
        conn.close()
    
    def add_shrinkage(self, item_id, quantity, reason, value=0):
        """Record shrinkage/loss"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Log shrinkage
        cursor.execute('''
            INSERT INTO shrinkage (item_id, quantity, reason, value)
            VALUES (?, ?, ?, ?)
        ''', (item_id, quantity, reason, value))
        
        # Update quantity
        cursor.execute('''
            UPDATE items SET quantity = quantity - ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (quantity, item_id))
        
        conn.commit()
        conn.close()
    
    def get_item_by_id(self, item_id):
        """Get specific item"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,))
        item = cursor.fetchone()
        conn.close()
        return item
    
    # Expense operations
    def add_expense(self, description, amount, category=None, item_id=None):
        """Add an expense"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (description, category, amount, item_id)
            VALUES (?, ?, ?, ?)
        ''', (description, category, amount, item_id))
        conn.commit()
        expense_id = cursor.lastrowid
        conn.close()
        return expense_id
    
    def get_expenses(self, limit=None):
        """Get all expenses"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if limit:
            cursor.execute('SELECT * FROM expenses ORDER BY created_at DESC LIMIT ?', (limit,))
        else:
            cursor.execute('SELECT * FROM expenses ORDER BY created_at DESC')
        expenses = cursor.fetchall()
        conn.close()
        return expenses
    
    def get_shrinkage_report(self):
        """Get shrinkage report"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT i.name, SUM(s.quantity) as total_shrinkage, 
                   SUM(s.value) as total_value, s.reason
            FROM shrinkage s
            JOIN items i ON s.item_id = i.id
            GROUP BY s.item_id, s.reason
            ORDER BY total_value DESC
        ''')
        report = cursor.fetchall()
        conn.close()
        return report
