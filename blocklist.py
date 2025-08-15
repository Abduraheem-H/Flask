import os
import redis
from datetime import timedelta


redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST", "redis-server"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True,
)

BLOCKLIST_KEY = "jwt_blocklist"


def add_to_blocklist(jti: str, expires_in: int):
    """Store the JWT's jti in Redis with an expiry time."""
    redis_client.setex(f"{BLOCKLIST_KEY}:{jti}", timedelta(seconds=expires_in), "true")


def is_token_revoked(jti: str) -> bool:
    """Check if the JWT's jti is in Redis."""
    return redis_client.exists(f"{BLOCKLIST_KEY}:{jti}") == 1
