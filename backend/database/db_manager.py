# -*- coding: utf-8 -*-
"""
Database Manager - SQLite database operations
Handles users, workspaces, chat history, sessions, and audit logs
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages all database operations for MicroLLM-PrivateStack
    Uses SQLite for simplicity and on-premise deployment
    """
    
    def __init__(self, db_path: str = 'data/microllm.db'):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
        logger.info(f"✅ Database initialized: {db_path}")
    
    def init_db(self):
        """Initialize database with schema"""
        schema_path = Path(__file__).parent / 'schema.sql'
        
        if not schema_path.exists():
            logger.error(f"❌ Schema file not found: {schema_path}")
            return
        
        conn = sqlite3.connect(self.db_path)
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            conn.commit()
            logger.info("✅ Database schema applied successfully")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
        finally:
            conn.close()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with Row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, email: str, password_hash: str, display_name: str) -> str:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        conn = self.get_connection()
        try:
            conn.execute(
                'INSERT INTO users (id, email, password_hash, display_name) VALUES (?, ?, ?, ?)',
                (user_id, email, password_hash, display_name)
            )
            conn.commit()
            logger.info(f"✅ User created: {email}")
            return user_id
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️ User already exists: {email}")
            raise ValueError("Email already registered")
        finally:
            conn.close()
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        conn = self.get_connection()
        try:
            user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            return dict(user) if user else None
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.get_connection()
        try:
            user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            return dict(user) if user else None
        finally:
            conn.close()
    
    def update_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        conn = self.get_connection()
        try:
            conn.execute(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                (user_id,)
            )
            conn.commit()
        finally:
            conn.close()
    
    # ==================== WORKSPACE OPERATIONS ====================
    
    def create_workspace(self, user_id: str, name: str, description: str = '') -> str:
        """Create a new workspace"""
        workspace_id = str(uuid.uuid4())
        conn = self.get_connection()
        try:
            conn.execute(
                'INSERT INTO workspaces (id, user_id, name, description) VALUES (?, ?, ?, ?)',
                (workspace_id, user_id, name, description)
            )
            conn.commit()
            logger.info(f"✅ Workspace created: {name} for user {user_id}")
            return workspace_id
        finally:
            conn.close()
    
    def get_user_workspaces(self, user_id: str) -> List[Dict]:
        """Get all workspaces for a user"""
        conn = self.get_connection()
        try:
            workspaces = conn.execute(
                'SELECT * FROM workspaces WHERE user_id = ? ORDER BY created_at DESC',
                (user_id,)
            ).fetchall()
            return [dict(w) for w in workspaces]
        finally:
            conn.close()
    
    def get_workspace(self, workspace_id: str) -> Optional[Dict]:
        """Get workspace by ID"""
        conn = self.get_connection()
        try:
            workspace = conn.execute(
                'SELECT * FROM workspaces WHERE id = ?',
                (workspace_id,)
            ).fetchone()
            return dict(workspace) if workspace else None
        finally:
            conn.close()
    
    def verify_workspace_access(self, user_id: str, workspace_id: str) -> bool:
        """Verify user has access to workspace"""
        conn = self.get_connection()
        try:
            result = conn.execute(
                'SELECT id FROM workspaces WHERE id = ? AND user_id = ?',
                (workspace_id, user_id)
            ).fetchone()
            return result is not None
        finally:
            conn.close()
    
    def delete_workspace(self, workspace_id: str, user_id: str) -> bool:
        """Delete workspace (with ownership check)"""
        conn = self.get_connection()
        try:
            cursor = conn.execute(
                'DELETE FROM workspaces WHERE id = ? AND user_id = ?',
                (workspace_id, user_id)
            )
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"✅ Workspace deleted: {workspace_id}")
            return deleted
        finally:
            conn.close()
    
    # ==================== CHAT HISTORY OPERATIONS ====================
    
    def save_chat_message(
        self,
        workspace_id: str,
        user_id: str,
        role: str,
        message: str,
        assistant_type: Optional[str] = None
    ) -> str:
        """Save chat message"""
        message_id = str(uuid.uuid4())
        conn = self.get_connection()
        try:
            conn.execute(
                '''INSERT INTO chat_history 
                   (id, workspace_id, user_id, role, message, assistant_type) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (message_id, workspace_id, user_id, role, message, assistant_type)
            )
            conn.commit()
            return message_id
        finally:
            conn.close()
    
    def get_chat_history(
        self,
        workspace_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Get chat history for workspace"""
        conn = self.get_connection()
        try:
            messages = conn.execute(
                '''SELECT * FROM chat_history 
                   WHERE workspace_id = ? 
                   ORDER BY timestamp DESC 
                   LIMIT ? OFFSET ?''',
                (workspace_id, limit, offset)
            ).fetchall()
            return [dict(m) for m in reversed(messages)]  # Reverse to chronological order
        finally:
            conn.close()
    
    def delete_chat_history(self, workspace_id: str) -> int:
        """Delete all chat history for workspace"""
        conn = self.get_connection()
        try:
            cursor = conn.execute(
                'DELETE FROM chat_history WHERE workspace_id = ?',
                (workspace_id,)
            )
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    # ==================== SESSION OPERATIONS ====================
    
    def create_session(
        self,
        user_id: str,
        token: str,
        expires_hours: int = 24,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Create new session"""
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(hours=expires_hours)
        
        conn = self.get_connection()
        try:
            conn.execute(
                '''INSERT INTO sessions 
                   (id, user_id, token, expires_at, ip_address, user_agent) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (session_id, user_id, token, expires_at, ip_address, user_agent)
            )
            conn.commit()
            return session_id
        finally:
            conn.close()
    
    def validate_session(self, token: str) -> Optional[str]:
        """Validate session token and return user_id if valid"""
        conn = self.get_connection()
        try:
            session = conn.execute(
                'SELECT user_id, expires_at FROM sessions WHERE token = ?',
                (token,)
            ).fetchone()
            
            if not session:
                return None
            
            expires_at = datetime.fromisoformat(session['expires_at'])
            if datetime.now() > expires_at:
                # Session expired
                conn.execute('DELETE FROM sessions WHERE token = ?', (token,))
                conn.commit()
                return None
            
            return session['user_id']
        finally:
            conn.close()
    
    def delete_session(self, token: str):
        """Delete session (logout)"""
        conn = self.get_connection()
        try:
            conn.execute('DELETE FROM sessions WHERE token = ?', (token,))
            conn.commit()
        finally:
            conn.close()
    
    def delete_user_sessions(self, user_id: str):
        """Delete all sessions for user (logout all devices)"""
        conn = self.get_connection()
        try:
            conn.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
            conn.commit()
        finally:
            conn.close()
    
    # ==================== AUDIT LOG OPERATIONS ====================
    
    def log_audit(
        self,
        action: str,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Log audit event"""
        log_id = str(uuid.uuid4())
        conn = self.get_connection()
        try:
            conn.execute(
                '''INSERT INTO audit_log 
                   (id, user_id, action, resource, details, ip_address, user_agent) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (log_id, user_id, action, resource, details, ip_address, user_agent)
            )
            conn.commit()
            return log_id
        finally:
            conn.close()
    
    def get_audit_log(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """Get audit log entries"""
        conn = self.get_connection()
        try:
            if user_id:
                logs = conn.execute(
                    '''SELECT * FROM audit_log 
                       WHERE user_id = ? 
                       ORDER BY timestamp DESC 
                       LIMIT ? OFFSET ?''',
                    (user_id, limit, offset)
                ).fetchall()
            else:
                logs = conn.execute(
                    'SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ? OFFSET ?',
                    (limit, offset)
                ).fetchall()
            return [dict(log) for log in logs]
        finally:
            conn.close()
    
    # ==================== SECURITY SETTINGS OPERATIONS ====================
    
    def get_security_settings(self, user_id: str) -> Dict[str, bool]:
        """Get user security settings"""
        conn = self.get_connection()
        try:
            settings = conn.execute(
                'SELECT * FROM security_settings WHERE user_id = ?',
                (user_id,)
            ).fetchone()
            
            if settings:
                return dict(settings)
            else:
                # Return defaults
                return {
                    'pii_masking': True,
                    'injection_detection': True,
                    'toxicity_filter': True,
                    'hallucination_check': True,
                    'audit_logging': True
                }
        finally:
            conn.close()
    
    def update_security_settings(self, user_id: str, settings: Dict[str, bool]):
        """Update user security settings"""
        conn = self.get_connection()
        try:
            # Insert or replace
            conn.execute(
                '''INSERT OR REPLACE INTO security_settings 
                   (user_id, pii_masking, injection_detection, toxicity_filter, 
                    hallucination_check, audit_logging, updated_at) 
                   VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)''',
                (
                    user_id,
                    settings.get('pii_masking', True),
                    settings.get('injection_detection', True),
                    settings.get('toxicity_filter', True),
                    settings.get('hallucination_check', True),
                    settings.get('audit_logging', True)
                )
            )
            conn.commit()
            logger.info(f"✅ Security settings updated for user {user_id}")
        finally:
            conn.close()
    
    # ==================== UTILITY OPERATIONS ====================
    
    def close(self):
        """Close database (for graceful shutdown)"""
        logger.info("Database connections closed")
    
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        conn = self.get_connection()
        try:
            stats = {}
            stats['users'] = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
            stats['workspaces'] = conn.execute('SELECT COUNT(*) FROM workspaces').fetchone()[0]
            stats['messages'] = conn.execute('SELECT COUNT(*) FROM chat_history').fetchone()[0]
            stats['sessions'] = conn.execute('SELECT COUNT(*) FROM sessions').fetchone()[0]
            stats['audit_logs'] = conn.execute('SELECT COUNT(*) FROM audit_log').fetchone()[0]
            return stats
        finally:
            conn.close()
