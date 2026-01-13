# -*- coding: utf-8 -*-
"""
Create Admin Account
Run this script to create the initial admin/developer account
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from database import DatabaseManager
from auth import AuthManager

def create_admin_account():
    """Create admin account for MicroLLM-PrivateStack"""
    
    print("=" * 70)
    print("MicroLLM-PrivateStack - Admin Account Setup")
    print("=" * 70)
    
    # Initialize database and auth
    try:
        db = DatabaseManager(db_path='data/microllm.db')
        print("✅ Database connected")
        
        # Use same secret key as in api_gateway.py
        JWT_SECRET = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
        auth = AuthManager(secret_key=JWT_SECRET, db_manager=db)
        print("✅ Auth manager initialized")
        
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Admin credentials
    admin_email = "admin@microllm.local"
    admin_password = "Admin@123456"  # CHANGE THIS IN PRODUCTION!
    admin_name = "System Administrator"
    
    print("\n📋 Creating admin account:")
    print(f"   Email: {admin_email}")
    print(f"   Password: {admin_password}")
    print(f"   Name: {admin_name}")
    
    try:
        # Check if admin already exists
        existing_user = db.get_user_by_email(admin_email)
        
        if existing_user:
            print(f"\n⚠️  Admin account already exists!")
            print(f"   User ID: {existing_user['id']}")
            print(f"   Created: {existing_user['created_at']}")
            
            # Show existing workspaces
            workspaces = db.get_user_workspaces(existing_user['id'])
            print(f"   Workspaces: {len(workspaces)}")
            
            # Ask if want to reset password
            reset = input("\n❓ Reset admin password? (y/N): ").lower()
            if reset == 'y':
                # Delete old user and recreate
                print("⚠️  Deleting existing admin account...")
                # Note: This will cascade delete workspaces, chats, etc.
                conn = db.get_connection()
                conn.execute('DELETE FROM users WHERE email = ?', (admin_email,))
                conn.commit()
                conn.close()
                print("✅ Old account deleted")
            else:
                print("\n✅ Admin account ready to use!")
                print(f"\n🔐 Login credentials:")
                print(f"   Email: {admin_email}")
                print(f"   Password: {admin_password}")
                return
        
        # Create admin user
        user_data = auth.register_user(
            email=admin_email,
            password=admin_password,
            display_name=admin_name
        )
        
        print("\n✅ Admin account created successfully!")
        print(f"\n📊 Account details:")
        print(f"   User ID: {user_data['user_id']}")
        print(f"   Email: {user_data['email']}")
        print(f"   Name: {user_data['display_name']}")
        print(f"   Workspace ID: {user_data['workspace_id']}")
        
        # Create additional workspaces for admin
        print("\n📁 Creating additional workspaces...")
        
        workspaces = [
            ("Development", "Development and testing workspace"),
            ("Production", "Production environment workspace"),
            ("Security Audits", "Security testing and compliance")
        ]
        
        for ws_name, ws_desc in workspaces:
            ws_id = db.create_workspace(user_data['user_id'], ws_name, ws_desc)
            print(f"   ✅ Created: {ws_name}")
        
        # Get database stats
        stats = db.get_stats()
        print(f"\n📊 Database statistics:")
        print(f"   Users: {stats['users']}")
        print(f"   Workspaces: {stats['workspaces']}")
        print(f"   Messages: {stats['messages']}")
        print(f"   Sessions: {stats['sessions']}")
        print(f"   Audit logs: {stats['audit_logs']}")
        
        print("\n" + "=" * 70)
        print("✅ ADMIN ACCOUNT READY!")
        print("=" * 70)
        
        print(f"\n🔐 Login credentials:")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        
        print(f"\n🌐 Access the application:")
        print(f"   Login page: file:///{Path().absolute()}/frontend/login.html")
        print(f"   API endpoint: http://localhost:8000")
        
        print(f"\n⚠️  IMPORTANT:")
        print(f"   1. CHANGE THE PASSWORD after first login!")
        print(f"   2. DO NOT commit this password to git")
        print(f"   3. Store credentials securely")
        
        print("\n" + "=" * 70)
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    create_admin_account()
