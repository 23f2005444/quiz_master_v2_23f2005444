from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_caching import Cache
import redis
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

# Enhanced Redis client for advanced operations
redis_client = None

# Cache with configurable backend
cache = Cache()

def init_cache(app):
    """Initialize cache with application config"""
    global cache, redis_client
    
    # Configure cache
    cache_config = {
        "CACHE_TYPE": app.config.get("CACHE_TYPE", "redis"),
        "CACHE_REDIS_HOST": app.config.get("REDIS_HOST", "localhost"),
        "CACHE_REDIS_PORT": app.config.get("REDIS_PORT", 6379),
        "CACHE_REDIS_DB": app.config.get("CACHE_REDIS_DB", 0),
        "CACHE_DEFAULT_TIMEOUT": app.config.get("CACHE_TIMEOUT", 300),
        # Add socket connection timeout to avoid hanging
        "CACHE_REDIS_SOCKET_TIMEOUT": 5,
        # Add retry options
        "CACHE_REDIS_SOCKET_CONNECT_TIMEOUT": 5
    }
    
    # Log cache configuration
    logger.info(f"Initializing cache with config: {cache_config}")
    
    try:
        # Initialize cache with the app
        cache.init_app(app, config=cache_config)
        
        # Only initialize Redis client if Redis cache type is specified
        if app.config.get("CACHE_TYPE", "").lower() == "redis":
            # Initialize Redis client for direct access with better error handling
            try:
                redis_client = redis.Redis(
                    host=app.config.get("REDIS_HOST", "localhost"),
                    port=app.config.get("REDIS_PORT", 6379),
                    db=app.config.get("REDIS_DB", 0),
                    decode_responses=True,  # Auto-decode responses to strings
                    socket_timeout=5,  # Socket timeout in seconds
                    socket_connect_timeout=5  # Connection timeout in seconds
                )
                
                # Test Redis connection
                redis_client.ping()
                logger.info("Redis connection successful")
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
                redis_client = None
                logger.error(f"Redis connection error: {str(e)}")
                
                # Fall back to SimpleCache
                app.config['CACHE_TYPE'] = 'SimpleCache'
                cache.init_app(app)
                logger.warning("Falling back to SimpleCache as Redis is unavailable")
            except Exception as e:
                redis_client = None
                logger.error(f"Unexpected Redis error: {str(e)}")
                
                # Fall back to SimpleCache
                app.config['CACHE_TYPE'] = 'SimpleCache'
                cache.init_app(app)
                logger.warning("Falling back to SimpleCache due to unexpected error")
        else:
            logger.info(f"Using non-Redis cache: {app.config.get('CACHE_TYPE')}")
            
    except Exception as e:
        logger.error(f"Error initializing cache: {str(e)}")
        
        # Set up a simple cache if initialization fails
        app.config['CACHE_TYPE'] = 'SimpleCache'
        cache = Cache(app, config={"CACHE_TYPE": "SimpleCache"})
        logger.warning("Falling back to SimpleCache due to initialization error")
    
    return cache