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

logger.info(f"LLM Engine initialized. Model loaded: {llm_engine.model_loaded}")
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
def chat():
    """
    Chat endpoint - Real LLM inference
    Optimized for 2GB RAM (max 256 tokens)
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
        
        logger.info(f"Response generated: {len(response)} chars")
        
        return jsonify({
            "response": response,
            "status": "success",
            "model_loaded": llm_engine.model_loaded,
            "tokens_generated": len(response.split())  # Approximate
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
