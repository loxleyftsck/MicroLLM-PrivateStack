# -*- coding: utf-8 -*-
"""
Create Admin Account
Run this script to create the initial admin/developer account.

SECURITY (2026-03-26):
  - Credentials entered interactively via getpass — never hardcoded.
  - JWT_SECRET_KEY must be set as an OS environment variable.
    The script refuses to run with weak/default secrets.
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


def _get_jwt_secret() -> str:
    jwt_secret = os.getenv("JWT_SECRET_KEY", "")
    if jwt_secret in _KNOWN_WEAK_SECRETS or len(jwt_secret) < 32:
        print(
            "\n[FATAL] JWT_SECRET_KEY is absent, too short, or a known weak default.\n"
            "Generate one and set it before running this script:\n"
            "  PowerShell: $env:JWT_SECRET_KEY = "
            "(python -c \"import secrets; print(secrets.token_hex(32))\")\n"
        )
        sys.exit(1)
    return jwt_secret


def create_admin_account() -> None:
    """Create admin account for MicroLLM-PrivateStack (interactive)."""
    print("=" * 70)
    print("MicroLLM-PrivateStack - Admin Account Setup")
    print("=" * 70)

    # ── Initialise DB + Auth ──
    try:
        db = DatabaseManager(db_path='data/microllm.db')
        print("OK  Database connected")

        jwt_secret = _get_jwt_secret()
        auth = AuthManager(secret_key=jwt_secret, db_manager=db)
        print("OK  Auth manager initialised")
    except SystemExit:
        raise
    except Exception as e:
        print(f"ERR Failed to initialise: {e}")
        return

    # ── Collect credentials interactively ──
    print("\nEnter admin account credentials (nothing is hardcoded):")
    admin_email = input("  Email: ").strip()
    if not admin_email or '@' not in admin_email:
        print("ERR Invalid email.")
        return

    admin_password = getpass.getpass("  Password (min 8 chars): ")
    if len(admin_password) < 8:
        print("ERR Password too short.")
        return

    confirm = getpass.getpass("  Confirm password: ")
    if admin_password != confirm:
        print("ERR Passwords do not match.")
        return

    admin_name = input("  Display name [System Administrator]: ").strip()
    if not admin_name:
        admin_name = "System Administrator"

    # ── Create or reset user ──
    try:
        existing = db.get_user_by_email(admin_email)
        if existing:
            print(f"\nWARN User already exists (ID: {existing['id']})")
            reset = input("  Delete and recreate? (y/N): ").strip().lower()
            if reset == 'y':
                conn = db.get_connection()
                conn.execute('DELETE FROM users WHERE email = ?', (admin_email,))
                conn.commit()
                conn.close()
                print("OK   Old account deleted")
            else:
                print("OK   Keeping existing account. Exiting.")
                return

        user_data = auth.register_user(
            email=admin_email,
            password=admin_password,
            display_name=admin_name,
        )

        print("\nOK  Admin account created successfully!")
        print(f"    User ID   : {user_data['user_id']}")
        print(f"    Email     : {user_data['email']}")
        print(f"    Name      : {user_data['display_name']}")
        print(f"    Workspace : {user_data['workspace_id']}")

        # Extra workspaces
        for ws_name, ws_desc in [
            ("Development", "Development and testing workspace"),
            ("Production",  "Production environment workspace"),
            ("Security Audits", "Security testing and compliance"),
        ]:
            db.create_workspace(user_data['user_id'], ws_name, ws_desc)
            print(f"    Workspace '{ws_name}' created")

        stats = db.get_stats()
        print(f"\n    DB stats: {stats}")

        print("\n" + "=" * 70)
        print("ADMIN ACCOUNT READY")
        print("=" * 70)
        print("\nLogin via: frontend/login.html")
        print("IMPORTANT: Do not share or commit credentials.\n")

    except ValueError as e:
        print(f"\nERR {e}")
    except Exception as e:
        print(f"\nERR Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    create_admin_account()
