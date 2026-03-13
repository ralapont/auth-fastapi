from pydantic import BaseModel, Field
from typing import Optional

class LoginRequest(BaseModel):
    username: str = Field(..., examples=["alice"])
    password: str = Field(..., examples=["secret123"])

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeResponse(BaseModel):
    username: str
    full_name: Optional[str] = None