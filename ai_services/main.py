from fastapi import FastAPI
from pydantic import BaseModel
from sentiment_engine import SentimentEngine

app = FastAPI()

engine = SentimentEngine()


class FeedbackRequest(BaseModel):
    text: str

@app.post("/analyze")
async def analyze_feedback(request: FeedbackRequest):
    analysis = engine.analyze(request.text)
    return analysis