# -*- coding: utf-8 -*-
"""
Create Test User for Stress Testing
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from database import DatabaseManager
from auth import AuthManager

def create_test_user():
    """Create test user for stress testing"""
    
    print("Creating stress test user...")
    
    # Initialize database and auth
    try:
        db = DatabaseManager(db_path='data/microllm.db')
        JWT_SECRET = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
        auth = AuthManager(secret_key=JWT_SECRET, db_manager=db)
        
    except Exception as e:
        print(f"Failed to initialize: {e}")
        return
    
    # Test user credentials
    email = "test@stress.local"
    password = "stress123"
    
    try:
        # Check if user exists
        existing_user = db.get_user_by_email(email)
        
        if existing_user:
            print("Test user already exists")
            # Login to get token
            login_result = auth.login_user(email, password)
            token = login_result['token'] if isinstance(login_result, dict) else login_result
            print(f"\nToken: {token}\n")
            
            # Save token
            with open("test_token.txt", 'w') as f:
                f.write(token)  
            print("Token saved to test_token.txt")
            return
        
        # Create new user
        user_data = auth.register_user(
            email=email,
            password=password,
            display_name="Stress Test User"
        )
        
        print(f"User created: {user_data['user_id']}")
        
        # Login to get token
        login_result = auth.login_user(email, password)
        token = login_result['access_token'] if isinstance(login_result, dict) else login_result
        print(f"\nToken: {token}\n")
        
        # Save token
        with open("test_token.txt", 'w') as f:
            f.write(token)
        
        print("Token saved to test_token.txt")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    create_test_user()
