from bson import ObjectId
from mongoDB import mongo

# Access the users collection
users_collection = mongo.get_collection("users")


def update_chat_id(chat_id, user_id):
    print("update...")
    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"preferences.telegram_id": int(chat_id)}}
    )
