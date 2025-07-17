#!/usr/bin/env python3
"""
Enhanced database management with connection pooling and performance optimizations.
"""

import logging
import time
import sqlite3
from contextlib import contextmanager
from typing import Optional, Any, Dict, List, Generator, Union
import os

# Try to import psycopg2, fall back to sqlite3 if not available
try:
    import psycopg2
    from psycopg2 import pool, extras
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
    # Type aliases for when psycopg2 is available
    PostgresConnection = psycopg2.extensions.connection
    PostgresPool = psycopg2.pool.AbstractConnectionPool
except ImportError:
    print("psycopg2 not available, using sqlite3 fallback")
    HAS_POSTGRES = False
    psycopg2 = None
    # Fallback type aliases
    PostgresConnection = Any
    PostgresPool = Any

try:
    from src.config import settings
except ImportError:
    # Fallback settings for standalone operation
    class FallbackSettings:
        DATABASE_URL: Optional[str] = None
        class Database:
            MIN_CONNECTIONS: int = 1
            MAX_CONNECTIONS: int = 20
            RETRY_DELAY: float = 1.0
    settings = FallbackSettings()

try:
    from src.schema import get_schema_queries, get_default_settings
except ImportError:
    # Fallback schema functions
    def get_schema_queries() -> List[str]:
        """Fallback function when schema module is not available."""
        return []

    def get_default_settings() -> List[tuple]:
        """Fallback function when schema module is not available."""
        return []

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Enhanced database manager with connection pooling."""

    _instance: Optional['DatabaseManager'] = None
    _pool: Optional[Union[PostgresPool, None]] = None
    _db_type: str = 'unknown'
    _sqlite_path: str = 'telegram_bot.db'

    def __new__(cls) -> 'DatabaseManager':
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the database manager."""
        logger.info("Initializing PostgreSQL connection pool")
        
        # Check if database initialization should be deferred
        if os.getenv('DEFER_DB_INIT', '').lower() == 'true':
            logger.info("Database initialization deferred due to DEFER_DB_INIT flag")
            self._pool = None
            self._connection_params = None
            return
        
        try:
            self._initialize_pool()
            self.ensure_schema()
            logger.info("Database pool initialized successfully (postgresql)")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            # Don't raise exception during import to allow bot to start with limited functionality
            self._pool = None
            self._connection_params = None
            if not os.getenv('DEFER_DB_INIT'):
                logger.warning("Database unavailable - bot will run with limited functionality")

    def initialize_if_deferred(self):
        """Initialize database if it was deferred during import."""
        if self._pool is None and os.getenv('DEFER_DB_INIT', '').lower() == 'true':
            # Remove defer flag and try to initialize
            if 'DEFER_DB_INIT' in os.environ:
                del os.environ['DEFER_DB_INIT']
            try:
                logger.info("Initializing deferred database connection")
                self._initialize_pool()
                self.ensure_schema()
                logger.info("Database pool initialized successfully (deferred)")
                return True
            except Exception as e:
                logger.error(f"Deferred database initialization failed: {e}")
                return False
        return self._pool is not None

    def _initialize_pool(self) -> None:
        """Initialize database connection pool."""
        try:
            if HAS_POSTGRES and settings.DATABASE_URL:
                logger.info("Initializing PostgreSQL connection pool")
                self._pool = psycopg2.pool.ThreadedConnectionPool(
                    minconn=1, # Simplified, can use a constant
                    maxconn=10, # Simplified, can use a constant
                    dsn=settings.DATABASE_URL,
                    cursor_factory=RealDictCursor
                )
                self._db_type = 'postgresql'
            else:
                logger.info("Initializing SQLite fallback database")
                self._sqlite_path = 'telegram_bot.db'
                self._db_type = 'sqlite'
                # Create SQLite database if it doesn't exist
                conn = sqlite3.connect(self._sqlite_path)
                conn.close()

            logger.info(f"Database pool initialized successfully ({self._db_type})")

            # Ensure schema is created
            self.ensure_schema()

        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise

    def ensure_schema(self) -> None:
        """Ensure database schema exists."""
        try:
            schema_queries = get_schema_queries()

            with self.get_connection() as conn:
                if self._db_type == 'postgresql':
                    with conn.cursor() as cursor:
                        for query in schema_queries:
                            cursor.execute(query)
                        conn.commit()
                else:  # SQLite
                    cursor = conn.cursor()
                    for query in schema_queries:
                        # Convert PostgreSQL queries to SQLite if needed
                        sqlite_query = self._convert_to_sqlite(query)
                        cursor.execute(sqlite_query)
                    conn.commit()

            logger.info("Database schema ensured")
            
            # Initialize default data after schema creation
            try:
                from src.schema import ensure_default_data
                ensure_default_data()
            except Exception as e:
                logger.warning(f"Failed to initialize default data: {e}")

        except Exception as e:
            logger.error(f"Failed to ensure schema: {e}")
            # Don't raise - allow the app to continue without schema

    def _convert_to_sqlite(self, query: str) -> str:
        """Convert PostgreSQL query to SQLite compatible format."""
        # Basic conversions for common PostgreSQL to SQLite differences
        query = query.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
        query = query.replace('BOOLEAN', 'INTEGER')
        query = query.replace('TIMESTAMP', 'TEXT')
        
        # Correctly handle ON CONFLICT for INSERT statements
        if 'ON CONFLICT DO NOTHING' in query:
            query = query.replace('INSERT INTO', 'INSERT OR IGNORE INTO')
            query = query.replace('ON CONFLICT DO NOTHING', '')
            
        return query

    @contextmanager
    def get_connection(self) -> Generator[Union[PostgresConnection, sqlite3.Connection], None, None]:
        """Get database connection from pool."""
        if self._db_type == 'disabled':
            # Return a mock connection object for disabled state
            logger.warning("Database is disabled - returning mock connection")
            yield None
            return
            
        if self._db_type == 'postgresql' and self._pool:
            conn = None
            try:
                conn = self._pool.getconn()
                yield conn
            except Exception as e:
                if conn:
                    conn.rollback()
                logger.error(f"Database connection error: {e}")
                raise
            finally:
                if conn:
                    self._pool.putconn(conn)
        else:  # SQLite
            conn = None
            try:
                conn = sqlite3.connect(self._sqlite_path)
                conn.row_factory = sqlite3.Row  # Enable dict-like access
                yield conn
            except Exception as e:
                if conn:
                    conn.rollback()
                logger.error(f"SQLite connection error: {e}")
                raise
            finally:
                if conn:
                    conn.close()

    def execute_query(self, query: str, params: Optional[tuple] = None,
                     fetch_one: bool = False, fetch_all: bool = False) -> Any:
        """Execute database query with retry logic."""
        for attempt in range(3): # Max retries
            try:
                with self.get_connection() as conn:
                    if self._db_type == 'postgresql':
                        with conn.cursor() as cursor:
                            cursor.execute(query, params)

                            if fetch_one:
                                return cursor.fetchone()
                            elif fetch_all:
                                return cursor.fetchall()
                            else:
                                conn.commit()
                                return cursor.rowcount
                    else:  # SQLite
                        cursor = conn.cursor()
                        cursor.execute(query, params or ())

                        if fetch_one:
                            return cursor.fetchone()
                        elif fetch_all:
                            return cursor.fetchall()
                        else:
                            conn.commit()
                            return cursor.rowcount

            except Exception as e:
                logger.error(f"Query execution failed (attempt {attempt + 1}): {e}")
                if attempt < 2: # Max retries - 1
                    time.sleep(1.0) # Retry delay
                else:
                    raise

    def execute_transaction(self, operations: List[Dict[str, Any]]) -> bool:
        """Execute multiple operations in a transaction."""
        try:
            with self.get_connection() as conn:
                if self._db_type == 'postgresql':
                    with conn.cursor() as cursor:
                        for op in operations:
                            cursor.execute(op['query'], op.get('params'))
                        conn.commit()
                else:  # SQLite
                    cursor = conn.cursor()
                    for op in operations:
                        cursor.execute(op['query'], op.get('params', ()))
                    conn.commit()

            return True
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            return False

    def close_pool(self) -> None:
        """Close database connection pool."""
        if self._pool and self._db_type == 'postgresql':
            self._pool.closeall()
            logger.info("Database pool closed")


