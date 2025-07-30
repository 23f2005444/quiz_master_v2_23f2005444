import functools
import time
import logging
from flask import request, jsonify
from controllers.extensions import cache, redis_client

# Set up logging
logger = logging.getLogger(__name__)

def rate_limit(limit=30, per=60, by="ip"):
    """
    Rate limiting decorator with fallback when Redis is unavailable
    
    Args:
        limit: Maximum number of requests allowed
        per: Time window in seconds
        by: Rate limit by 'ip' or 'user'
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            # Skip rate limiting if Redis is not available
            if redis_client is None:
                logger.warning(f"Redis client is not available - rate limiting disabled for {func.__name__}")
                return func(*args, **kwargs)
                
            try:
                # Get identifier based on IP or user
                if by == "user" and request.headers.get("Authorization"):
                    # Extract user from JWT token (simplified)
                    identifier = request.headers.get("Authorization")
                else:
                    # Use client IP
                    identifier = request.remote_addr or "unknown"
                    
                # Create a rate limit key
                rate_key = f"ratelimit:{func.__name__}:{identifier}"
                
                # Check if Redis is connected before using pipeline
                if not hasattr(redis_client, 'ping') or not redis_client.ping():
                    logger.warning(f"Redis connection lost - rate limiting disabled for {func.__name__}")
                    return func(*args, **kwargs)
                
                # Use Redis pipeline for atomicity
                pipe = redis_client.pipeline()
                now = time.time()
                pipe.zremrangebyscore(rate_key, 0, now - per)
                pipe.zcard(rate_key)
                pipe.zadd(rate_key, {now: now})
                pipe.expire(rate_key, per)
                _, request_count, _, _ = pipe.execute()
                
                # Check if rate limit exceeded
                if request_count > limit:
                    response = {
                        "error": "Rate limit exceeded",
                        "limit": limit,
                        "per": per,
                        "retry_after": per - (now % per) 
                    }
                    return jsonify(response), 429
            except Exception as e:
                logger.error(f"Error in rate limiting for {func.__name__}: {str(e)}")
            
            return func(*args, **kwargs)
            
        return wrapped
    return decorator


def cached(timeout=300, key_prefix='view', user_specific=False):
    """
    Caching decorator that supports user-specific caching with fallback
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Prefix for cache key
        user_specific: Whether to include user ID in cache key
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            try:
                from flask_jwt_extended import get_jwt_identity
                
                # Build cache key
                cache_key = f"{key_prefix}:{func.__name__}"
                
                arg_strings = [str(arg) for arg in args[1:]]  # Skip self/cls
                kwarg_strings = [f"{k}={v}" for k, v in kwargs.items()]
                args_key = "_".join(arg_strings + kwarg_strings)
                
                if args_key:
                    cache_key = f"{cache_key}:{args_key}"
                    
                if user_specific:
                    try:
                        user_id = get_jwt_identity()
                        if user_id:
                            cache_key = f"{cache_key}:user={user_id}"
                    except Exception:
                        logger.debug("Could not get user identity for cache key")
                
                if cache:
                    # Try to get from cache
                    try:
                        cached_result = cache.get(cache_key)
                        if cached_result is not None:
                            return cached_result
                    except Exception as cache_error:
                        logger.error(f"Error retrieving from cache: {str(cache_error)}")
                
                # Generate the response
                result = func(*args, **kwargs)
                
                if cache:
                    try:
                        cache.set(cache_key, result, timeout=timeout)
                    except Exception as cache_error:
                        logger.error(f"Error writing to cache: {str(cache_error)}")
                
                return result
                
            except Exception as e:
                logger.error(f"Unexpected error in cached decorator for {func.__name__}: {str(e)}")
                return func(*args, **kwargs)
            
        return wrapped
    return decorator