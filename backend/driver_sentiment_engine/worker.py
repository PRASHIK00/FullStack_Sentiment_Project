import os
from redis import Redis
from rq import Worker, Queue
from . import database, models
# 1. Import your services (Logic)
from .services import FeedbackProcessor, AISentimentAnalyzer, AlertingService

# 2. Queue name (must match queue.py)
listen = ['feedback']

REDIS_CONN_STR = os.environ.get("REDIS_URL", "redis://localhost:6379")

# --- INITIALIZE THE BRAIN (GLOBAL) ---
print("Worker: Loading AI Model...")
analyzer = AISentimentAnalyzer()
alerter = AlertingService()
processor = FeedbackProcessor(analyzer=analyzer, alerter=alerter)

def run_feedback_processing_job(submission: models.GenericFeedbackSubmission, *args):
    """
    This function is called by RQ when a message arrives.
    """
    print(f"WORKER: Received job for {submission.entity_type} {submission.entity_id}")

    try:
        # 3. Use the global processor
        processor.process_feedback(submission)
        print(f"WORKER: Successfully processed job for {submission.entity_id}")

    except Exception as e:
        print(f"WORKER: FAILED job. Error: {e}")

if __name__ == '__main__':
    # 4. Connect to Redis and Start Listening
    try:
        redis_conn = Redis.from_url(REDIS_CONN_STR)
        
        # FIX: We create the Queue objects manually with the connection
        # This avoids using the 'Connection' class that caused your error
        queues = [Queue(name, connection=redis_conn) for name in listen]
        
        print(f"Worker listening on queues: {listen}")
        
        # Pass the connection directly to the worker
        worker = Worker(queues, connection=redis_conn)
        worker.work()

    except Exception as e:
        print(f"CRITICAL: Worker failed to start. Redis error: {e}")