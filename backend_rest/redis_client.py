import redis
from django.conf import settings
# redis_client = redis.from_url(
#     settings.REDIS_URL,
#     decode_responses=True
# )
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)