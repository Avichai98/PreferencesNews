from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel
from authentication_model import AuthenticationModel
from preference_model import PreferencesModel
from user_function import get_user_by_email, save_user, update_user_preferences, \
    verify_user_credentials, get_all_users, delete_user_by_email

app = FastAPI()

DAPR_HTTP_PORT = 3500  # Dapr sidecar HTTP port
PUBSUB_NAME = 'rabbitmq-pubsub'  # Name of the pub/sub Component
TOPIC_NAME = 'news_requests'  # Topic to publish news requests


class NewsRequest(BaseModel):
    email: str


@app.post("/user/news")
async def request_news(preferences: PreferencesModel):
    try:
        data = preferences.model_dump()
        response = requests.post(f"http://news_manager:8001/news", json=data)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/user/news1")
async def request_news(request: NewsRequest):
    """
    Publish a news request to the 'news_requests' topic asynchronously using DaprClient.
    """
    try:
        async with DaprClient() as client:
            # Publish the message to the specified topic
            await client.publish_event(
                pubsub_name=PUBSUB_NAME,
                topic_name=TOPIC_NAME,
                data=request.email  # Payload to send
            )
        return {"status": "accepted", "message": "News request published successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish news request: {str(e)}")


@app.post("/user/register")
def register_user(user: AuthenticationModel):
    # Check if user already exists
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    else:
        # Initialize preferences with default values
        preferences = {
            "categories": ["Sports"],
            "language": "en",
            "platforms": ["Telegram"],
            "email": user.email,
            "telegram_id": 0
        }
        # Save the user
        user_data = user.model_dump()  # Convert Pydantic model to dictionary
        user_data["preferences"] = preferences  # Add preferences to the user data
        _id = save_user(user_data)
        return {"message": "User created successfully", "email": user_data.get('email'), "_id": _id}


@app.put("/user/preferences/{email}")
def update_preferences(email: str, preferences: PreferencesModel):
    # Convert Pydantic model to dictionary
    preferences_data = preferences.model_dump()

    # Update preferences in the database
    update_user_preferences(email, preferences_data)
    return {"message": "Preferences updated successfully"}


@app.post("/user/login")
def login_user(user: AuthenticationModel):
    # Verify credentials
    user_data = verify_user_credentials(user.email, user.password)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "message": "Login successful",
        "user": {
            "id": str(user_data['_id']),
            "email": str(user_data['email']),
            "preferences": user_data.get('preferences', [])
        }
    }


@app.get("/user/logout")
def logout_user():
    return {"message": "Logout successful"}


@app.get("/user/{email}")
async def get_user(email: str):
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        return {
            "message": "Login successful",
            "user": user
        }


@app.get("/admin/users")
def get_users():
    users = get_all_users()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return {"users": users}


@app.delete("/admin/users/{email}")
def delete_user(email: str):
    result = delete_user_by_email(email)
    if not result:
        raise HTTPException(status_code=404, detail="No users found")

    return {"message": "User deleted successfully"}
