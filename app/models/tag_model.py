# In app/models/tag_model.py

from typing import List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from app.models.book_tag_model import BookTag

if TYPE_CHECKING:
    from app.models.book_model import Book


class Tag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    name: str = Field(index=True, unique=True, nullable=False)

    books: List["Book"] = Relationship(back_populates="tags", link_model=BookTag)
