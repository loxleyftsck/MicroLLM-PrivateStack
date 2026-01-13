"""
API Gateway - Main Flask application with authentication and endpoints
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

#Initialize Flask app
app = Flask(__name__)
CORS(app, origins=os.getenv("CORS_ORIGINS", "*").split(","))

# Configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-key")


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "MicroLLM-PrivateStack",
        "version": "1.0.0"
    }), 200


@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat endpoint - placeholder"""
    data = request.get_json()
    message = data.get("message", "")
    
    return jsonify({
        "response": f"Echo: {message}",
        "status": "success"
    }), 200


if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting MicroLLM-PrivateStack API on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
