"""
LLM Engine Module - Real inference using llama-cpp-python
Handles model loading, inference, and context management
"""

import os
import logging
from typing import Optional, Dict, Any, Generator, Union
from pathlib import Path

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    logging.warning("llama-cpp-python not installed. LLM engine will use mock responses.")

logger = logging.getLogger(__name__)


class LLMEngine:
    """Core LLM inference engine using llama.cpp"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model: Optional[Llama] = None
        self.model_loaded = False
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the GGUF model into memory"""
        if not LLAMA_CPP_AVAILABLE:
            logger.warning("Skipping model load - llama-cpp-python not available")
            return
        
        model_path = self.config.get("MODEL_PATH", "./models/deepseek-r1-1.5b-q4.gguf")
        
        if not os.path.exists(model_path):
            logger.error(f"Model not found at {model_path}")
            logger.info("Please run: python scripts/download_model.py")
            return
        
        try:
            logger.info(f"Loading model from {model_path}...")
            self.model = Llama(
                model_path=model_path,
                n_ctx=int(self.config.get("MODEL_CONTEXT_LENGTH", 2048)),
                n_threads=int(self.config.get("MODEL_THREADS", 4)),
                n_batch=512,
                verbose=False,
                n_gpu_layers=0
            )
            self.model_loaded = True
            logger.info("✓ Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model_loaded = False
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = None,
                 top_p: float = None, stream: bool = False) -> Union[str, Generator[str, None, None]]:
        """Generate text completion"""
        if temperature is None:
            temperature = float(self.config.get("MODEL_TEMPERATURE", 0.3))
        if top_p is None:
            top_p = float(self.config.get("MODEL_TOP_P", 0.9))
        
        if not self.model_loaded:
            return self._mock_response(prompt, stream)
        
        formatted_prompt = self._format_prompt(prompt)
        
        if stream:
            return self._stream_generate(formatted_prompt, max_tokens, temperature, top_p)
        else:
            return self._sync_generate(formatted_prompt, max_tokens, temperature, top_p)
    
    def _sync_generate(self, prompt: str, max_tokens: int, temperature: float, top_p: float) -> str:
        """Synchronous text generation"""
        try:
            response = self.model(prompt, max_tokens=max_tokens, temperature=temperature,
                                top_p=top_p, stop=["</s>", "Human:", "User:"], echo=False)
            return response['choices'][0]['text'].strip()
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return f"Error generating response: {str(e)}"
    
    def _stream_generate(self, prompt: str, max_tokens: int, temperature: float, 
                        top_p: float) -> Generator[str, None, None]:
        """Stream text generation token by token"""
        try:
            for output in self.model(prompt, max_tokens=max_tokens, temperature=temperature,
                                   top_p=top_p, stop=["</s>", "Human:"], stream=True):
                token = output['choices'][0]['text']
                if token:
                    yield token
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"\n\nError: {str(e)}"
    
    def _format_prompt(self, user_prompt: str) -> str:
        """Format prompt with system instructions"""
        system_prompt = "You are a professional business analyst assistant. Provide structured, actionable insights."
        return f"{system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"
    
    def _mock_response(self, prompt: str, stream: bool = False) -> Union[str, Generator[str, None, None]]:
        """Mock response when model not loaded"""
        mock_text = f"""[DEMO MODE - Model not loaded]

Your query: "{prompt[:100]}..."

This is a demo response. To enable real LLM:
1. Install: pip install llama-cpp-python
2. Download model: python scripts/download_model.py
3. Restart server

Currently running in DEMO mode."""
        
        if stream:
            import time
            for word in mock_text.split():
                yield word + " "
                time.sleep(0.01)
        else:
            return mock_text
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded model"""
        return {
            "loaded": self.model_loaded,
            "model_path": self.config.get("MODEL_PATH", "Not set"),
            "context_length": self.config.get("MODEL_CONTEXT_LENGTH", 2048),
            "threads": self.config.get("MODEL_THREADS", 4),
            "llama_cpp_available": LLAMA_CPP_AVAILABLE
        }
