from pydantic import BaseModel
from typing import Optional

class TagBase(BaseModel):
    """Base schema for a tag."""
    name: str

class TagCreate(TagBase):
    """Schema for creating a new tag (used by admins)."""
    pass

class TagUpdate(BaseModel):
    """Schema for updating a tag's name (used by admins)."""
    name: Optional[str] = None

class TagResponse(TagBase):
    """Schema for returning a tag in an API response."""
    id: int

    class Config:
        from_attributes = True
