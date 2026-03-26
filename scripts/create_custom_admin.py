# -*- coding: utf-8 -*-
"""
Create Custom Admin Account
Interactive script to create admin with YOUR email.

SECURITY (2026-03-26):
  - Password collected via getpass — never hardcoded or written plaintext to disk.
  - JWT_SECRET_KEY must be set as an OS environment variable.
"""

import sys
import os
import getpass
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from database import DatabaseManager
from auth import AuthManager

# ── Known weak JWT secrets — same blocklist as api_gateway.py ──
_KNOWN_WEAK_SECRETS = {
    "",
    "change-me-in-production",
    "dev-secret-key-change-in-production",
    "secret",
    "changeme",
    "your-secret-key",
    "jwt-secret",
}

def create_custom_admin():
    """Create admin account with custom email"""
    
    print("=" * 70)
    print("MicroLLM-PrivateStack - Custom Admin Account Setup")
    print("=" * 70)
    
    # Get custom email
    print("\n📧 Enter your email for admin account:")
    print("   (Example: admin@gmail.com)")
    custom_email = input("   Email: ").strip()
    
    if not custom_email or '@' not in custom_email:
        print("❌ Invalid email format!")
        return
    
    # Get custom password
    print("\n🔑 Enter password for admin account:")
    print("   (Minimum 8 characters, NOT your Gmail password!)")
    custom_password = getpass.getpass("   Password: ")
    
    if len(custom_password) < 8:
        print("❌ Password must be at least 8 characters!")
        return
    
    # Confirm password
    confirm_password = getpass.getpass("   Confirm password: ")
    
    if custom_password != confirm_password:
        print("❌ Passwords don't match!")
        return
    
    # Get display name
    print("\n👤 Enter your display name:")
    display_name = input("   Name (default: Admin): ").strip()
    if not display_name:
        display_name = "Admin"
    
    # Initialize database and auth
    try:
        db = DatabaseManager(db_path='data/microllm.db')
        print("\n✅ Database connected")
        
        JWT_SECRET = os.getenv("JWT_SECRET_KEY", "")
        if JWT_SECRET in _KNOWN_WEAK_SECRETS or len(JWT_SECRET) < 32:
            print(
                "\n[FATAL] JWT_SECRET_KEY is absent or weak.\n"
                "Set it via: $env:JWT_SECRET_KEY = "
                "(python -c \"import secrets; print(secrets.token_hex(32))\")\n"
            )
            sys.exit(1)
        auth = AuthManager(secret_key=JWT_SECRET, db_manager=db)
        print("✅ Auth manager initialized")
        
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Create admin account
    print(f"\n🔨 Creating admin account...")
    print(f"   Email: {custom_email}")
    print(f"   Name: {display_name}")
    
    try:
        # Check if user exists
        existing_user = db.get_user_by_email(custom_email)
        
        if existing_user:
            print(f"\n⚠️  User already exists with this email!")
            reset = input("   Delete and recreate? (y/N): ").lower()
            if reset == 'y':
                conn = db.get_connection()
                conn.execute('DELETE FROM users WHERE email = ?', (custom_email,))
                conn.commit()
                conn.close()
                print("✅ Old account deleted")
            else:
                print("\n✅ Keeping existing account")
                return
        
        # Create new user
        user_data = auth.register_user(
            email=custom_email,
            password=custom_password,
            display_name=display_name
        )
        
        print("\n✅ Admin account created successfully!")
        print(f"\n📊 Account details:")
        print(f"   User ID: {user_data['user_id']}")
        print(f"   Email: {user_data['email']}")
        print(f"   Name: {user_data['display_name']}")
        print(f"   Default Workspace: {user_data['workspace_id']}")
        
        # Create additional workspaces
        print("\n📁 Creating workspaces...")
        workspaces = [
            ("Development", "Development and testing"),
            ("Production", "Production environment"),
            ("Personal", "Personal workspace")
        ]
        
        for ws_name, ws_desc in workspaces:
            db.create_workspace(user_data['user_id'], ws_name, ws_desc)
            print(f"   ✅ {ws_name}")
        
        # Save non-sensitive account info only (no password on disk)
        creds_file = Path("MY_CREDENTIALS.txt")
        with open(creds_file, 'w') as f:
            f.write("# MicroLLM Account Info\n")
            f.write("# Password is NOT stored here — keep it in your password manager.\n\n")
            f.write(f"Email: {custom_email}\n")
            f.write(f"Name: {display_name}\n\n")
            f.write("Login at: frontend/login.html\n")

        print(f"\nAccount info (no password) saved to: MY_CREDENTIALS.txt")
        
        print("\n" + "=" * 70)
        print("✅ SETUP COMPLETE!")
        print("=" * 70)
        
        print(f"\nLogin credentials:")
        print(f"   Email   : {custom_email}")
        print(f"   Password: (the one you just entered — store it in your password manager)")
        
        print(f"\n🌐 Login at:")
        print(f"   {Path().absolute()}/frontend/login.html")
        
        print("\n⚠️  IMPORTANT:")
        print("   1. Credentials saved in MY_CREDENTIALS.txt")
        print("   2. This file is in .gitignore (safe)")
        print("   3. Do NOT share this file!")
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    create_custom_admin()
