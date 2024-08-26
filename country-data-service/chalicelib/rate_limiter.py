import os
from redis import Redis
from functools import wraps
from chalice import ChaliceViewError
from chalice import Chalice
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger()

class RateLimitExceededError(ChaliceViewError):
    default_message = 'Rate Limit Exceeded.'

    def __init__(self):
        super().__init__(self.default_message)


class RateLimiter:
    def __init__(self, app: Chalice, rate_limits: dict):
        self.route = app
        self.rate_limits = rate_limits
        redis_host = os.environ.get('REDIS_HOST', 'localhost')
        redis_port = int(os.environ.get('REDIS_PORT', 6379))
        try:
            self.redis_client = Redis(host=redis_host, port=redis_port)
            self.redis_client.ping()

            logger.info("Redis client initialized successfully.")
        except:
            logger.warning("Redis not available. Rate limiting will be disabled.")
            self.redis_client = None

    def limit(self):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if self.redis_client is None:
                    return func(*args, **kwargs)
                
                endpoint = func.__name__
                limit_config = self.rate_limits.get(endpoint)
                if not limit_config:
                    logger.warning(f"No rate limit configuration found for endpoint: {endpoint}")
                    return func(*args, **kwargs)

                current_request = self.route.current_request
                user_id = current_request.context.get('identity', {}).get('sourceIp', 'unknown')
                redis_key = f"throttling-{user_id}-{endpoint}"

                if self.request_is_limited(redis_key, limit_config['limit'], int(limit_config['period'].total_seconds())):
                    raise RateLimitExceededError()
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def request_is_limited(self, redis_key: str, limit: int, period_in_seconds: int) -> bool:
        if self.redis_client is None:
            return False
        try:
            logger.info(f"Checking rate limit for key: {redis_key}")
            current = self.redis_client.get(redis_key)

            if current is None:
                logger.info(f"Setting rate limit for key: {redis_key}")
                self.redis_client.set(redis_key, 1, ex=period_in_seconds)
                return False

            if int(current) >= limit:
                logger.info(f"Rate limit exceeded for key: {redis_key}")
                return True

            self.redis_client.incr(redis_key)
            logger.info(f"Incrementing key: {redis_key}")

            return False
        except Exception as e:
            logger.error(f"Error accessing Redis: {e}")
            return False
