from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.user_model import UserRole


class UserCreate(BaseModel):
    """
    Schema for creating a user. Receives a plain-text password.
    The API should NEVER receive a pre-hashed password.
    """
    name: str
    email: EmailStr
    password: str 

class UserUpdate(BaseModel):
    """
    Schema for updating a user's profile.
    All fields are optional to support PATCH requests.
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None

# ===================================================================
# Body schemas for user-related operations
# ===================================================================

class UserResponse(BaseModel):
    """Schema for returning a user in an API response. NEVER includes the password."""
    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_verified: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
        
        
        
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str