# Global database manager instance
db_manager = DatabaseManager()


def get_db_connection() -> Generator[Union[PostgresConnection, sqlite3.Connection], None, None]:
    """Get database connection (legacy function for compatibility)."""
    return db_manager.get_connection()


@contextmanager
def get_db_cursor() -> Generator[Any, None, None]:
    """Get database cursor with automatic connection management."""
    try:
        with db_manager.get_connection() as conn:
            if db_manager._db_type == 'postgresql':
                with conn.cursor() as cursor:
                    yield cursor
            else:  # SQLite
                cursor = conn.cursor()
                try:
                    yield cursor
                finally:
                    cursor.close()
    except Exception as e:
        logger.error(f"Database cursor error: {e}")
        raise


def get_user_credits_optimized(user_id: int) -> int:
    """Get user credits with caching optimization."""
    try:
        query = """
        SELECT message_credits, time_credits
        FROM users
        WHERE user_id = %s
        """ if db_manager._db_type == 'postgresql' else """
        SELECT message_credits, time_credits
        FROM users
        WHERE user_id = ?
        """

        result = db_manager.execute_query(
            query,
            (user_id,),
            fetch_one=True
        )

        if result:
            return result['message_credits'] if db_manager._db_type == 'postgresql' else result[0]
        return 0

    except Exception as e:
        logger.error(f"Error getting user credits: {e}")
        return 0


