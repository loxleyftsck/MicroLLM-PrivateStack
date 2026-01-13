# -*- coding: utf-8 -*-
"""
LLM Engine Module - Optimized for 2GB RAM
Enhanced logging and error handling
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Generator, Union

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    logging.warning("llama-cpp-python not installed. LLM engine will use mock responses.")

logger = logging.getLogger(__name__)


class LLMEngine:
    """
    Core LLM inference engine using llama.cpp
    Optimized for 2GB RAM constraint
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model: Optional[Llama] = None
        self.model_loaded = False
        self.load_error: Optional[str] = None
        
        # Log configuration
        logger.info("=" * 70)
        logger.info("LLM Engine Initialization")
        logger.info("=" * 70)
        logger.info(f"llama-cpp-python available: {LLAMA_CPP_AVAILABLE}")
        logger.info(f"Config: {config}")
        logger.info("=" * 70)
        
        # Load model
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the GGUF model into memory with detailed logging"""
        if not LLAMA_CPP_AVAILABLE:
            self.load_error = "llama-cpp-python not installed"
            logger.warning(f"⚠️ {self.load_error}")
            return
        
        # Get model path (convert to absolute path)
        model_path_raw = self.config.get("MODEL_PATH", "../models/deepseek-r1-1.5b-q4.gguf")
        model_path = Path(model_path_raw).resolve()
        
        logger.info(f"Model path (raw): {model_path_raw}")
        logger.info(f"Model path (absolute): {model_path}")
        logger.info(f"Model exists: {model_path.exists()}")
        
        if not model_path.exists():
            self.load_error = f"Model file not found at {model_path}"
            logger.error(f"❌ {self.load_error}")
            logger.info("Please run: python scripts/download_model.py")
            return
        
        # Log file info
        file_size_mb = model_path.stat().st_size / (1024 * 1024)
        logger.info(f"Model file size: {file_size_mb:.1f} MB")
        
        # Optimize settings for 2GB RAM
        n_ctx = int(self.config.get("MODEL_CONTEXT_LENGTH", 512))  # Reduced from 2048
        n_threads = int(self.config.get("MODEL_THREADS", 2))  # Reduced from 4
        n_batch = int(self.config.get("MODEL_BATCH", 256))  # Reduced from 512
        
        logger.info("Loading model with MINIMAL settings for 2GB RAM:")
        logger.info(f"  - Context length: {n_ctx} tokens")
        logger.info(f"  - Threads: {n_threads}")
        logger.info(f"  - Batch size: {n_batch}")
        logger.info(f"  - GPU layers: 0 (CPU only)")
        
        try:
            logger.info("Starting model load... (this may take 30-60 seconds)")
            
            self.model = Llama(
                model_path=str(model_path),
                n_ctx=n_ctx,
                n_threads=n_threads,
                n_batch=n_batch,
                verbose=True,  # Enable llama.cpp logging
                n_gpu_layers=0,  # CPU only
                use_mlock=False,  # Don't lock memory (safer for low RAM)
                use_mmap=True,   # Use memory mapping (more efficient)
                low_vram=True,   # Low VRAM mode
            )
            
            self.model_loaded = True
            logger.info("✅ Model loaded successfully!")
            logger.info(f"Model type: {type(self.model)}")
            
        except MemoryError as e:
            self.load_error = f"Out of memory: {str(e)}"
            logger.error(f"❌ MEMORY ERROR: {self.load_error}")
            logger.error("💡 This machine may not have enough RAM for this model.")
            logger.error("   Try: 1) Smaller model (Q2_K), 2) Lower n_ctx, 3) Close other apps")
            self.model_loaded = False
            
        except Exception as e:
            self.load_error = f"Failed to load model: {str(e)}"
            logger.exception(f"❌ MODEL LOAD ERROR: {self.load_error}")
            logger.error(f"Error type: {type(e).__name__}")
            self.model_loaded = False
    
    def generate(self, prompt: str, max_tokens: int = 256, temperature: float = None,
                 top_p: float = None, stream: bool = False) -> Union[str, Generator[str, None, None]]:
        """Generate text completion (optimized for 2GB RAM)"""
        if temperature is None:
            temperature = float(self.config.get("MODEL_TEMPERATURE", 0.7))
        if top_p is None:
            top_p = float(self.config.get("MODEL_TOP_P", 0.9))
        
        # Cap max_tokens for low RAM
        max_tokens = min(max_tokens, 256)  # Never exceed 256 tokens
        
        if not self.model_loaded:
            logger.warning(f"Model not loaded: {self.load_error}")
            return self._mock_response(prompt, stream)
        
        formatted_prompt = self._format_prompt(prompt)
        
        logger.info(f"Generating response (max_tokens={max_tokens}, temp={temperature})")
        
        if stream:
            return self._stream_generate(formatted_prompt, max_tokens, temperature, top_p)
        else:
            return self._sync_generate(formatted_prompt, max_tokens, temperature, top_p)
    
    def _sync_generate(self, prompt: str, max_tokens: int, temperature: float, top_p: float) -> str:
        """Synchronous text generation"""
        try:
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=["</s>", "Human:", "User:", "\n\nUser:"],
                echo=False
            )
            result = response['choices'][0]['text'].strip()
            logger.info(f"Generated {len(result)} characters")
            return result
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return f"Error generating response: {str(e)}"
    
    def _stream_generate(self, prompt: str, max_tokens: int, temperature: float, 
                        top_p: float) -> Generator[str, None, None]:
        """Stream text generation token by token"""
        try:
            for output in self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=["</s>", "Human:", "User:"],
                stream=True
            ):
                token = output['choices'][0]['text']
                if token:
                    yield token
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"\n\nError: {str(e)}"
    
    def _format_prompt(self, user_prompt: str) -> str:
        """Format prompt with system instructions"""
        system_prompt = "You are a helpful business analyst. Provide concise, actionable insights."
        return f"{system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"
    
    def _mock_response(self, prompt: str, stream: bool = False) -> Union[str, Generator[str, None, None]]:
        """Mock response when model not loaded"""
        reason = self.load_error or "Model not initialized"
        mock_text = f"""[DEMO MODE]

Reason: {reason}

Your query: "{prompt[:100]}..."

To enable real LLM inference:
1. Ensure model downloaded: python scripts/download_model.py
2. Check logs for errors: server.log
3. Verify RAM available: At least 2GB free
4. Restart server

Currently running in DEMO mode."""
        
        if stream:
            def mock_gen():
                for word in mock_text.split():
                    yield word + " "
            return mock_gen()
        else:
            return mock_text
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get detailed information about loaded model"""
        model_path = Path(self.config.get("MODEL_PATH", "Not set")).resolve()
        
        info = {
            "loaded": self.model_loaded,
            "model_path": str(model_path),
            "model_path_exists": model_path.exists(),
            "context_length": self.config.get("MODEL_CONTEXT_LENGTH", 512),
            "threads": self.config.get("MODEL_THREADS", 2),
            "llama_cpp_available": LLAMA_CPP_AVAILABLE,
        }
        
        if not self.model_loaded and self.load_error:
            info["error"] = self.load_error
        
        if model_path.exists():
            info["model_size_mb"] = round(model_path.stat().st_size / (1024 * 1024), 1)
        
        return info
