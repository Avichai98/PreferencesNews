from mongoDB import mongo
from pymongo.errors import DuplicateKeyError
from passlib.hash import bcrypt

# Access the users collection
users_collection = mongo.get_collection("users")


# Create a new user
def save_user(user_data):
    try:

        # Hash the password
        user_data["password"] = bcrypt.hash(user_data["password"])

        result = users_collection.insert_one(user_data)
        return str(result.inserted_id)  # Return the ID of the inserted document
    except DuplicateKeyError:
        return "User with this email already exists."


# Fetch a user by email
def get_user_by_email(email):
    user = users_collection.find_one({"email": email})
    if user is not None:
        user["_id"] = str(user["_id"])
    return user


def update_user_preferences(email: str, preferences: dict):
    users_collection.update_one(
        {"email": email},  # Locate the user by ID
        {"$set": {"preferences": preferences}}  # Update preferences field
    )


def verify_user_credentials(email: str, password: str):
    user = users_collection.find_one({"email": email})
    if user and bcrypt.verify(password, user["password"]):
        return user
    return None


def get_all_users():
    users = list(users_collection.find({}))
    # Convert MongoDB ObjectId to string for JSON serialization
    for user in users:
        user["_id"] = str(user["_id"])
    return users


def delete_user_by_email(email: str):
    print("Deleting user by email")
    result = users_collection.delete_one({"email": email})
    return result.deleted_count
