from typing import TYPE_CHECKING, Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Relationship, Field, func
from pydantic import ConfigDict
from app.models.book_tag_model import BookTag 

if TYPE_CHECKING:
    from app.models.user_model import User
    from app.models.review_model import Review
    from app.models.tag_model import Tag 


class Book(SQLModel, table=True):
    model_config = ConfigDict(extra="allow")
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, unique=True, nullable=False)
    author: str = Field(nullable=False)
    publisher: str = Field(nullable=False)
    language: str = Field(nullable=False)
    page_count: int = Field(nullable=False)
    published_date: datetime = Field(nullable=False)

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    user: Optional["User"] = Relationship(back_populates="books")
    tags: List["Tag"] = Relationship(back_populates="books", link_model=BookTag)
    

    created_at: datetime = Field(
        default=None, sa_column_kwargs={"server_default": func.now()}, nullable=False
    )
    updated_at: datetime = Field(
        default=None,
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
        nullable=False,
    )

    reviews: List["Review"] = Relationship(back_populates="book")
