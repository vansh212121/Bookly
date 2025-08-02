from typing import TYPE_CHECKING, List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, func
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

if TYPE_CHECKING:
    from app.models.book_model import Book
    from app.models.review_model import Review

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    
    role: UserRole = Field(default=UserRole.USER, nullable=False)
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)

    created_at: datetime = Field(
        default=None, sa_column_kwargs={"server_default": func.now()}, nullable=False
    )
    updated_at: datetime = Field(
        default=None, sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
        nullable=False
    )

    # ✅ FIXED - Use List for string-based forward references
    books: List["Book"] = Relationship(back_populates="user")
    reviews: List["Review"] = Relationship(back_populates="user")