from pydantic import BaseModel, EmailStr
from typing import Optional

from preference_model import PreferencesModel


class UserModel(BaseModel):
    id: str
    email: EmailStr
    password: str
    preferences: Optional["PreferencesModel"]
