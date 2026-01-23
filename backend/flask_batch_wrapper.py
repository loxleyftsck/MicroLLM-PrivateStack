"""
Flask-Compatible Batch Wrapper
Bridges async batch processor with synchronous Flask endpoints

Uses thread-safe queue and background asyncio event loop
"""

import threading
import asyncio
import uuid
import logging
from typing import Optional
from concurrent.futures import Future

logger = logging.getLogger(__name__)


class FlaskBatchWrapper:
    """
    Flask-compatible wrapper for async batch processor.
    
    Runs batch processor in background thread with asyncio event loop.
    Provides synchronous interface for Flask endpoints.
    """
    
    def __init__(self, batch_processor):
        self.batch_processor = batch_processor
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[threading.Thread] = None
        
        # Start background thread
        self._start_background_loop()
    
    def _start_background_loop(self):
        """Start asyncio event loop in background thread"""
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Start batch processor
            self.loop.run_until_complete(self.batch_processor.start())
            
            # Run forever
            self.loop.run_forever()
        
        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()
        
        # Wait for loop to be ready
        import time
        while self.loop is None:
            time.sleep(0.01)
        
        logger.info("✅ Flask batch wrapper started")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
        timeout: int = 30
    ) -> str:
        """
        Synchronous generate method for Flask.
        
        Args:
            prompt: User prompt
            max_tokens: Max tokens to generate
            temperature: Sampling temperature  
            top_p: Nucleus sampling
            timeout: Request timeout in seconds
            
        Returns:
            Generated text
        """
        request_id = str(uuid.uuid4())
        
        # Schedule async request in background loop
        future = asyncio.run_coroutine_threadsafe(
            self.batch_processor.add_request(
                request_id=request_id,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            ),
            self.loop
        )
        
        # Wait for result (blocks Flask thread but that's OK)
        try:
            response = future.result(timeout=timeout)
            return response
        except Exception as e:
            logger.error(f"Batch request failed: {e}")
            raise
    
    def get_stats(self):
        """Get batch processor statistics"""
        return self.batch_processor.get_stats()
    
    def stop(self):
        """Stop batch processor and background loop"""
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self.batch_processor.stop(),
                self.loop
            ).result(timeout=5)
            
            self.loop.call_soon_threadsafe(self.loop.stop)
        
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("Batch wrapper stopped")
