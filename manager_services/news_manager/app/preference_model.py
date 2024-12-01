from pydantic import BaseModel, EmailStr
from typing import List, Optional


class PreferencesModel(BaseModel):
    categories: List[str]  # E.g., ["Technology", "Sports"]
    language: Optional[str] = "en"  # Default language is English
    platforms: List[str] = ["Telegram"]  # Default platform is Telegram
    email: Optional[EmailStr]
    telegram_id: Optional[int]
