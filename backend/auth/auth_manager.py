# -*- coding: utf-8 -*-
"""
Authentication Manager - JWT-based authentication with bcrypt
Handles user registration, login, token generation/validation
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class AuthManager:
    """
    Manages authentication with JWT tokens and bcrypt password hashing
    Integrates with DatabaseManager for user operations
    """
    
    def __init__(self, secret_key: str, db_manager):
        self.secret_key = secret_key
        self.db = db_manager
        self.token_expiry_days = 7
        logger.info("✅ Auth manager initialized")
    
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def generate_token(self, user_id: str, email: str) -> str:
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=self.token_expiry_days),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
       return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def register_user(
        self,
        email: str,
        password: str,
        display_name: str
    ) -> Dict:
        """Register new user"""
        # Validate email format
        if '@' not in email:
            raise ValueError("Invalid email format")
        
        # Validate password strength
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        # Hash password
        password_hash = self.hash_password(password)
        
        # Create user in database
        try:
            user_id = self.db.create_user(email, password_hash, display_name)
        except ValueError as e:
            # Email already exists
            raise
        
        # Create default workspace
        workspace_id = self.db.create_workspace(
            user_id,
            "Default Workspace",
            "Your personal workspace"
        )
        
        # Initialize default security settings
        self.db.update_security_settings(user_id, {
            'pii_masking': True,
            'injection_detection': True,
            'toxicity_filter': True,
            'hallucination_check': True,
            'audit_logging': True
        })
        
        # Log audit
        self.db.log_audit(
            action='user_registered',
            user_id=user_id,
            details=f"New user registered: {email}"
        )
        
        logger.info(f"✅ User registered: {email}")
        
        return {
            'user_id': user_id,
            'email': email,
            'display_name': display_name,
            'workspace_id': workspace_id
        }
    
    def login_user(
        self,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict:
        """Login user and return token"""
        # Get user from database
        user = self.db.get_user_by_email(email)
        
        if not user:
            logger.warning(f"Login failed: User not found - {email}")
            raise ValueError("Invalid credentials")
        
        # Verify password
        if not self.verify_password(password, user['password_hash']):
            logger.warning(f"Login failed: Invalid password - {email}")
            self.db.log_audit(
                action='login_failed',
                user_id=user['id'],
                details="Invalid password",
                ip_address=ip_address
            )
            raise ValueError("Invalid credentials")
        
        # Check if user is active
        if not user.get('is_active', True):
            logger.warning(f"Login failed: User inactive - {email}")
            raise ValueError("Account is deactivated")
        
        # Generate JWT token
        token = self.generate_token(user['id'], user['email'])
        
        # Create session in database
        self.db.create_session(
            user_id=user['id'],
            token=token,
            expires_hours=self.token_expiry_days * 24,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Update last login
        self.db.update_last_login(user['id'])
        
        # Log audit
        self.db.log_audit(
            action='login_success',
            user_id=user['id'],
            details=f"User logged in: {email}",
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f"✅ User logged in: {email}")
        
        return {
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'display_name': user['display_name']
            }
        }
    
    def logout_user(self, token: str):
        """Logout user (invalidate session)"""
        # Validate and get user from token
        payload = self.verify_token(token)
        if payload:
            user_id = payload['user_id']
            
            # Delete session
            self.db.delete_session(token)
            
            # Log audit
            self.db.log_audit(
                action='logout',
                user_id=user_id
            )
            
            logger.info(f"✅ User logged out: {user_id}")
    
    def require_auth(self, f):
        """
        Decorator for protected routes
        Validates JWT token and adds user context to request
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get Authorization header
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Missing Authorization header"
                }), 401
            
            # Extract token (format: "Bearer <token>")
            if not auth_header.startswith('Bearer '):
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Invalid Authorization header format. Use 'Bearer <token>'"
                }), 401
            
            token = auth_header.split(' ')[1]
            
            # Verify token
            payload = self.verify_token(token)
            
            if not payload:
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Invalid or expired token"
                }), 401
            
            # Verify session exists in database
            user_id_from_session = self.db.validate_session(token)
            
            if not user_id_from_session:
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Session expired or invalid"
                }), 401
            
            # Add user context to request
            request.user_id = payload['user_id']
            request.user_email = payload['email']
            
            # Log API access in audit trail
            self.db.log_audit(
                action=f"api_call_{f.__name__}",
                user_id=request.user_id,
                resource=request.path,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            return f(*args, **kwargs)
        
        return decorated
    
    def get_current_user(self, token: str) -> Optional[Dict]:
        """Get current user from token"""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user = self.db.get_user_by_id(payload['user_id'])
        if not user:
            return None
        
        # Remove password hash from response
        user_data = dict(user)
        user_data.pop('password_hash', None)
        
        return user_data
