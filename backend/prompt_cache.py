"""
Prompt Prefix Cache
Implements RadixAttention-style caching for common prompt prefixes
Tier 1 optimization for MicroLLM-PrivateStack
"""

import hashlib
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class CachedPromptState:
    """Represents a cached prompt prefix state"""
    prompt_hash: str
    prefix: str
    tokens: List[int]
    timestamp: float
    hit_count: int = 0


class PromptPrefixCache:
    """
    Cache for common prompt prefixes to avoid recomputation.
    
    Example use cases:
    - System prompts
    - Common conversation starters  
    - Repeated query patterns
    """
    
    def __init__(self, max_entries: int = 100, ttl_seconds: int = 3600):
        self.cache: Dict[str, CachedPromptState] = {}
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        
        # Statistics
        self.hits = 0
        self.misses = 0
        
        logger.info(f"PromptPrefixCache initialized: max_entries={max_entries}, ttl={ttl_seconds}s")
    
    def _hash_prefix(self, prefix: str) -> str:
        """Generate hash for prefix"""
        return hashlib.sha256(prefix.encode()).hexdigest()[:16]
    
    def get(self, prompt: str, check_prefix_length: int = 50) -> Optional[CachedPromptState]:
        """
        Check if prompt has a cached prefix.
        
        Args:
            prompt: Full prompt text
            check_prefix_length: Number of characters to check for prefix match
            
        Returns:
            CachedPromptState if cache hit, None otherwise
        """
        # Extract prefix
        prefix = prompt[:check_prefix_length]
        prefix_hash = self._hash_prefix(prefix)
        
        # Check cache
        if prefix_hash in self.cache:
            cached = self.cache[prefix_hash]
            
            # Check TTL
            if time.time() - cached.timestamp > self.ttl_seconds:
                del self.cache[prefix_hash]
                self.misses += 1
                return None
            
            # Cache hit
            cached.hit_count += 1
            self.hits += 1
            
            logger.debug(f"Prompt prefix cache HIT: '{prefix[:30]}...' (hits: {cached.hit_count})")
            return cached
        
        self.misses += 1
        return None
    
    def set(self, prompt: str, tokens: List[int], check_prefix_length: int = 50):
        """
        Cache a prompt prefix with its tokenized form.
        
        Args:
            prompt: Full prompt text
            tokens: Tokenized form
            check_prefix_length: Number of characters to cache as prefix
        """
        # Evict old entries if cache is full
        if len(self.cache) >= self.max_entries:
            self._evict_lru()
        
        prefix = prompt[:check_prefix_length]
        prefix_hash = self._hash_prefix(prefix)
        
        self.cache[prefix_hash] = CachedPromptState(
            prompt_hash=prefix_hash,
            prefix=prefix,
            tokens=tokens,
            timestamp=time.time(),
            hit_count=0
        )
        
        logger.debug(f"Prompt prefix cached: '{prefix[:30]}...'")
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.cache:
            return
        
        # Find oldest entry
        oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].timestamp)
        del self.cache[oldest_key]
        logger.debug(f"Evicted LRU cache entry: {oldest_key}")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_entries": self.max_entries,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_pct": round(hit_rate, 2),
            "entries": [
                {
                    "prefix": state.prefix[:30] + "...",
                    "hit_count": state.hit_count,
                    "age_seconds": int(time.time() - state.timestamp)
                }
                for state in sorted(self.cache.values(), key=lambda s: s.hit_count, reverse=True)[:5]
            ]
        }
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Prompt prefix cache cleared")


# Global cache instance
_prompt_cache: Optional[PromptPrefixCache] = None


def get_prompt_cache() -> PromptPrefixCache:
    """Get or create global prompt cache instance"""
    global _prompt_cache
    if _prompt_cache is None:
        _prompt_cache = PromptPrefixCache()
    return _prompt_cache
