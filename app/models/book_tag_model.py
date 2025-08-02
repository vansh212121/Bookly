# In app/models/book_tag_model.py
from sqlmodel import SQLModel, Field


class BookTag(SQLModel, table=True):

    book_id: int | None = Field(default=None, foreign_key="book.id", primary_key=True)
    tag_id: int | None = Field(default=None, foreign_key="tag.id", primary_key=True)
