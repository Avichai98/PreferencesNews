import requests
from fastapi import FastAPI, HTTPException
from preference_model import PreferencesModel
from news_function import news_data_api, gemini_api

app = FastAPI()


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
