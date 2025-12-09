from transformers import pipeline


class SentimentEngine:

    def __init__(self):
        print("Loading Ai Model... please wait.")

        self.pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english")

    def analyze(self, text: str) -> dict:
        result = self.pipeline(text)[0]

        label = result['label']
        score = result['score']
        is_confident = score > 0.75

        return {
            "sentiment": label,
            "confident": score,
            "is_reliable": is_confident
        }
