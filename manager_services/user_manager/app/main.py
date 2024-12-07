import json
from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException
from authentication_model import AuthenticationModel
from preference_model import PreferencesModel
from user_function import get_user_by_email, save_user, update_user_preferences, \
    verify_user_credentials, get_all_users, delete_user_by_email

app = FastAPI()


@app.post("/user/news")
async def request_news(preferences: PreferencesModel):
    try:
        data = preferences.model_dump()

        # Publish the preferences data using Dapr PubSub
        with DaprClient() as client:
            result = client.publish_event(
                pubsub_name='newspubsub',  # Your pubsub component
                topic_name='news_requests',  # Topic to publish to
                data=json.dumps(data),  # Convert data to JSON
                data_content_type='application/json',  # Content type
            )
        print(data)
        print(json.dumps(data))  # To debug the structure of the published message

        return f' message": "Event published successfully", "status": {result}, data: {data}'
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
