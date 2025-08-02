from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.user_model import UserRole
# ===================================================================
# This is the data the API receives.
# ===================================================================

class UserCreate(BaseModel):
    """
    Schema for creating a user. Receives a plain-text password.
    The API should NEVER receive a pre-hashed password.
    """
    name: str
    email: EmailStr
    password: str # CRITICAL: Receive plain password, hash it in the service layer.

class UserUpdate(BaseModel):
    """
    Schema for updating a user's profile.
    All fields are optional to support PATCH requests.
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None

# ===================================================================
# This is the data the API sends back.
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
        # This allows the model to be created from ORM objects (e.g., the User model).
        from_attributes = True
        
        
        
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str