def decrement_user_credits_optimized(user_id: int, cost: int) -> int:
    """Decrement user credits optimally."""
    try:
        query = """
        UPDATE users
        SET message_credits = GREATEST(message_credits - %s, 0),
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = %s
        RETURNING message_credits
        """ if db_manager._db_type == 'postgresql' else """
        UPDATE users
        SET message_credits = MAX(message_credits - ?, 0),
            updated_at = datetime('now')
        WHERE user_id = ?
        """

        if db_manager._db_type == 'postgresql':
            result = db_manager.execute_query(query, (cost, user_id), fetch_one=True)
            return result['message_credits'] if result else 0
        else:
            db_manager.execute_query(query, (cost, user_id))
            # Get updated credits for SQLite
            return get_user_credits_optimized(user_id)

    except Exception as e:
        logger.error(f"Error decrementing credits: {e}")
        return 0


def batch_update_user_credits(updates: List[Dict[str, Union[int, str]]]) -> bool:
    """Batch update user credits for improved performance."""
    try:
        operations = []
        for update in updates:
            query = """
            UPDATE users
            SET message_credits = message_credits + %s,
                time_credits = time_credits + %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            """ if db_manager._db_type == 'postgresql' else """
            UPDATE users
            SET message_credits = message_credits + ?,
                time_credits = time_credits + ?,
                updated_at = datetime('now')
            WHERE user_id = ?
            """

            operations.append({
                'query': query,
                'params': (
                    update.get('message_credits', 0),
                    update.get('time_credits', 0),
                    update['user_id']
                )
            })

        return db_manager.execute_transaction(operations)

    except Exception as e:
        logger.error(f"Batch update failed: {e}")
        return False


def check_database_health() -> Dict[str, Any]:
    """Check database health and performance."""
    try:
        start_time = time.time()

        # Simple health check query
        query = "SELECT 1 as health_check"
        result = db_manager.execute_query(query, fetch_one=True)

        response_time = time.time() - start_time

        return {
            'status': 'healthy' if result else 'unhealthy',
            'response_time_ms': round(response_time * 1000, 2),
            'database_type': db_manager._db_type,
            'timestamp': time.time()
        }

    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'database_type': getattr(db_manager, '_db_type', 'unknown'),
            'timestamp': time.time()
        }

