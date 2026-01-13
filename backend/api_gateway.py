"""
API Gateway - Main Flask application with LLM integration
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import LLM engine  
try:
    from llm_engine import LLMEngine
except ImportError:
    # Fallback if running from different directory
    sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
    from llm_engine import LLMEngine

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=os.getenv("CORS_ORIGINS", "*").split(","))

# Configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-key")

# Initialize LLM Engine
logger.info("Initializing LLM engine...")
llm_config = {
    "MODEL_PATH": os.getenv("MODEL_PATH", "./models/deepseek-r1-1.5b-q4.gguf"),
    "MODEL_CONTEXT_LENGTH": os.getenv("MODEL_CONTEXT_LENGTH", "2048"),
    "MODEL_THREADS": os.getenv("MODEL_THREADS", "4"),
    "MODEL_TEMPERATURE": os.getenv("MODEL_TEMPERATURE", "0.3"),
    "MODEL_TOP_P": os.getenv("MODEL_TOP_P", "0.9"),
}
llm_engine = LLMEngine(llm_config)


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    model_info = llm_engine.get_model_info()
    
    return jsonify({
        "status": "healthy",
        "service": "MicroLLM-PrivateStack",
        "version": "1.0.0-sprint1",
        "model": model_info
    }), 200


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Chat endpoint - Real LLM inference
    
    Request body:
        {
            "message": "Your question here",
            "max_tokens": 512,  // optional
            "temperature": 0.3,  // optional
            "stream": false      // optional
        }
    """
    try:
        data = request.get_json()
        
        if not data or "message" not in data:
            return jsonify({
                "error": "Missing 'message' in request body"
            }), 400
        
        message = data.get("message", "")
        max_tokens = int(data.get("max_tokens", 512))
        temperature = float(data.get("temperature", llm_config["MODEL_TEMPERATURE"]))
        stream = data.get("stream", False)
        
        logger.info(f"Received chat request: {message[:100]}...")
        
        # Generate response
        response = llm_engine.generate(
            prompt=message,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream
        )
        
        if stream:
            # TODO: Implement SSE streaming
            return jsonify({
                "error": "Streaming not yet implemented in Sprint 1"
            }), 501
        
        logger.info(f"Response generated successfully")
        
        return jsonify({
            "response": response,
            "status": "success",
            "model_loaded": llm_engine.model_loaded
        }), 200
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


@app.route("/api/model/info", methods=["GET"])
def model_info():
    """Get model information"""
    return jsonify(llm_engine.get_model_info()), 200


if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info("=" * 70)
    logger.info("MicroLLM-PrivateStack API Gateway")
    logger.info("=" * 70)
    logger.info(f"Listening on: http://{host}:{port}")
    logger.info(f"Model loaded: {llm_engine.model_loaded}")
    logger.info("=" * 70)
    
    app.run(host=host, port=port, debug=debug)
