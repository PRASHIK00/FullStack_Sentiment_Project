import os
import datetime
from pymongo import MongoClient, UpdateOne, errors
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from typing import Optional, Any, Dict, List
from .models import UiConfig
from .auth import UserInDB

#  Database Connection
try:
    MONGO_CONN_STR = os.environ.get("MONGO_CONN_STR",
                                    "mongodb://localhost:27017/")
    client = MongoClient(MONGO_CONN_STR)
    client.admin.command('ping')
    db = client.sentiment_db
    driver_stats_collection = db.driver_stats
    processed_trips_collection = db.processed_trips
    users_collection = db.users
    ui_config_collection = db.ui_config
    marshal_stats_collection = db.marshal_stats
    trip_feedback_collection = db.trip_feedback
    app_feedback_collection = db.app_feedback

    processed_trips_collection.create_index("trip_id", unique=True)
    users_collection.create_index("username", unique=True)
    driver_stats_collection.create_index("driver_id", unique=True)
    marshal_stats_collection.create_index("marshal_id", unique=True)

    print("Connected to MongoDB successfully!")
except ConnectionFailure as e:
    print(f"Could not connect to MongoDB: {e}")
    client = None
    db = None
    driver_stats_collection = None
    processed_trips_collection = None
    users_collection = None
    ui_config_collection = None
    marshal_stats_collection = None
    trip_feedback_collection = None
    app_feedback_collection = None

# EMA Settings
EMA_ALPHA = 0.1


#  Idempotency
def check_and_mark_trip(trip_id: str) -> bool:
    if not trip_id: return True
    if processed_trips_collection is None: return True
    try:
        processed_trips_collection.insert_one({
            'trip_id':
            trip_id,
            'processed_at':
            datetime.datetime.now(datetime.UTC)
        })
        print(f"IDEMPOTENCY: New trip {trip_id}. Marked for processing.")
        return True
    except errors.DuplicateKeyError:
        print(f"IDEMPOTENCY: Duplicate trip {trip_id}. Skipping job.")
        return False
    except Exception as e:
        print(f"ERROR: Could not check/mark trip_id {trip_id}: {e}")
        return True


# Generic Stats Updaters
def _update_scored_entity_stats(collection: Any, entity_id_field: str,
                                entity_id: str,
                                new_score: float) -> Optional[float]:
    if collection is None: return None
    doc = collection.find_one({entity_id_field: entity_id})
    if doc:
        old_avg = doc['average_score']
        new_avg = (EMA_ALPHA * new_score) + ((1 - EMA_ALPHA) * old_avg)
        new_count = doc['feedback_count'] + 1
        collection.update_one(
            {entity_id_field: entity_id},
            {'$set': {
                'average_score': new_avg,
                'feedback_count': new_count
            }})
    else:
        new_avg = new_score
        new_count = 1
        collection.insert_one({
            entity_id_field: entity_id,
            'average_score': new_avg,
            'feedback_count': new_count
        })
    return new_avg


# Specific Stats Functions
def update_driver_stats(entity_id: str, new_score: float):
    return _update_scored_entity_stats(collection=driver_stats_collection,
                                       entity_id_field="driver_id",
                                       entity_id=entity_id,
                                       new_score=new_score)


def update_marshal_stats(entity_id: str, new_score: float):
    return _update_scored_entity_stats(collection=marshal_stats_collection,
                                       entity_id_field="marshal_id",
                                       entity_id=entity_id,
                                       new_score=new_score)


def save_simple_feedback(collection: Any, data: Dict[str, Any]):
    if collection is None: return
    collection.insert_one(data)


# Stats Getters
def get_driver_stats(driver_id: str):
    if driver_stats_collection is None: return None
    return driver_stats_collection.find_one({'driver_id': driver_id},
                                            {'_id': 0})


def get_marshal_stats(marshal_id: str):
    if marshal_stats_collection is None: return None
    return marshal_stats_collection.find_one({'marshal_id': marshal_id},
                                             {'_id': 0})


# Config Getter
def get_ui_config() -> Optional[UiConfig]:
    if ui_config_collection is None: return None
    config_doc = ui_config_collection.find_one()
    if config_doc:
        return UiConfig(**config_doc)
    else:
        print("ERROR: No UI config found in database!")
        return None


# User Auth Function
def get_user_from_db(username: str) -> Optional[UserInDB]:
    if users_collection is None: return None
    user_data = users_collection.find_one({"username": username})
    if user_data:
        return UserInDB(**user_data)
    return None


# Admin Dashboard Functions
def get_all_driver_stats() -> List[Dict[str, Any]]:
    if driver_stats_collection is None: return []
    return list(driver_stats_collection.find({}, {'_id': 0}))


def get_all_marshal_stats() -> List[Dict[str, Any]]:
    if marshal_stats_collection is None: return []
    return list(marshal_stats_collection.find({}, {'_id': 0}))


def get_recent_trip_feedback(limit: int = 50) -> List[Dict[str, Any]]:
    if trip_feedback_collection is None: return []
    return list(
        trip_feedback_collection.find({}, {
            '_id': 0
        }).sort("created_at", -1).limit(limit))


def get_recent_app_feedback(limit: int = 50) -> List[Dict[str, Any]]:
    if app_feedback_collection is None: return []
    return list(
        app_feedback_collection.find({}, {
            '_id': 0
        }).sort("created_at", -1).limit(limit))
