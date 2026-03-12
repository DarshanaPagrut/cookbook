"""
Redis connection manager with connection pooling.
"""

import redis
import os


class RedisClient:
    """
    Provides Redis connection using connection pool.
    """

    def __init__(self):
        """
        Initialize Redis client with connection pooling.
        """

        pool = redis.ConnectionPool(
            host=os.getenv("REDIS_HOST", "redis"),
            port=6379,
            decode_responses=True,
            max_connections=20
        )

        self.client = redis.Redis(connection_pool=pool)

    def get(self, key):
        """Fetch value from Redis."""
        return self.client.get(key)

    def set(self, key, value, expire=None):
        """Store value in Redis."""
        self.client.set(key, value, ex=expire)

    def delete(self, key):
        """Delete Redis key."""
        self.client.delete(key)