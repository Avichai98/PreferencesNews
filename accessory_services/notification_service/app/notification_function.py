import os
import smtplib
import requests


def send_email(data):
    try:
        email = data.get("email")
        news = data.get("news")

        # creates SMTP session using a secure port
        s = smtplib.SMTP_SSL('smtp-mail.outlook.com', 465)

        password = os.getenv("PASSWORD")

        s.login('avichaiwork@outlook.com', password)
        s.sendmail('avichaiwork@outlook.com', email, news)
        s.quit()
        return True

    except (smtplib.SMTPException, smtplib.SMTPAuthenticationError) as e:
        print(f"Error sending email: {e}")
        return False


def telegram_bot_send_news(data):
    telegram_id = data.get("telegram_id")
    news = data.get("news")

    bot_token = os.getenv("BOT_TOKEN")
    print(telegram_id)
    # Telegram API URL
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": telegram_id,
        "text": news
    }

    # Send the message
    response = requests.post(url, json=payload)
    return response
