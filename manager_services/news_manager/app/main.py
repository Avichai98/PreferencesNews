import json
from dapr.clients import DaprClient
from dapr.ext.fastapi import DaprApp
from fastapi import FastAPI, HTTPException, Request
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

            data = {
                'news': response_ai_api.text,  # Assuming response_ai_api.text is the news content
                'telegram_id': preferences.telegram_id  # Example data from user preferences
            }

            # Publish the notification data using Dapr PubSub
            with DaprClient() as client:
                try:
                    result = client.publish_event(
                        pubsub_name='notificationpubsub',  # Your pubsub component
                        topic_name='notification_requests',  # Topic to publish to
                        data=json.dumps(data),  # Data to send (it will be serialized automatically)
                        data_content_type='application/json',  # Ensure content type is set to JSON
                    )
                    print("Event published successfully:", result)
                except Exception as e:
                    print("Error publishing event:", e)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
