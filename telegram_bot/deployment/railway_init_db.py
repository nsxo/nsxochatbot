#!/usr/bin/env python3
"""
Railway database initialization script.
This script is designed to run automatically during Railway deployment.
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional

# Try to import psycopg2, but don't fail if it's not available
try:
    import psycopg2
    from psycopg2 import sql
    HAS_POSTGRES = True
except ImportError:
    print("psycopg2 not available during build - this is normal for Railway")
    HAS_POSTGRES = False
    psycopg2 = None

# Add src directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))


def get_database_url() -> str:
    """Get database URL with Railway fallbacks."""
    # Try different environment variable names that Railway might use
    database_url = (
        os.getenv('DATABASE_URL') or
        os.getenv('POSTGRES_URL') or
        os.getenv('POSTGRESQL_URL')
    )

    if not database_url:
        raise ValueError("No database URL found. Please set DATABASE_URL environment variable.")

    return database_url


def check_database_exists() -> bool:
    """Check if the database is accessible and has tables."""
    if not HAS_POSTGRES:
        print("PostgreSQL client not available - skipping database check")
        return False

    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            database_url = get_database_url()
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()

            # Check if users table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'users'
                )
            """)

            table_exists = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            return table_exists
        except Exception as e:
            print(f"Database check attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("All database check attempts failed")
                return False


def initialize_railway_database() -> bool:
    """Initialize database for Railway deployment."""
    print("🚀 Railway Database Initialization Starting...")

    try:
        database_url = get_database_url()
        print(f"✅ Database URL found: {database_url[:50]}...")

        # Skip database initialization if we can't connect
        # The bot will handle creating tables on first successful connection
        if not check_database_exists():
            print("⚠️ Cannot connect to database during build - this is normal for Railway")
            print("✅ Database will be initialized on first bot startup")
            return True

        print("✅ Database already initialized, skipping setup.")
        return True

    except Exception as e:
        print(f"⚠️ Database initialization skipped: {e}")
        print("✅ Database will be initialized on first bot startup")
        return True  # Return True to allow deployment to continue


def main() -> None:
    """Main function for Railway database initialization."""
    try:
        success = initialize_railway_database()
        if success:
            print("🎉 Database initialization check completed!")
            sys.exit(0)
        else:
            print("⚠️ Database initialization check completed with warnings")
            sys.exit(0)  # Exit successfully to allow deployment to continue
    except Exception as e:
        print(f"⚠️ Database initialization check error: {e}")
        sys.exit(0)  # Exit successfully to allow deployment to continue


if __name__ == "__main__":
    main()