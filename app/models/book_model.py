# books = [

#     {
#         "id": 1,
#         "title": "The Pragmatic Programmer",
#         "author": "Andrew Hunt, David Thomas",
#         "publisher": "Addison-Wesley",
#         "published_date": "1999-10-30",
#         "page_count": 352,
#         "language": "en",
#     },
#     {
#         "id": 2,
#         "title": "Clean Code",
#         "author": "Robert C. Martin",
#         "publisher": "Prentice Hall",
#         "published_date": "2008-08-11",
#         "page_count": 464,
#         "language": "en",
#     },
#     {
#         "id": 3,
#         "title": "Design Patterns",
#         "author": "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
#         "publisher": "Addison-Wesley",
#         "published_date": "1994-10-21",
#         "page_count": 395,
#         "language": "en",
#     },
#     {
#         "id": 4,
#         "title": "You Don't Know JS Yet",
#         "author": "Kyle Simpson",
#         "publisher": "Independently published",
#         "published_date": "2020-01-28",
#         "page_count": 143,
#         "language": "en",
#     },
#     {
#         "id": 5,
#         "title": "Atomic Habits",
#         "author": "James Clear",
#         "publisher": "Avery"
#         "published_date": "2018-10-16"
#         "page_count": 320,
#         "language": "en",
#     },
#     {
#         "id": 6,
#         "title": "Deep Work",
#         "author": "Cal Newport",
#         "publisher": "Grand Central Publishing",
#         "published_date": "2016-01-05",
#         "page_count": 304,
#         "language": "en",
#     },
#     {
#         "id": 7,
#         "title": "Sapiens: A Brief History of Humankind",
#         "author": "Yuval Noah Harari",
#         "publisher": "Harper",
#         "published_date": "2015-02-10",
#         "page_count": 498,
#         "language": "en",
#     },
#     {
#         "id": 8,
#         "title": "Ikigai",
#         "author": "Héctor García, Francesc Miralles",
#         "publisher": "Penguin Books",
#         "published_date": "2017-08-29",
#         "page_count": 208,
#         "language": "en",
#     },
# ]


from typing import TYPE_CHECKING, Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Relationship, Field, func
from pydantic import ConfigDict
from app.models.book_tag_model import BookTag # <-- Add this import

if TYPE_CHECKING:
    from app.models.user_model import User
    from app.models.review_model import Review
    from app.models.tag_model import Tag # <-- Add this import


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

    # ✅ FIXED - Use Optional for string-based forward references
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
