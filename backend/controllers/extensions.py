from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_caching import Cache
import redis
import logging

logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

redis_client = None

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
        "CACHE_REDIS_SOCKET_TIMEOUT": 5,
        "CACHE_REDIS_SOCKET_CONNECT_TIMEOUT": 5
    }
    
    logger.info(f"Initializing cache with config: {cache_config}")
    
    try:
        cache.init_app(app, config=cache_config)
        
        if app.config.get("CACHE_TYPE", "").lower() == "redis":
            try:
                redis_client = redis.Redis(
                    host=app.config.get("REDIS_HOST", "localhost"),
                    port=app.config.get("REDIS_PORT", 6379),
                    db=app.config.get("REDIS_DB", 0),
                    decode_responses=True,  
                    socket_timeout=5,  
                    socket_connect_timeout=5
                )
                
                redis_client.ping()
                logger.info("Redis connection successful")
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
                redis_client = None
                logger.error(f"Redis connection error: {str(e)}")
                
                app.config['CACHE_TYPE'] = 'SimpleCache'
                cache.init_app(app)
                logger.warning("Falling back to SimpleCache as Redis is unavailable")
            except Exception as e:
                redis_client = None
                logger.error(f"Unexpected Redis error: {str(e)}")
                
                app.config['CACHE_TYPE'] = 'SimpleCache'
                cache.init_app(app)
                logger.warning("Falling back to SimpleCache due to unexpected error")
        else:
            logger.info(f"Using non-Redis cache: {app.config.get('CACHE_TYPE')}")
            
    except Exception as e:
        logger.error(f"Error initializing cache: {str(e)}")
        
        app.config['CACHE_TYPE'] = 'SimpleCache'
        cache = Cache(app, config={"CACHE_TYPE": "SimpleCache"})
        logger.warning("Falling back to SimpleCache due to initialization error")
    
    return cache