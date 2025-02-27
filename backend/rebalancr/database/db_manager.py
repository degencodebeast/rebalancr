import sqlite3
from datetime import datetime
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path=None):
        # Use the standard path by default
        if db_path is None:
            data_dir = Path(__file__).parent.parent.parent / "data"
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = data_dir / "rebalancr.db"
        else:
            self.db_path = db_path
            
        logger.info(f"Initializing database at {self.db_path}")
        self._create_tables()
    
    def _create_tables(self):
        """Create all necessary tables if they don't exist"""
        logger.info("Creating database tables...")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                external_id TEXT UNIQUE,
                username TEXT,
                wallet_address TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Agent wallets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                wallet_address TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Agent settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                settings_json TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
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
        
        # Chat history table (with modern schema from the beginning)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                user_id INTEGER,
                message TEXT,
                message_type TEXT,  -- "user", "agent", "tool", "system" 
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Create indices for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_conversation_id 
            ON chat_history(conversation_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_user_id 
            ON chat_history(user_id)
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database initialization complete")
    
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

    async def insert_chat_message(self, message_data):
        """
        Insert a chat message into the database
        
        Args:
            message_data: Dictionary with message details
                - user_id: User identifier
                - message: Message content
                - message_type: Type of message (user, agent, tool, system)
                - conversation_id: Optional conversation ID
        
        Returns:
            Dictionary with inserted message details including ID
        """
        # Generate conversation_id if not provided
        if not message_data.get("conversation_id"):
            # Use a simple timestamp-based ID if uuid not available
            import time
            message_data["conversation_id"] = f"conv_{int(time.time())}_{message_data['user_id']}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert message
            cursor.execute(
                """
                INSERT INTO chat_history 
                (conversation_id, user_id, message, message_type, timestamp) 
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    message_data["conversation_id"],
                    message_data["user_id"],
                    message_data["message"],
                    message_data["message_type"],
                    message_data.get("timestamp", datetime.now().isoformat())
                )
            )
            
            # Get the ID of the inserted message
            message_id = cursor.lastrowid
            
            conn.commit()
            
            # Return message data with ID
            return {
                "id": message_id,
                **message_data
            }
        except Exception as e:
            conn.rollback()
            print(f"Error inserting chat message: {str(e)}")
            raise
        finally:
            conn.close()

    async def get_chat_messages(self, conversation_id, limit=50):
        """
        Get messages for a specific conversation
        
        Args:
            conversation_id: Conversation identifier
            limit: Maximum number of messages to return
        
        Returns:
            List of message dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables dictionary-like access to rows
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT * FROM chat_history 
                WHERE conversation_id = ? 
                ORDER BY timestamp ASC 
                LIMIT ?
                """, 
                (conversation_id, limit)
            )
            
            # Convert to list of dictionaries
            messages = [dict(row) for row in cursor.fetchall()]
            return messages
        except Exception as e:
            print(f"Error getting chat messages: {str(e)}")
            return []
        finally:
            conn.close()

    async def get_user_conversations(self, user_id, limit=10):
        """
        Get list of conversations for a user
        
        Args:
            user_id: User identifier
            limit: Maximum number of conversations to return
        
        Returns:
            List of conversation dictionaries with latest message
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Get distinct conversation IDs with their latest message
            cursor.execute(
                """
                SELECT 
                    conversation_id,
                    MAX(timestamp) as last_message_time,
                    COUNT(*) as message_count
                FROM chat_history
                WHERE user_id = ? AND conversation_id IS NOT NULL
                GROUP BY conversation_id
                ORDER BY last_message_time DESC
                LIMIT ?
                """,
                (user_id, limit)
            )
            
            conversations = []
            for row in cursor.fetchall():
                conv_id = row['conversation_id']
                
                # Get the latest message for this conversation
                cursor.execute(
                    """
                    SELECT * FROM chat_history
                    WHERE conversation_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                    """,
                    (conv_id,)
                )
                
                last_message = cursor.fetchone()
                
                if last_message:
                    conversations.append({
                        'conversation_id': conv_id,
                        'last_message': last_message['message'],
                        'last_message_type': last_message['message_type'],
                        'last_message_time': last_message['timestamp'],
                        'message_count': row['message_count']
                    })
                    
            return conversations
        except Exception as e:
            print(f"Error getting user conversations: {str(e)}")
            return []
        finally:
            conn.close()

    async def get_active_portfolios(self):
        """
        Get all active portfolios from the database
        
        Returns:
            List of portfolio dictionaries with user_id and portfolio details
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT 
                    p.id,
                    p.user_id,
                    p.name,
                    p.created_at,
                    COUNT(a.id) as asset_count,
                    SUM(a.amount) as total_assets
                FROM portfolios p
                LEFT JOIN assets a ON p.id = a.portfolio_id
                GROUP BY p.id
                """
            )
            
            # Convert to list of dictionaries
            portfolios = [dict(row) for row in cursor.fetchall()]
            return portfolios
        except Exception as e:
            print(f"Error getting active portfolios: {str(e)}")
            return []
        finally:
            conn.close()
