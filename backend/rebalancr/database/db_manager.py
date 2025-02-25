import sqlite3
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path='rebalancr.db'):
        self.db_path = db_path
        print(f"Initializing database at {self.db_path}")
        self._create_tables()
    
    def _create_tables(self):
        """Create all necessary tables if they don't exist"""
        print("Creating tables...")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                external_id TEXT UNIQUE,
                username TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Portfolios table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Assets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER,
                token_address TEXT,
                symbol TEXT,
                amount REAL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
            )
        """)
        
        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER,
                transaction_hash TEXT,
                transaction_type TEXT,
                token_address TEXT,
                amount REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
            )
        """)
        
        # Chat history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT,
                is_bot BOOLEAN,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    
    # User methods
    def create_user(self, external_id, username=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (external_id, username) VALUES (?, ?)",
                (external_id, username)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return None
        finally:
            conn.close()
    
    def get_user_by_external_id(self, external_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE external_id = ?", (external_id,))
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None
