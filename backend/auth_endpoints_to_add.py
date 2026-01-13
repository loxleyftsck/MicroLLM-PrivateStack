# -*- coding: utf-8 -*-
"""
Authentication Endpoints
Add these to api_gateway.py before the server startup
"""

# ============================================
# Authentication Endpoints
# ============================================

@app.route("/api/auth/register", methods=["POST"])
def register():
    """User registration endpoint"""
    if not auth:
        return jsonify({"error": "Authentication not available"}), 503
    
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        display_name = data.get('display_name', email.split('@')[0] if email else '')
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
        
        # Register user
        user_data = auth.register_user(email, password, display_name)
        
        # Generate token
        token = auth.generate_token(user_data['user_id'], user_data['email'])
        
        return jsonify({
            "message": "Registration successful",
            "token": token,
            "user": {
                "id": user_data['user_id'],
                "email": user_data['email'],
                "display_name": user_data['display_name']
            },
            "workspace_id": user_data['workspace_id']
        }), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"error": "Registration failed"}), 500


@app.route("/api/auth/login", methods=["POST"])
def login():
    """User login endpoint"""
    if not auth:
        return jsonify({"error": "Authentication not available"}), 503
    
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
        
        # Login user
        login_data = auth.login_user(
            email,
            password,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify(login_data), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Login failed"}), 500


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    """User logout endpoint"""
    if not auth:
        return jsonify({"error": "Authentication not available"}), 503
    
    try:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            auth.logout_user(token)
        
        return jsonify({"message": "Logged out successfully"}), 200
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({"error": "Logout failed"}), 500


@app.route("/api/auth/me", methods=["GET"])
def get_current_user_info():
    """Get current user information"""
    if not auth:
        return jsonify({"error": "Authentication not available"}), 503
    
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
        
        token = auth_header.split(' ')[1]
        payload = auth.verify_token(token)
        
        if not payload:
            return jsonify({"error": "Invalid token"}), 401
        
        user = db.get_user_by_id(payload['user_id'])
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Remove sensitive data
        user_data = dict(user)
        user_data.pop('password_hash', None)
        
        return jsonify({"user": user_data}), 200
        
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({"error": "Failed to get user info"}), 500
