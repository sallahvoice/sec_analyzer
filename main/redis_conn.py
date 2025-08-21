import redis
import logging
logger = logging.getLogger(__name__)

try:
    redis_client = redis.Redis(host="localhost",port=6379,db=0, decode_responses=False)
    redis_client.ping()
    logger.info("Redis connected successfully")
except redis.ConnectionError as e:
    logger.exception("redis.ConnectionError")
    redis_client = None