from sqlmodel import SQLModel
from app.models.user_model import User
from app.models.tag_model import Tag

# 2. Import models that depend on the ones above.
from app.models.book_model import Book

# 3. Import models that depend on the ones above.
from app.models.review_model import Review
from app.models.book_tag_model import BookTag
