import os
from redis import Redis
from rq import Queue

REDIS_CONN_STR = os.environ.get("REDIS_URL", "redis://localhost:6379")

try:
    #  Redis connection
    redis_conn = Redis.from_url(REDIS_CONN_STR)
    redis_conn.ping()
    print("Connected to Redis successfully!")

    # Create the feedback queue
    feedback_queue = Queue("feedback", connection=redis_conn)

except Exception as e:
    print(f"Could not connect to Redis: {e}")
    redis_conn = None
    feedback_queue = None
