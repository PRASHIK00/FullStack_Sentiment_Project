from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware
from . import models, database, queue, worker, auth
from .services import FeedbackProcessor, RuleBasedAnalyzer, AlertingService, AISentimentAnalyzer
from datetime import timedelta
from typing import List, Dict

# App State & Lifespan
app_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # analyzer = RuleBasedAnalyzer()
    analyzer = AISentimentAnalyzer()
    alerter = AlertingService()
    processor = FeedbackProcessor(analyzer=analyzer, alerter=alerter)
    app_state['feedback_processor'] = processor
    print("FastAPI server starting up with AI Engine...")
    print("NOTE: Make sure your MongoDB and Redis servers are running.")
    print("NOTE: Run the RQ worker in a separate terminal.")
    print("INFO:     Application startup complete.")
    yield
    print("INFO:     Application shutdown...")


app = FastAPI(title="Driver Sentiment Engine", lifespan=lifespan)

# CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_feedback_processor() -> FeedbackProcessor:
    return app_state['feedback_processor']


# Auth Endpoints
@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user_signup: models.UserSignup):
    if database.users_collection is None:
        raise HTTPException(status_code=503, detail="Database not connected")
    existing_user = database.get_user_from_db(user_signup.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username already registered")
    hashed_password = auth.get_password_hash(user_signup.password)
    try:
        database.users_collection.insert_one({
            "username": user_signup.username,
            "hashed_password": hashed_password
        })
        return {
            "message": "User created successfully",
            "username": user_signup.username
        }
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Failed to create user: {e}")


@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = database.get_user_from_db(form_data.username)
    if not user or not auth.verify_password(form_data.password,
                                            user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={
        "sub": user.username,
        "role": user.role
    },
                                            expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


# Application Endpoints
@app.get("/")
def get_root():
    return {"status": "Driver Sentiment Engine is running"}


@app.get("/config", response_model=models.UiConfig)
def get_config():
    config = database.get_ui_config()
    if config:
        return config
    else:
        raise HTTPException(status_code=503,
                            detail="UI Configuration not found in database.")


@app.post("/feedback", status_code=status.HTTP_202_ACCEPTED)
def submit_feedback(
    background_tasks: BackgroundTasks,
    feedback_body: models.GenericFeedbackBody,
    processor: FeedbackProcessor = Depends(get_feedback_processor),
    active_user: auth.ActiveUser = Depends(auth.get_current_user)):
    submission = models.GenericFeedbackSubmission(
        user_id=active_user.username,
        entity_type=feedback_body.entity_type.upper(),
        entity_id=feedback_body.entity_id,
        feedback_text=feedback_body.feedback_text,
        trip_id=feedback_body.trip_id)

    try:
        queue.feedback_queue.enqueue(worker.run_feedback_processing_job,
                                     submission, processor)
        print(
            f"Published {submission.entity_type} feedback for {submission.entity_id} to REDIS queue."
        )
        return {"message": "Feedback received and queued for processing."}

    except Exception as e:
        print(f"ERROR: Failed to enqueue job: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not queue feedback. Redis may be down.")


@app.get("/driver/{driver_id}/stats", response_model=models.DriverStat)
def get_driver_statistics(driver_id: str):
    stats = database.get_driver_stats(driver_id)
    if stats:
        return stats
    else:
        raise HTTPException(status_code=404, detail="Driver stats not found")


@app.get("/marshal/{marshal_id}/stats", response_model=models.MarshalStat)
def get_marshal_statistics(marshal_id: str):
    stats = database.get_marshal_stats(marshal_id)
    if stats:
        return stats
    else:
        raise HTTPException(status_code=404, detail="Marshal stats not found")


# Admin Dashboard Endpoints
admin_router = APIRouter()


@admin_router.get("/stats/drivers", response_model=List[models.DriverStat])
def get_all_drivers():
    """(ADMIN) Get stats for all drivers."""
    return database.get_all_driver_stats()


@admin_router.get("/stats/marshals", response_model=List[models.MarshalStat])
def get_all_marshals():
    """(ADMIN) Get stats for all marshals."""
    return database.get_all_marshal_stats()


@admin_router.get("/feedback/trip", response_model=List[models.TripFeedback])
def get_admin_recent_trip_feedback():
    """(ADMIN) Get the 50 most recent trip feedback entries."""
    return database.get_recent_trip_feedback(limit=50)


@admin_router.get("/feedback/app", response_model=List[models.AppFeedback])
def get_admin_recent_app_feedback():
    """(ADMIN) Get the 50 most recent app feedback entries."""
    return database.get_recent_app_feedback(limit=50)


# Mount the admin router
app.include_router(admin_router,
                   prefix="/admin",
                   tags=["Admin"],
                   dependencies=[Depends(auth.get_current_admin_user)])