def get_active_products() -> List[Dict[str, Any]]:
    """Get all active products from the database."""
    try:
        query = """
        SELECT *
        FROM products
        WHERE is_active = TRUE
        ORDER BY amount
        """
        return db_manager.execute_query(query, fetch_all=True)
    except Exception as e:
        logger.error(f"Error getting active products: {e}")
        return []

def get_stripe_customer_id(user_id: int) -> Optional[str]:
    """Get Stripe customer ID for a user."""
    try:
        query = "SELECT stripe_customer_id FROM users WHERE telegram_id = %s" if db_manager._db_type == 'postgresql' else "SELECT stripe_customer_id FROM users WHERE telegram_id = ?"
        result = db_manager.execute_query(query, (user_id,), fetch_one=True)
        return result['stripe_customer_id'] if result else None
    except Exception as e:
        logger.error(f"Error getting Stripe customer ID: {e}")
        return None

def set_stripe_customer_id(user_id: int, customer_id: str) -> None:
    """Set Stripe customer ID for a user."""
    try:
        query = "UPDATE users SET stripe_customer_id = %s WHERE telegram_id = %s" if db_manager._db_type == 'postgresql' else "UPDATE users SET stripe_customer_id = ? WHERE telegram_id = ?"
        db_manager.execute_query(query, (customer_id, user_id))
    except Exception as e:
        logger.error(f"Error setting Stripe customer ID: {e}")

def add_user_credits(user_id: int, amount: int, credit_type: str = 'message') -> None:
    """Add credits or time to a user's account."""
    try:
        if credit_type == 'time':
            query = "UPDATE users SET time_credits_seconds = time_credits_seconds + %s WHERE telegram_id = %s" if db_manager._db_type == 'postgresql' else "UPDATE users SET time_credits_seconds = time_credits_seconds + ? WHERE telegram_id = ?"
        else:
            query = "UPDATE users SET message_credits = message_credits + %s WHERE telegram_id = %s" if db_manager._db_type == 'postgresql' else "UPDATE users SET message_credits = message_credits + ? WHERE telegram_id = ?"
        
        db_manager.execute_query(query, (amount, user_id))
    except Exception as e:
        logger.error(f"Error adding user credits: {e}")

def get_setting(key: str, default: str = None) -> Optional[str]:
    """Get a specific setting from the database."""
    try:
        query = "SELECT setting_value FROM bot_settings WHERE setting_key = %s" if db_manager._db_type == 'postgresql' else "SELECT setting_value FROM bot_settings WHERE setting_key = ?"
        result = db_manager.execute_query(query, (key,), fetch_one=True)
        return result['setting_value'] if result else default
    except Exception as e:
        logger.error(f"Error getting setting '{key}': {e}")
        return default

def set_setting(key: str, value: str) -> None:
    """Create or update a specific setting in the database."""
    try:
        query = """
            INSERT INTO bot_settings (setting_key, setting_value) VALUES (%s, %s)
            ON CONFLICT (setting_key) DO UPDATE SET setting_value = EXCLUDED.setting_value
        """ if db_manager._db_type == 'postgresql' else """
            INSERT OR REPLACE INTO bot_settings (setting_key, setting_value) VALUES (?, ?)
        """
        db_manager.execute_query(query, (key, value))
    except Exception as e:
        logger.error(f"Error setting '{key}': {e}")

def get_user_stats() -> Dict[str, int]:
    """Get basic statistics about users."""
    try:
        query = "SELECT COUNT(*) as total, COUNT(CASE WHEN is_banned THEN 1 END) as banned FROM users"
        result = db_manager.execute_query(query, fetch_one=True)
        return {
            "total_users": result['total'] if result else 0,
            "banned_users": result['banned'] if result else 0,
        }
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        return {"total_users": 0, "banned_users": 0}

def is_user_banned(user_id: int) -> bool:
    """Check if a user is banned."""
    try:
        query = "SELECT is_banned FROM users WHERE telegram_id = %s" if db_manager._db_type == 'postgresql' else "SELECT is_banned FROM users WHERE telegram_id = ?"
        result = db_manager.execute_query(query, (user_id,), fetch_one=True)
        return result['is_banned'] if result and result['is_banned'] else False
    except Exception as e:
        logger.error(f"Error checking if user {user_id} is banned: {e}")
        return False

