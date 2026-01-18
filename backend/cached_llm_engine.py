"""
Integrated LLM Engine with SoA Semantic Cache
Production-ready integration of SemanticCacheSOA for 3.5x faster lookups

Author: Herald Michain Samuel Theo Ginting
Project: MicroLLM-PrivateStack
"""

import logging
import time
from typing import Optional, Dict, Any, Union, Generator, List

try:
    from .llm_engine import LLMEngine
    from .semantic_cache_soa import SemanticCacheSOA, create_semantic_cache
    logger = logging.getLogger(__name__)
except ImportError:
    # Support running as top-level script or from api_gateway
    from llm_engine import LLMEngine
    from semantic_cache_soa import SemanticCacheSOA, create_semantic_cache
    logger = logging.getLogger("cached_llm_engine")


class CachedLLMEngine:
    """
    LLM Engine with integrated SoA Semantic Cache.
    
    Features:
    - 3.5x faster cache lookups with SoA layout
    - Automatic caching of responses
    - Configurable similarity threshold
    - Performance metrics tracking
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        cache_dimension: int = 768,
        cache_max_entries: int = 10000,
        similarity_threshold: float = 0.95,
        embedding_fn=None,
        redis_client=None
    ):
        """
        Initialize cached LLM engine.
        
        Args:
            config: LLM configuration dict
            cache_dimension: Embedding dimension (768 for sentence-transformers)
            cache_max_entries: Maximum cache entries
            similarity_threshold: Cosine similarity threshold for cache hit
            embedding_fn: Function to generate embeddings (None = hash-based fallback)
            redis_client: Optional Redis client for persistence
        """
        # Initialize LLM engine
        self.llm = LLMEngine(config)
        
        # Initialize SoA semantic cache
        self.cache = create_semantic_cache(
            dimension=cache_dimension,
            max_entries=cache_max_entries,
            similarity_threshold=similarity_threshold,
            embedding_fn=embedding_fn,
            redis_client=redis_client,
            use_soa=True  # Use optimized SoA layout
        )
        
        # Performance metrics
        self.total_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_inference_time_ms = 0
        self.total_cache_time_ms = 0
        
        logger.info("=" * 70)
        logger.info("CachedLLMEngine Initialized")
        logger.info(f"  LLM loaded: {self.llm.model_loaded}")
        logger.info(f"  Cache type: SoA (Struct-of-Arrays)")
        logger.info(f"  Cache capacity: {cache_max_entries} entries")
        logger.info(f"  Similarity threshold: {similarity_threshold}")
        logger.info("=" * 70)
    
    @property
    def model_loaded(self) -> bool:
        """Delegate model_loaded check to underlying LLM engine"""
        return self.llm.model_loaded

    def create_embedding(self, text: str) -> List[float]:
        """Delegate embedding generation to underlying LLM engine"""
        return self.llm.create_embedding(text)

    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = None,
        top_p: float = None,
        stream: bool = False,
        use_cache: bool = True
    ) -> Union[str, Generator[str, None, None]]:
        """
        Generate text with semantic caching.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            stream: Enable streaming output
            use_cache: Whether to use cache (default: True)
            
        Returns:
            Generated text or generator for streaming
        """
        self.total_requests += 1
        start_time = time.perf_counter()
        
        # Try cache lookup
        if use_cache:
            cache_start = time.perf_counter()
            cached_response, similarity = self.cache.get(prompt)
            cache_time_ms = (time.perf_counter() - cache_start) * 1000
            self.total_cache_time_ms += cache_time_ms
            
            if cached_response is not None:
                self.cache_hits += 1
                logger.info(f"🎯 Cache HIT: similarity={similarity:.3f}, time={cache_time_ms:.2f}ms")
                
                if stream:
                    # Convert cached response to stream
                    def cached_stream():
                        for word in str(cached_response).split():
                            yield word + " "
                    return cached_stream()
                else:
                    return cached_response
        
        # Cache miss - run inference
        self.cache_misses += 1
        inference_start = time.perf_counter()
        
        if stream:
            # For streaming, collect full response then cache
            def inference_stream():
                full_response = []
                for token in self.llm.generate(prompt, max_tokens, temperature, top_p, stream=True):
                    full_response.append(token)
                    yield token
                
                # Cache the full response after streaming
                complete_response = "".join(full_response)
                if use_cache:
                    self.cache.set(prompt, complete_response)
                    logger.info(f"💾 Cached streaming response: {len(complete_response)} chars")
            
            return inference_stream()
        else:
            response = self.llm.generate(prompt, max_tokens, temperature, top_p, stream=False)
            inference_time_ms = (time.perf_counter() - inference_start) * 1000
            self.total_inference_time_ms += inference_time_ms
            
            # Cache the response
            if use_cache:
                self.cache.set(prompt, response)
            
            logger.info(f"🔄 Inference completed: {inference_time_ms:.2f}ms, response={len(response)} chars")
            return response
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        
        avg_inference_time = (self.total_inference_time_ms / self.cache_misses) if self.cache_misses > 0 else 0
        avg_cache_time = (self.total_cache_time_ms / total) if total > 0 else 0
        
        return {
            'total_requests': self.total_requests,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate_pct': round(hit_rate, 2),
            'avg_inference_time_ms': round(avg_inference_time, 2),
            'avg_cache_lookup_ms': round(avg_cache_time, 3),
            'llm_loaded': self.llm.model_loaded,
            'cache_entries': self.cache.n_entries,
            'cache_type': 'SoA (Optimized)'
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get combined model and cache info"""
        model_info = self.llm.get_model_info()
        cache_stats = self.cache.stats()
        
        return {
            'model': model_info,
            'cache': cache_stats,
            'performance': self.get_stats()
        }
    
    def clear_cache(self) -> int:
        """Clear the semantic cache"""
        count = self.cache.invalidate()
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_cache_time_ms = 0
        logger.info(f"🗑️ Cache cleared: {count} entries removed")
        return count


# Factory function for easy integration
def create_cached_engine(config: Dict[str, Any], **cache_kwargs) -> CachedLLMEngine:
    """
    Factory function to create CachedLLMEngine.
    
    Usage:
        from backend.cached_llm_engine import create_cached_engine
        
        engine = create_cached_engine(config, similarity_threshold=0.90)
        response = engine.generate("What is machine learning?")
    """
    return CachedLLMEngine(config, **cache_kwargs)


if __name__ == "__main__":
    # Demo usage
    logging.basicConfig(level=logging.INFO)
    
    config = {
        "MODEL_PATH": "../models/deepseek-r1-1.5b-q4.gguf",
        "MODEL_CONTEXT_LENGTH": 512,
        "MODEL_THREADS": 2
    }
    
    print("Creating Cached LLM Engine...")
    engine = create_cached_engine(config, cache_max_entries=100)
    
    print("\nTest 1: First query (cache miss)")
    response1 = engine.generate("Explain machine learning in simple terms")
    print(f"Response: {response1[:100]}...")
    
    print("\nTest 2: Same query (cache hit)")
    response2 = engine.generate("Explain machine learning in simple terms")
    print(f"Response: {response2[:100]}...")
    
    print("\nTest 3: Similar query (may cache hit)")
    response3 = engine.generate("What is machine learning?")
    print(f"Response: {response3[:100]}...")
    
    print("\nPerformance Stats:")
    stats = engine.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
