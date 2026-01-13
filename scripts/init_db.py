#!/usr/bin/env python3
"""
Initialize Database
Creates user and system tables
"""

import os
import sqlite3
from pathlib import Path
import hashlib

DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "app.db"


def create_tables(conn):
    """Create database tables"""
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    
    # Query history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            query TEXT NOT NULL,
            response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    conn.commit()
    print("✓ Database tables created")


def create_default_user(conn):
    """Create default admin user"""
    cursor = conn.cursor()
    
    # Check if admin exists
    cursor.execute("SELECT id FROM users WHERE username = ?", ("admin@microllm.local",))
    if cursor.fetchone():
        print("✓ Default admin user already exists")
        return
    
    # Create admin user with hashed password
    # Password: changeme123
    password_hash = hashlib.sha256("changeme123".encode()).hexdigest()
    
    cursor.execute("""
        INSERT INTO users (username, password_hash, role)
        VALUES (?, ?, ?)
    """, ("admin@microllm.local", password_hash, "admin"))
    
    conn.commit()
    print("✓ Created default admin user")
    print("  Username: admin@microllm.local")
    print("  Password: changeme123")
    print("  ⚠️  CHANGE THIS PASSWORD IN PRODUCTION!")


def main():
    """Main initialization logic"""
    print("=" * 70)
    print("MicroLLM-PrivateStack - Database Initialization")
    print("=" * 70)
    print()
    
    # Create data directory
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    
    try:
        create_tables(conn)
        create_default_user(conn)
        
        print()
        print(f"Database initialized at: {DB_PATH}")
        print("You can now start the API server.")
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()
