from fastapi import FastAPI, Request
from redis_conn import redis_client
import logging
app = FastAPI()

logger = logging.getLogger(__name__)

@app.post("/expire_cache/")
async def expire_cache(request: Request):
    try:
        data = await request.json()
        cache_key = data.get("cache_key")
        if not cache_key:
            return {"status": "error", "message": "no cache_key provide"}
        if not redis_client:
            return {"status": "error", "message": " redis_client not available"}
    
        result = redis_client.delete(cache_key)
        if result:
            logger.info(f"Cache key '{cache_key}' expired successfully")
            return {"status": "success", "message": f"Cache key '{cache_key}' expired successfully"}
        else:
            return {"status": "warning", "message": f"Cache key '{cache_key}' not found"}
        
    except Exception as e:
        logger.error(f"Cache expiry error: {e}")
        return {"status": "error", "message": f"Cache expiry failed: {str(e)}"}
    
@app.get("/health")
async def health_check():
    redis_status = "connected" if redis_client else "disconnected"
    return {"status": "health", "message": redis_status}



