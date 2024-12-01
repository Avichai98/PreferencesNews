from fastapi import FastAPI, Request
from notification_function import telegram_bot_send_news, send_email

app = FastAPI()


@app.post("/email_notification")
async def notification(request: Request):
    data = await request.json()

    # Send the news
    if send_email(data):
        print("News sent successfully!")
        return "News sent successfully!"
    else:
        print("Failed to send news")
        return "Failed to send news"


@app.post("/telegram_notification")
async def telegram_notification(request: Request):
    data = await request.json()

    # Send the news
    try:
        response = telegram_bot_send_news(data)
        print(response)
        if response.status_code == 200:
            print(f"News sent successfully!")
            return response.text
        else:
            print(f"Failed to send news. Error: {response.text}")
            return response.text
    except Exception as e:
        print(f"An error occurred: {e}")
