from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    refresh_token: str 
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str
