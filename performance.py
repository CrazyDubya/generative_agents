"""
Performance optimizations for generative agents.
Includes caching, async operations, and cost tracking.
"""
import asyncio
import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from functools import wraps
import os
import pickle
from pathlib import Path

from logger_config import get_logger, log_api_call

logger = get_logger('performance')

class APICache:
    """Simple file-based cache for API responses to reduce costs."""
    
    def __init__(self, cache_dir: str = "cache", max_age_hours: int = 24):
        """
        Initialize API cache.
        
        Args:
            cache_dir: Directory to store cache files
            max_age_hours: Maximum age of cached items in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_age = timedelta(hours=max_age_hours)
        
    def _get_cache_key(self, prompt: str, params: Dict[str, Any]) -> str:
        """Generate cache key from prompt and parameters."""
        # Create a deterministic hash of prompt and params
        content = f"{prompt}{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for a given key."""
        return self.cache_dir / f"{cache_key}.cache"
    
    def get(self, prompt: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get cached response if available and not expired.
        
        Args:
            prompt: API prompt
            params: API parameters
            
        Returns:
            Cached response if available, None otherwise
        """
        try:
            cache_key = self._get_cache_key(prompt, params)
            cache_path = self._get_cache_path(cache_key)
            
            if not cache_path.exists():
                return None
            
            # Check if cache is expired
            cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
            if datetime.now() - cache_time > self.max_age:
                cache_path.unlink()  # Remove expired cache
                return None
            
            # Load cached response
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
            
            logger.debug(f"Cache hit for key: {cache_key[:8]}...")
            return cached_data
            
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
            return None
    
    def set(self, prompt: str, params: Dict[str, Any], response: Dict[str, Any]) -> None:
        """
        Cache API response.
        
        Args:
            prompt: API prompt
            params: API parameters
            response: API response to cache
        """
        try:
            cache_key = self._get_cache_key(prompt, params)
            cache_path = self._get_cache_path(cache_key)
            
            with open(cache_path, 'wb') as f:
                pickle.dump(response, f)
            
            logger.debug(f"Cached response for key: {cache_key[:8]}...")
            
        except Exception as e:
            logger.warning(f"Error writing cache: {e}")
    
    def clear_expired(self) -> int:
        """Clear expired cache entries. Returns number of cleared entries."""
        cleared = 0
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if datetime.now() - cache_time > self.max_age:
                    cache_file.unlink()
                    cleared += 1
            
            if cleared > 0:
                logger.info(f"Cleared {cleared} expired cache entries")
                
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
        
        return cleared

# Global cache instance
api_cache = APICache()

class CostTracker:
    """Track API costs and usage."""
    
    def __init__(self):
        """Initialize cost tracker."""
        self.costs_file = Path("api_costs.json")
        self.costs = self._load_costs()
    
    def _load_costs(self) -> Dict[str, Any]:
        """Load existing cost data."""
        if self.costs_file.exists():
            try:
                with open(self.costs_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading costs file: {e}")
        
        return {
            "total_cost": 0.0,
            "daily_costs": {},
            "api_calls": 0,
            "cached_calls": 0
        }
    
    def _save_costs(self) -> None:
        """Save cost data to file."""
        try:
            with open(self.costs_file, 'w') as f:
                json.dump(self.costs, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving costs file: {e}")
    
    def add_cost(self, cost: float, cached: bool = False) -> None:
        """Add cost entry."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if not cached:
            self.costs["total_cost"] += cost
            self.costs["api_calls"] += 1
            
            if today not in self.costs["daily_costs"]:
                self.costs["daily_costs"][today] = 0.0
            self.costs["daily_costs"][today] += cost
        else:
            self.costs["cached_calls"] += 1
        
        self._save_costs()
        
        log_api_call(
            "openai", 
            cost if not cached else 0.0,
            True
        )
    
    def get_daily_cost(self, date: str = None) -> float:
        """Get cost for a specific date (today if None)."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return self.costs["daily_costs"].get(date, 0.0)
    
    def get_total_cost(self) -> float:
        """Get total accumulated cost."""
        return self.costs["total_cost"]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        total_calls = self.costs["api_calls"] + self.costs["cached_calls"]
        cache_rate = (self.costs["cached_calls"] / total_calls * 100) if total_calls > 0 else 0
        
        return {
            "total_cost": self.costs["total_cost"],
            "total_calls": total_calls,
            "api_calls": self.costs["api_calls"],
            "cached_calls": self.costs["cached_calls"],
            "cache_rate": round(cache_rate, 2),
            "daily_cost": self.get_daily_cost(),
            "average_cost_per_call": (
                self.costs["total_cost"] / self.costs["api_calls"] 
                if self.costs["api_calls"] > 0 else 0
            )
        }

# Global cost tracker
cost_tracker = CostTracker()

def cached_api_call(func: Callable) -> Callable:
    """
    Decorator to add caching to API calls.
    
    Args:
        func: Function that makes API calls
        
    Returns:
        Wrapped function with caching
    """
    @wraps(func)
    def wrapper(prompt: str, *args, **kwargs):
        # Extract parameters for cache key
        params = {
            'args': args,
            'kwargs': kwargs,
            'function': func.__name__
        }
        
        # Check cache first
        cached_response = api_cache.get(prompt, params)
        if cached_response is not None:
            cost_tracker.add_cost(0.0, cached=True)
            logger.debug(f"Using cached response for {func.__name__}")
            return cached_response
        
        # Make actual API call
        start_time = time.time()
        response = func(prompt, *args, **kwargs)
        end_time = time.time()
        
        # Estimate cost (rough approximation for GPT-3.5-turbo)
        # This would need to be adjusted based on actual model and pricing
        token_estimate = len(prompt.split()) + len(str(response).split())
        estimated_cost = token_estimate * 0.000002  # Rough estimate
        
        # Cache the response
        api_cache.set(prompt, params, response)
        cost_tracker.add_cost(estimated_cost, cached=False)
        
        logger.info(f"API call to {func.__name__} took {end_time - start_time:.2f}s, estimated cost: ${estimated_cost:.6f}")
        
        return response
    
    return wrapper

async def batch_api_calls(calls: list, max_concurrent: int = 5) -> list:
    """
    Execute multiple API calls concurrently with rate limiting.
    
    Args:
        calls: List of (function, args, kwargs) tuples
        max_concurrent: Maximum concurrent calls
        
    Returns:
        List of results in same order as input
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def call_with_semaphore(func, args, kwargs):
        async with semaphore:
            # Add small delay to respect rate limits
            await asyncio.sleep(0.1)
            return func(*args, **kwargs)
    
    tasks = [
        call_with_semaphore(func, args, kwargs)
        for func, args, kwargs in calls
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

def optimize_file_operations():
    """Optimize file operations by cleaning up temporary files."""
    try:
        # Clean expired cache
        cleared = api_cache.clear_expired()
        
        # Clean up temporary files
        temp_patterns = [
            "*.tmp",
            "*.temp", 
            "*.log.*"  # Old log files
        ]
        
        cleaned_files = 0
        for pattern in temp_patterns:
            for file_path in Path(".").rglob(pattern):
                try:
                    # Only delete files older than 1 day
                    if time.time() - file_path.stat().st_mtime > 86400:
                        file_path.unlink()
                        cleaned_files += 1
                except Exception:
                    pass
        
        logger.info(f"Cleanup completed: {cleared} cache entries, {cleaned_files} temp files")
        
    except Exception as e:
        logger.error(f"Error in cleanup: {e}")

def get_performance_stats() -> Dict[str, Any]:
    """Get comprehensive performance statistics."""
    stats = cost_tracker.get_stats()
    
    # Add cache stats
    cache_files = len(list(api_cache.cache_dir.glob("*.cache")))
    cache_size = sum(f.stat().st_size for f in api_cache.cache_dir.glob("*.cache")) / 1024 / 1024  # MB
    
    stats.update({
        "cache_files": cache_files,
        "cache_size_mb": round(cache_size, 2)
    })
    
    return stats