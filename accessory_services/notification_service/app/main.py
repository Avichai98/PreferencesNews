from dapr.ext.fastapi import DaprApp
from fastapi import FastAPI, Request, HTTPException
from notification_function import telegram_bot_send_news, send_email

app = FastAPI()
dapr_app = DaprApp(app)


@app.post("/email_notification")
async def notification(request: Request):
    data = await request.json()

    try:
        # Send the news
        if send_email(data):
            print("News sent successfully!")
            return "News sent successfully!"
        else:
            print("Failed to send news")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@dapr_app.subscribe(pubsub='notificationpubsub', topic='notification_requests')
async def news_requests_subscriber(request: Request):
    # Extract data from the request body (Dapr envelope)
    data = await request.json()
    print(data)
    # Send the news
    try:
        response = telegram_bot_send_news(data)
        print(response)
        if response.status_code == 200:
            print(f"News sent successfully!")
            return response.text
        else:
            print(f"Failed to send news. Error: {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
