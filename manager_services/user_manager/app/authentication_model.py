from pydantic import BaseModel


class AuthenticationModel(BaseModel):
    email: str
    password: str
