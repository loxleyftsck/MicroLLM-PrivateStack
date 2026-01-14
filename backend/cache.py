# Redis Cache Configuration for MicroLLM-PrivateStack
# Phase 2 - Performance Optimization

from functools import wraps
import hashlib
import json
import redis
import os

class LLMCache:
    """
    Redis-based caching for LLM responses
    Provides instant responses for frequently asked questions
    """
    
    def __init__(self, host='localhost', port=6379, db=0, ttl=3600):
        """
        Initialize Redis cache
        
        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            ttl: Time to live in seconds (default: 1 hour)
        """
        self.enabled = os.getenv('REDIS_ENABLED', 'False').lower() == 'true'
        self.ttl = ttl
        
        if self.enabled:
            try:
                self.redis_client = redis.Redis(
                    host=host,
                    port=port,
                    db=db,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                # Test connection
                self.redis_client.ping()
                print(f"✅ Redis cache connected: {host}:{port}")
            except Exception as e:
                print(f"⚠️  Redis cache disabled: {e}")
                self.enabled = False
        else:
            print("ℹ️  Redis cache disabled (set REDIS_ENABLED=true to enable)")
            self.redis_client = None
    
    def _generate_key(self, prompt, **kwargs):
        """Generate cache key from prompt and parameters"""
        cache_data = {
            'prompt': prompt,
            **kwargs
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return f"llm:{hashlib.sha256(cache_string.encode()).hexdigest()}"
    
    def get(self, prompt, **kwargs):
        """
        Get cached response
        
        Returns:
            Cached response or None if not found
        """
        if not self.enabled:
            return None
        
        try:
            key = self._generate_key(prompt, **kwargs)
            cached = self.redis_client.get(key)
            
            if cached:
                print(f"🎯 Cache HIT: {prompt[:50]}...")
                return json.loads(cached)
            
            return None
        except Exception as e:
            print(f"⚠️  Cache get error: {e}")
            return None
    
    def set(self, prompt, response, **kwargs):
        """
        Cache a response
        
        Args:
            prompt: User prompt
            response: LLM response to cache
            **kwargs: Additional parameters that affect caching
        """
        if not self.enabled:
            return
        
        try:
            key = self._generate_key(prompt, **kwargs)
            value = json.dumps(response)
            self.redis_client.setex(key, self.ttl, value)
            print(f"💾Cache SET: {prompt[:50]}...")
        except Exception as e:
            print(f"⚠️  Cache set error: {e}")
    
    def invalidate(self, pattern='llm:*'):
        """
        Invalidate cache entries matching pattern
        
        Args:
            pattern: Redis key pattern (default: all LLM caches)
        """
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                print(f"🗑️  Invalidated {deleted} cache entries")
                return deleted
            return 0
        except Exception as e:
            print(f"⚠️  Cache invalidation error: {e}")
            return 0
    
    def stats(self):
        """Get cache statistics"""
        if not self.enabled:
            return {
                'enabled': False,
                'message': 'Redis cache is disabled'
            }
        
        try:
            info = self.redis_client.info()
            keys_count = len(self.redis_client.keys('llm:*'))
            
            return {
                'enabled': True,
                'connected': True,
                'total_keys': keys_count,
                'used_memory': info.get('used_memory_human', 'N/A'),
                'uptime_days': info.get('uptime_in_days', 0),
                'hit_rate': 'Available in Redis stats'
            }
        except Exception as e:
            return {
                'enabled': True,
                'connected': False,
                'error': str(e)
            }


def cached_llm_response(cache_instance, ttl=3600):
    """
    Decorator for caching LLM responses
    
    Usage:
        @cached_llm_response(cache, ttl=7200)
        def generate_response(prompt, max_tokens=256):
            # ... LLM inference ...
            return response
    """
    def decorator(func):
        @wraps(func)
        def wrapper(prompt, *args, **kwargs):
            # Try to get from cache
            cache_key_params = {
                'max_tokens': kwargs.get('max_tokens', 256),
                'temperature': kwargs.get('temperature', 0.7)
            }
            
            cached = cache_instance.get(prompt, **cache_key_params)
            if cached:
                return cached
            
            # Generate new response
            response = func(prompt, *args, **kwargs)
            
            # Cache the response
            cache_instance.set(prompt, response, **cache_key_params)
            
            return response
        
        return wrapper
    return decorator


# Example integration with LLM engine
if __name__ == "__main__":
    # Test cache
    cache = LLMCache()
    
    # Test set/get
    cache.set("What is AI?", "AI is artificial intelligence...")
    result = cache.get("What is AI?")
    print(f"Cached result: {result}")
    
    # Test stats
    stats = cache.stats()
    print(f"Cache stats: {stats}")
