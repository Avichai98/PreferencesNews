import requests
from dapr.ext.fastapi import DaprApp
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from preference_model import PreferencesModel
from news_function import news_data_api, gemini_api

app = FastAPI()
dapr_app = DaprApp(app)


# Dapr subscription route
@dapr_app.subscribe(pubsub='newspubsub', topic='news_requests')
async def news_requests_subscriber(request: Request):
    try:
        # Extract data from the request body (Dapr envelope)
        event = await request.json()
        preferences_data = event.get("data")  # Extract the actual `PreferencesModel` payload

        # Parse `data` into PreferencesModel
        preferences = PreferencesModel(**preferences_data)
        print(preferences)  # Log incoming preferences

        # Process preferences
        categories = preferences.categories
        response_news = news_data_api(categories, preferences.language)  # Get news from the API
        if not response_news:
            return {"message": "No news found for the given categories."}
        response_ai_api = gemini_api(response_news)  # Filter the news by AI

        platforms = preferences.platforms
        telegram_response = None

        if 'email' in platforms:
            print("Sending email")
            # Uncomment and configure your email service as needed
            # email_response = requests.post(
            #     'http://notification_service:8002/email_notification',
            #     json={'news': response_ai_api.text, 'email': preferences.email}
            # )
            # email_response.raise_for_status()

        if 'Telegram' in platforms:
            print("Sending Telegram")
            telegram_response = requests.post(
                'http://notification_service:8002/telegram_notification',
                json={'news': response_ai_api.text, 'telegram_id': preferences.telegram_id}
            )
            telegram_response.raise_for_status()

        if not telegram_response:
            raise HTTPException(status_code=404, detail="No Telegram found.")
        else:
            print(telegram_response.json())
            return telegram_response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Send the news
@app.post("/news")
async def post_news(preferences: PreferencesModel):
    categories = preferences.categories
    response_news = news_data_api(categories, preferences.language)  # Get news from the API
    if not response_news:
        return {"message": "No news found for the given categories."}
    response_ai_api = gemini_api(response_news)  # filter the news by AI
    try:
        platforms = preferences.platforms
        email_response = ''
        telegram_response = ''

        if 'email' in platforms:
            print("Sending email")
            # email_response = requests.post('http://notification_service:8002/email_notification',
            #                              json={'news': response_ai_api.text, 'email': preferences.email})
            # email_response.raise_for_status()  # Raise HTTPError for bad responses

        if 'Telegram' in platforms:
            print("Sending telegram")
            telegram_response = requests.post('http://notification_service:8002/telegram_notification',
                                              json={'news': response_ai_api.text,
                                                    'telegram_id': preferences.telegram_id})
            telegram_response.raise_for_status()

        if 'Telegram' not in platforms:
            return HTTPException(status_code=404, detail="No telegram found.")
        else:
            print(telegram_response.json())
            return telegram_response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
