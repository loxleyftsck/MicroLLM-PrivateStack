# -*- coding: utf-8 -*-
"""
API Gateway - Main Flask application with LLM integration
Enhanced logging and 2GB RAM optimization
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
import logging
from pathlib import Path

# Configure logging FIRST
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../logs/server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import LLM engine
from llm_engine import LLMEngine

# Import security modules
try:
    from security.guardrails import OutputGuardrail, GuardrailResult
    from security.validators import DataIngestionValidator, ValidationError
    SECURITY_AVAILABLE = True
    logger.info("✅ Security modules loaded")
except ImportError as e:
    SECURITY_AVAILABLE = False
    logger.warning(f"⚠️ Security modules not available: {e}")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")

# Initialize LLM Engine with ABSOLUTE path
logger.info("=" * 70)
logger.info("MicroLLM-PrivateStack API Gateway")
logger.info("=" * 70)
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Script location: {__file__}")

# Use absolute path for model
BASE_DIR = Path(__file__).parent.parent
MODEL_PATH = BASE_DIR / "models" / "deepseek-r1-1.5b-q4.gguf"

logger.info(f"Base directory: {BASE_DIR}")
logger.info(f"Model path: {MODEL_PATH}")
logger.info(f"Model exists: {MODEL_PATH.exists()}")

llm_config = {
    "MODEL_PATH": str(MODEL_PATH),  # Absolute path
    "MODEL_CONTEXT_LENGTH": os.getenv("MODEL_CONTEXT_LENGTH", "512"),   # Optimized for 2GB
    "MODEL_THREADS": os.getenv("MODEL_THREADS", "2"),  # Reduced for 2GB
    "MODEL_BATCH": os.getenv("MODEL_BATCH", "256"),  # Reduced for 2GB
    "MODEL_TEMPERATURE": os.getenv("MODEL_TEMPERATURE", "0.7"),
    "MODEL_TOP_P": os.getenv("MODEL_TOP_P", "0.9"),
}

logger.info("Initializing LLM engine with config:")
for key, value in llm_config.items():
    logger.info(f"  {key}: {value}")

llm_engine = LLMEngine(llm_config)

# Initialize security guardrails
if SECURITY_AVAILABLE:
    output_guardrail = OutputGuardrail({
        'strict_mode': True,
        'toxicity_threshold': 0.7,
        'hallucination_threshold': 0.8,
        'mask_pii': True
    })
    logger.info("✅ Output guardrails initialized")
else:
    output_guardrail = None
    logger.warning("⚠️ Running WITHOUT security guardrails")

logger.info(f"LLM Engine initialized. Model loaded: {llm_engine.model_loaded}")

# ============================================
# Initialize Database and Authentication
# ============================================
from database import DatabaseManager
from auth import AuthManager

try:
    # Initialize database
    db = DatabaseManager(db_path='data/microllm.db')
    logger.info(f"✅ Database initialized: {db.get_stats()}")
    
    # Initialize auth manager
    JWT_SECRET = app.config["JWT_SECRET_KEY"]
    auth = AuthManager(secret_key=JWT_SECRET, db_manager=db)
    logger.info("✅ Authentication system ready")
    
except Exception as e:
    logger.error(f"❌ Database/Auth initialization failed: {e}")
    logger.warning("⚠️ Running in LIMITED MODE without auth")
    db = None
    auth = None

logger.info("=" * 70)


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    model_info = llm_engine.get_model_info()
    
    return jsonify({
        "status": "healthy",
        "service": "MicroLLM-PrivateStack",
        "version": "1.0.1-optimized",
        "model": model_info
    }), 200


@app.route("/api/chat", methods=["POST"])
@auth.require_auth if auth else lambda f: f
def chat():
    """
    Chat endpoint - Real LLM inference with security guardrails
    OWASP ASVS V5.3.1, V5.3.4, V14.4.1
    Optimized for 2GB RAM (max 256 tokens)
    NOW PROTECTED: Requires authentication
    """
    try:
        data = request.get_json()
        
        if not data or "message" not in data:
            return jsonify({
                "error": "Missing 'message' in request body"
            }), 400
        
        message = data.get("message", "")
        
        # Validate and cap for 2GB RAM
        max_tokens = min(int(data.get("max_tokens", 256)), 256)
        temperature = float(data.get("temperature", llm_config["MODEL_TEMPERATURE"]))
        stream = data.get("stream", False)
        
        logger.info(f"Chat request: '{message[:50]}...' (max_tokens={max_tokens})")
        
        # Security check: Input validation (prompt injection detection)
        if output_guardrail and SECURITY_AVAILABLE:
            # Pre-check prompt for injection attempts
            pre_check = output_guardrail._detect_injection(message)
            if pre_check['detected']:
                logger.warning(f"⚠️ Prompt injection blocked: {pre_check}")
                return jsonify({
                    "error": "Request blocked by security guardrails",
                    "reason": "Potential prompt injection detected",
                    "status": "blocked",
                    "security": {
                        "asvs_compliance": ["V5.3.1"],
                        "threat_type": "prompt_injection",
                        "patterns_detected": len(pre_check['patterns'])
                    }
                }), 403
        
        # Generate response
        response = llm_engine.generate(
            prompt=message,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream
        )
        
        if stream:
            return jsonify({
                "error": "Streaming not yet implemented"
            }), 501
        
        # Security check: Output validation (PII, secrets, toxicity)
        if output_guardrail and SECURITY_AVAILABLE:
            validation_result = output_guardrail.validate_output(
                prompt=message,
                response=response,
                context=None
            )
            
            if validation_result.blocked:
                logger.warning(f"⚠️ Response blocked by guardrails: {validation_result.security_checks}")
                return jsonify({
                    "error": "Response blocked by security guardrails",
                    "status": "blocked",
                    "security": {
                        "asvs_compliance": validation_result.asvs_compliance,
                        "checks": {
                            k: v for k, v in validation_result.security_checks.items()
                            if k in ['prompt_injection', 'secrets_leaked', 'toxicity_score']
                        }
                    }
                }), 403
            
            # Use sanitized response (PII masked)
            safe_response = validation_result.response
            
            return jsonify({
                "response": safe_response,
                "status": "success",
                "model_loaded": llm_engine.model_loaded,
                "tokens_generated": len(response.split()),
                "security": {
                    "validated": True,
                    "confidence_score": validation_result.confidence_score,
                    "warnings": validation_result.warnings,
                    "asvs_compliance": validation_result.asvs_compliance
                }
            }), 200
        else:
            # No security validation (fallback)
            logger.warning("⚠️ Responding WITHOUT security validation")
            return jsonify({
                "response": response,
                "status": "success",
                "model_loaded": llm_engine.model_loaded,
                "tokens_generated": len(response.split()),
                "security": {
                    "validated": False,
                    "warning": "Security modules not available"
                }
            }), 200
        
    except Exception as e:
        logger.exception(f"Chat endpoint error: {e}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


@app.route("/api/model/info", methods=["GET"])
def model_info():
    """Get detailed model information"""
    return jsonify(llm_engine.get_model_info()), 200


@app.route("/api/debug/reload", methods=["POST"])
def debug_reload():
    """Debug endpoint to reload model"""
    global llm_engine
    
    logger.info("Manual model reload requested")
    llm_engine = LLMEngine(llm_config)
    
    return jsonify({
        "status": "reloaded",
        "model_loaded": llm_engine.model_loaded,
        "info": llm_engine.get_model_info()
    }), 200


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
        
        user_data = auth.register_user(email, password, display_name)
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
        
        login_data = auth.login_user(
            email, password,
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
        
        user_data = dict(user)
        user_data.pop('password_hash', None)
        return jsonify({"user": user_data}), 200
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({"error": "Failed to get user info"}), 500


# ============================================
# Server Startup
# ============================================

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    if debug:
        logger.warning("⚠️ Running in DEBUG mode - not for production!")
    
    logger.info("=" * 70)
    logger.info(f"Starting server on: http://{host}:{port}")
    logger.info(f"Model status: {'LOADED ✅' if llm_engine.model_loaded else 'NOT LOADED ❌'}")
    if not llm_engine.model_loaded:
        logger.warning(f"Model load error: {llm_engine.load_error}")
        logger.info("API will work in DEMO mode")
    logger.info("=" * 70)
    logger.info("Press CTRL+C to quit")
    
    app.run(host=host, port=port, debug=debug, use_reloader=False)
