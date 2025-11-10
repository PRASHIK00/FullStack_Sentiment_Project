from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime
import uuid


# Config Models
class UiFeature(BaseModel):
    key: str
    label: str
    enabled: bool


class UiConfig(BaseModel):
    title: str
    features: List[UiFeature]


# Auth Models
class UserSignup(BaseModel):
    username: str
    password: str


# Feedback Models
class EntityType(str, Enum):
    DRIVER = "DRIVER"
    MARSHAL = "MARSHAL"
    APP = "APP"
    TRIP = "TRIP"


class GenericFeedbackBody(BaseModel):
    entity_type: EntityType
    entity_id: str
    feedback_text: str
    trip_id: Optional[str] = None


class GenericFeedbackSubmission(BaseModel):
    user_id: str
    entity_type: EntityType
    entity_id: str
    feedback_text: str
    trip_id: Optional[str] = None


# Stats Models
class DriverStat(BaseModel):
    driver_id: str
    average_score: float
    feedback_count: int


class MarshalStat(BaseModel):
    marshal_id: str
    average_score: float
    feedback_count: int


# DB Storage Models (for Admin)


class TripFeedback(BaseModel):
    user_id: str
    entity_type: str
    entity_id: str
    feedback_text: str
    trip_id: Optional[str]
    score: Optional[float] = None
    created_at: datetime


class AppFeedback(BaseModel):
    user_id: str
    entity_type: str
    entity_id: str
    feedback_text: str
    trip_id: Optional[str]
    created_at: datetime
