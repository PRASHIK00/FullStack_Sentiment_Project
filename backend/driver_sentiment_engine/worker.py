from . import models, database, queue
from .services import FeedbackProcessor, RuleBasedAnalyzer, AlertingService


# Worker Function
def run_feedback_processing_job(submission: models.GenericFeedbackSubmission,
                                processor: FeedbackProcessor):

    print(
        f"WORKER: Received job for {submission.entity_type} {submission.entity_id}"
    )
    try:
        # The processor now contains all the router logic
        processor.process_feedback(submission)

        print(f"WORKER: Successfully processed job for {submission.entity_id}")
    except Exception as e:
        print(f"WORKER: FAILED job for {submission.entity_id}. Error: {e}")
        raise  # Re-raise exception to mark job as failed in RQ


#  Worker Initialization (for when this file is run directly) 
def main():
    
    print("Feedback worker components initialized (MongoDB).")
    #


if __name__ == "__main__":
    print("Initializing worker...")
