from fastapi import FastAPI, Request
from webhook_function import update_chat_id

app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request):
    try:
        # Parse incoming JSON payload
        data = await request.json()
        if "message" in data:
            message_text = data["message"].get("text", "")
            chat_id = data["message"]["chat"]["id"]
            user_id = message_text.split(" ")[1]
            update_chat_id(chat_id, user_id)
            print(f"Message: {user_id}")
            print(f"Chat ID: {chat_id}")
            return {"status": "success"}
        else:
            return {"status": "message not found"}
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}