def create_locked_content(content_type: str, file_id: str, price: int, created_by: int, description: str = None, thumbnail_file_id: str = None) -> int:
    """Create a new piece of locked content."""
    try:
        query = """
            INSERT INTO locked_content (content_type, file_id, price, created_by, description, thumbnail_file_id)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """ if db_manager._db_type == 'postgresql' else """
            INSERT INTO locked_content (content_type, file_id, price, created_by, description, thumbnail_file_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        if db_manager._db_type == 'postgresql':
            result = db_manager.execute_query(query, (content_type, file_id, price, created_by, description, thumbnail_file_id), fetch_one=True)
            return result['id']
        else:
            # SQLite does not support RETURNING, so we get the last inserted rowid
            cursor = db_manager.execute_query(query, (content_type, file_id, price, created_by, description, thumbnail_file_id))
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error creating locked content: {e}")
        return 0

def get_all_users(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Get paginated list of all users."""
    try:
        query = """
        SELECT telegram_id, username, first_name, message_credits, is_banned, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """ if db_manager._db_type == 'postgresql' else """
        SELECT telegram_id, username, first_name, message_credits, is_banned, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        """
        return db_manager.execute_query(query, (limit, offset), fetch_all=True)
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return []

def ban_user(user_id: int, reason: str = "Admin action") -> bool:
    """Ban a user with optional reason."""
    try:
        query = """
        UPDATE users 
        SET is_banned = TRUE, ban_reason = %s, updated_at = CURRENT_TIMESTAMP
        WHERE telegram_id = %s
        """ if db_manager._db_type == 'postgresql' else """
        UPDATE users 
        SET is_banned = 1, ban_reason = ?, updated_at = datetime('now')
        WHERE telegram_id = ?
        """
        db_manager.execute_query(query, (reason, user_id))
        logger.info(f"User {user_id} banned: {reason}")
        return True
    except Exception as e:
        logger.error(f"Error banning user {user_id}: {e}")
        return False

def unban_user(user_id: int) -> bool:
    """Unban a user."""
    try:
        query = """
        UPDATE users 
        SET is_banned = FALSE, ban_reason = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE telegram_id = %s
        """ if db_manager._db_type == 'postgresql' else """
        UPDATE users 
        SET is_banned = 0, ban_reason = NULL, updated_at = datetime('now')
        WHERE telegram_id = ?
        """
        db_manager.execute_query(query, (user_id,))
        logger.info(f"User {user_id} unbanned")
        return True
    except Exception as e:
        logger.error(f"Error unbanning user {user_id}: {e}")
        return False

def update_setting(key: str, value: str) -> bool:
    """Update a bot setting."""
    try:
        query = """
        INSERT INTO bot_settings (setting_key, setting_value, updated_at)
        VALUES (%s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (setting_key) 
        DO UPDATE SET setting_value = EXCLUDED.setting_value, updated_at = CURRENT_TIMESTAMP
        """ if db_manager._db_type == 'postgresql' else """
        INSERT OR REPLACE INTO bot_settings (setting_key, setting_value, updated_at)
        VALUES (?, ?, datetime('now'))
        """
        db_manager.execute_query(query, (key, value))
        logger.info(f"Setting updated: {key} = {value}")
        return True
    except Exception as e:
        logger.error(f"Error updating setting {key}: {e}")
        return False

def get_user_by_customer_id(customer_id: str) -> Optional[int]:
    """Get user ID by Stripe customer ID."""
    try:
        query = """
        SELECT telegram_id FROM users WHERE stripe_customer_id = %s
        """ if db_manager._db_type == 'postgresql' else """
        SELECT telegram_id FROM users WHERE stripe_customer_id = ?
        """
        result = db_manager.execute_query(query, (customer_id,), fetch_one=True)
        return result['telegram_id'] if result else None
    except Exception as e:
        logger.error(f"Error getting user by customer ID {customer_id}: {e}")
        return None

