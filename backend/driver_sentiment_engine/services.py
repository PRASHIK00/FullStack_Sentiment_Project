from .models import GenericFeedbackSubmission, EntityType
from . import database
import datetime
from transformers import pipeline


class AISentimentAnalyzer:

    def __init__(self):
        print("Loading AI Brain (DISTILBERT)... This runs once at startup")

        self.pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
              device = -1)

    def analyze(self, text: str) -> float:
        safe_text = text[:512]
        result = self.pipeline(safe_text)[0]
        label = result['label']
        confidence = result['score']

        if label == 'POSITIVE':
            final_score = 3.0 + (2.0 * confidence)
        else:
            final_score = 3.0 - (2.0 * confidence)

        final_score = max(1.0, min(5.0, final_score))

        print(f"AI Analysis: '{safe_text[:30]}...' -> {label} ({confidence:.2f}) -> Stars: {final_score: .2f}")
        return final_score


# Sentiment Analyzer
class RuleBasedAnalyzer:

    def __init__(self):
        self.positive_words = {
            "good", "great", "excellent", "awesome", "love", "best", "fast",
            "helpful"
        }
        self.negative_words = {
            "bad", "terrible", "horrible", "awful", "hate", "worst", "slow",
            "rude"
        }

    def analyze(self, text: str) -> float:
        text_lower = text.lower()
        score = 3.0  # Starts with a neutral score (out of 5)

        for word in self.positive_words:
            if word in text_lower:
                score = 5.0
                break  # A single strong positive word makes it positive

        for word in self.negative_words:
            if word in text_lower:
                score = 1.0
                break  # A single strong negative word makes it negative

        # Simple score logic
        if "not good" in text_lower or "not helpful" in text_lower:
            score = 1.5

        if score == 3.0 and len(text_lower) > 15:
            score = 4.0
        elif score == 3.0:
            score = 3.0

        print(f"Sentiment score: {score:.2f}")
        return score


# Alerting Service
class AlertingService:

    def __init__(self, threshold: float = 2.0):
        self.threshold = threshold

    def check_and_raise_alert(self, entity_type: str, entity_id: str,
                              new_avg_score: float):

        if new_avg_score < self.threshold:
            print(
                f"!!! ALERT: {entity_type} {entity_id} score is low: {new_avg_score:.2f} !!!"
            )
        else:
            print(
                f"INFO: Score for {entity_type} {entity_id} is OK: {new_avg_score:.2f}"
            )


# Feedback Processor
class FeedbackProcessor:

    def __init__(self, analyzer: RuleBasedAnalyzer, alerter: AlertingService):
        self.analyzer = analyzer
        self.alerter = alerter
        self.entity_map = {
            EntityType.DRIVER: database.update_driver_stats,
            EntityType.MARSHAL: database.update_marshal_stats,
        }

    def _process_scored_entity(self, entity_type: EntityType, entity_id: str,
                               score: float, submission_data: dict):

        update_function = self.entity_map.get(entity_type)

        if not update_function:
            print(f"ERROR: No update function for entity type {entity_type}")
            return

        new_avg = update_function(entity_id=entity_id, new_score=score)

        print(f"Processing scored feedback for {entity_type} {entity_id}...")

        if new_avg is not None:
            self.alerter.check_and_raise_alert(entity_type=entity_type.value,
                                               entity_id=entity_id,
                                               new_avg_score=new_avg)

        if entity_type == EntityType.DRIVER:
            database.save_simple_feedback(database.trip_feedback_collection,
                                          submission_data)
        elif entity_type == EntityType.MARSHAL:
            database.save_simple_feedback(database.trip_feedback_collection,
                                          submission_data)

    def _process_simple_entity(self, entity_type: EntityType,
                               submission_data: dict):

        print(f"Processing simple feedback for {entity_type}...")

        if entity_type == EntityType.APP:
            database.save_simple_feedback(database.app_feedback_collection,
                                          submission_data)
        elif entity_type == EntityType.TRIP:
            print("NOTE: Simple TRIP feedback noted.")

    def process_feedback(self, submission: GenericFeedbackSubmission):
        # Check idempotency
        if not database.check_and_mark_trip(submission.trip_id):
            return

        # Prepare data
        submission_data = submission.model_dump()
        submission_data["created_at"] = datetime.datetime.now(datetime.UTC)

        # Handle scored entities
        if submission.entity_type in (EntityType.DRIVER, EntityType.MARSHAL):
            score = self.analyzer.analyze(submission.feedback_text)
            submission_data["score"] = score
            self._process_scored_entity(entity_type=submission.entity_type,
                                        entity_id=submission.entity_id,
                                        score=score,
                                        submission_data=submission_data)

        # 4. Handle simple entities
        elif submission.entity_type in (EntityType.APP, EntityType.TRIP):
            self._process_simple_entity(entity_type=submission.entity_type,
                                        submission_data=submission_data)

        else:
            print(f"ERROR: Unknown entity type: {submission.entity_type}")
