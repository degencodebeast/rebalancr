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
        
        # Add portfolio events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER,
                event_type TEXT,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_portfolio_events_portfolio_id 
            ON portfolio_events(portfolio_id)
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

    async def get_portfolios_with_settings(self):
        """Get all portfolios with rebalancing settings and user external IDs"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    p.*,
                    u.external_id as user_external_id,
                    COUNT(a.id) as asset_count,
                    SUM(a.amount) as total_assets
                FROM portfolios p
                JOIN users u ON p.user_id = u.id
                LEFT JOIN assets a ON p.id = a.portfolio_id
                GROUP BY p.id
            """)
            
            portfolios = [dict(row) for row in cursor.fetchall()]
            return portfolios
        except Exception as e:
            logger.error(f"Error getting portfolios with settings: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()

    async def update_portfolio(self, portfolio_id, update_data):
        """Update portfolio settings including auto-rebalance options"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build the SET clause dynamically based on provided fields
            set_clauses = []
            params = []
            
            for key, value in update_data.items():
                set_clauses.append(f"{key} = ?")
                params.append(value)
            
            # No fields to update
            if not set_clauses:
                return False
            
            params.append(portfolio_id)  # For the WHERE clause
            
            query = f"UPDATE portfolios SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            
            # Check if any rows were affected
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating portfolio {portfolio_id}: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()

    async def log_portfolio_event(self, portfolio_id, event_type, details=None):
        """
        Log a portfolio event in the database
        
        Args:
            portfolio_id: ID of the portfolio
            event_type: Type of event (rebalance_recommendation, auto_rebalance, etc.)
            details: Dictionary with event details
        
        Returns:
            ID of the created event record
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert details to JSON string if it's a dictionary
            details_json = None
            if details:
                import json
                details_json = json.dumps(details)
            
            # Insert the event
            cursor.execute(
                """
                INSERT INTO portfolio_events 
                (portfolio_id, event_type, details, timestamp) 
                VALUES (?, ?, ?, ?)
                """,
                (
                    portfolio_id,
                    event_type,
                    details_json,
                    datetime.now().isoformat()
                )
            )
            
            # Get the ID of the inserted event
            event_id = cursor.lastrowid
            
            conn.commit()
            return event_id
        except Exception as e:
            logger.error(f"Error logging portfolio event: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()

    async def get_user_portfolios(self, user_id):
        """
        Get all portfolios for a specific user
        
        Args:
            user_id: External or internal user ID
        
        Returns:
            List of portfolio dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check if user_id is numeric (internal ID) or string (external ID)
            internal_user_id = None
            try:
                internal_user_id = int(user_id)
            except (ValueError, TypeError):
                # If conversion fails, treat as external ID
                user = self.get_user_by_external_id(user_id)
                if not user:
                    return []
                internal_user_id = user["id"]
            
            # Get portfolios
            cursor.execute(
                """
                SELECT 
                    p.*,
                    COUNT(a.id) as asset_count,
                    SUM(a.amount) as total_assets
                FROM portfolios p
                LEFT JOIN assets a ON p.id = a.portfolio_id
                WHERE p.user_id = ?
                GROUP BY p.id
                """,
                (internal_user_id,)
            )
            
            # Convert to list of dictionaries
            portfolios = [dict(row) for row in cursor.fetchall()]
            return portfolios
        except Exception as e:
            logger.error(f"Error getting user portfolios: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()

    async def get_portfolio(self, portfolio_id):
        """
        Get a specific portfolio by ID with all its details
        
        Args:
            portfolio_id: Portfolio ID
        
        Returns:
            Portfolio dictionary or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get portfolio with asset statistics
            cursor.execute(
                """
                SELECT 
                    p.*,
                    u.external_id as user_external_id,
                    COUNT(a.id) as asset_count,
                    SUM(a.amount) as total_assets
                FROM portfolios p
                JOIN users u ON p.user_id = u.id
                LEFT JOIN assets a ON p.id = a.portfolio_id
                WHERE p.id = ?
                GROUP BY p.id
                """,
                (portfolio_id,)
            )
            
            portfolio = cursor.fetchone()
            
            if not portfolio:
                return None
            
            portfolio_dict = dict(portfolio)
            
            # Get assets for this portfolio
            cursor.execute(
                """
                SELECT * FROM assets
                WHERE portfolio_id = ?
                """,
                (portfolio_id,)
            )
            
            assets = [dict(row) for row in cursor.fetchall()]
            portfolio_dict["assets"] = assets
            
            return portfolio_dict
        except Exception as e:
            logger.error(f"Error getting portfolio: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()

    async def create_conversation(self, user_id):
        """
        Create a new conversation for a user
        
        Args:
            user_id: External user ID
        
        Returns:
            Conversation ID
        """
        try:
            # Generate a unique conversation ID
            import time
            import uuid
            conversation_id = f"conv_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            # Get internal user ID if needed
            internal_user_id = None
            try:
                internal_user_id = int(user_id)
            except (ValueError, TypeError):
                # If conversion fails, treat as external ID
                user = self.get_user_by_external_id(user_id)
                if user:
                    internal_user_id = user["id"]
                else:
                    # If no matching user, create a placeholder record
                    internal_user_id = self.create_user(user_id)
                
            if not internal_user_id:
                logger.error(f"Could not resolve internal ID for user {user_id}")
                return None
            
            # Since conversations are implicit in our schema,
            # we just need to return the generated ID
            # The first message using this ID will effectively create the conversation
            
            return conversation_id
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            return None

    async def get_portfolio_events(self, portfolio_id, event_type=None, limit=50):
        """
        Get events for a specific portfolio
        
        Args:
            portfolio_id: ID of the portfolio
            event_type: Optional type of events to filter (e.g., 'rebalance_recommendation')
            limit: Maximum number of events to return
        
        Returns:
            List of event dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build query based on whether event_type is provided
            if event_type:
                cursor.execute(
                    """
                    SELECT * FROM portfolio_events
                    WHERE portfolio_id = ? AND event_type = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (portfolio_id, event_type, limit)
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM portfolio_events
                    WHERE portfolio_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (portfolio_id, limit)
                )
            
            events = []
            for row in cursor.fetchall():
                event = dict(row)
                
                # Parse JSON details if present
                if event.get('details'):
                    import json
                    try:
                        event['details'] = json.loads(event['details'])
                    except:
                        pass  # Keep as string if parsing fails
                        
                events.append(event)
                
            return events
        except Exception as e:
            logger.error(f"Error getting portfolio events: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()