def get_or_create_user_topic(user_id: int, username: str = None, first_name: str = None) -> Optional[int]:
    """Get existing topic ID for user or create a new one."""
    try:
        # First, check if user already has a topic
        query = """
        SELECT topic_id FROM conversations 
        WHERE user_id = %s AND topic_id IS NOT NULL 
        ORDER BY created_at DESC LIMIT 1
        """ if db_manager._db_type == 'postgresql' else """
        SELECT topic_id FROM conversations 
        WHERE user_id = ? AND topic_id IS NOT NULL 
        ORDER BY created_at DESC LIMIT 1
        """
        
        result = db_manager.execute_query(query, (user_id,), fetch_one=True)
        if result and result['topic_id']:
            return result['topic_id']
        
        # If no topic exists, return None - topic creation should be handled by the bot
        # when it actually creates the forum topic in Telegram
        return None
        
    except Exception as e:
        logger.error(f"Error getting/creating user topic for {user_id}: {e}")
        return None

def save_user_topic(user_id: int, topic_id: int) -> bool:
    """Save the topic ID for a user after topic creation."""
    try:
        query = """
        INSERT INTO conversations (user_id, topic_id, status, created_at, updated_at)
        VALUES (%s, %s, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id) DO UPDATE SET 
            topic_id = EXCLUDED.topic_id,
            updated_at = CURRENT_TIMESTAMP
        """ if db_manager._db_type == 'postgresql' else """
        INSERT OR REPLACE INTO conversations (user_id, topic_id, status, created_at, updated_at)
        VALUES (?, ?, 'active', datetime('now'), datetime('now'))
        """
        
        db_manager.execute_query(query, (user_id, topic_id))
        logger.info(f"Saved topic {topic_id} for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving user topic for {user_id}: {e}")
        return False

def update_conversation_activity(user_id: int, topic_id: int = None) -> bool:
    """Update the last message timestamp for a conversation."""
    try:
        if topic_id:
            query = """
            UPDATE conversations 
            SET last_message_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND topic_id = %s
            """ if db_manager._db_type == 'postgresql' else """
            UPDATE conversations 
            SET last_message_at = datetime('now'), updated_at = datetime('now')
            WHERE user_id = ? AND topic_id = ?
            """
            db_manager.execute_query(query, (user_id, topic_id))
        else:
            query = """
            UPDATE conversations 
            SET last_message_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            """ if db_manager._db_type == 'postgresql' else """
            UPDATE conversations 
            SET last_message_at = datetime('now'), updated_at = datetime('now')
            WHERE user_id = ?
            """
            db_manager.execute_query(query, (user_id,))
        
        return True
    except Exception as e:
        logger.error(f"Error updating conversation activity for {user_id}: {e}")
        return False

def get_user_by_topic_id(topic_id: int) -> Optional[int]:
    """Get user ID by topic ID."""
    try:
        query = """
        SELECT user_id FROM conversations WHERE topic_id = %s
        """ if db_manager._db_type == 'postgresql' else """
        SELECT user_id FROM conversations WHERE topic_id = ?
        """
        result = db_manager.execute_query(query, (topic_id,), fetch_one=True)
        return result['user_id'] if result else None
    except Exception as e:
        logger.error(f"Error getting user by topic ID {topic_id}: {e}")
        return None

def get_user_info(user_id: int) -> Optional[Dict[str, Any]]:
    """Get detailed user information."""
    try:
        query = """
        SELECT telegram_id, username, first_name, last_name, message_credits, 
               time_credits, is_banned, ban_reason, created_at, updated_at, last_active
        FROM users 
        WHERE telegram_id = %s
        """ if db_manager._db_type == 'postgresql' else """
        SELECT telegram_id, username, first_name, last_name, message_credits, 
               time_credits, is_banned, ban_reason, created_at, updated_at, last_active
        FROM users 
        WHERE telegram_id = ?
        """
        
        result = db_manager.execute_query(query, (user_id,), fetch_one=True)
        return dict(result) if result else None
        
    except Exception as e:
        logger.error(f"Error getting user info for {user_id}: {e}")
        return None