from pydantic import BaseModel
import datetime
from typing import Optional, List
from app.schemas.tag_schema import TagResponse  # <-- Import the new TagResponse schema


class BookBase(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: datetime.date
    page_count: int
    language: str


class BookResponse(BookBase):
    id: int

    class Config:
        # This allows the model to be created from ORM objects.
        from_attributes = True


class BookCreate(BookBase):
    tags: Optional[List[str]] = None


class BookUpdate(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str

    tags: Optional[List[str]] = None


class BookResponseWithTags(BookResponse):
    """
    A richer response model that includes the book's details
    PLUS a list of its associated tags.
    """

    tags: List[TagResponse] = []
