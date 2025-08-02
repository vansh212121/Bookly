from sqlmodel import SQLModel, Field, func, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user_model import User
    from app.models.book_model import Book


class Review(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    
    rating: int = Field(ge=1, le=5, nullable=False)
    review_text: str = Field(nullable=False)

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    book_id: Optional[int] = Field(default=None, foreign_key="book.id")

    created_at: datetime = Field(
        default=None, sa_column_kwargs={"server_default": func.now()}, nullable=False
    )
    updated_at: datetime = Field(
        default=None,
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
        nullable=False,
    )

    user: Optional["User"] = Relationship(back_populates="reviews")
    book: Optional["Book"] = Relationship(back_populates="reviews")
