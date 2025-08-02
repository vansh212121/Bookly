from app.crud import book_crud, tag_crud
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.book_schema import BookCreate, BookUpdate
from app.models.book_model import Book
from typing import List
from app.models.user_model import User, UserRole
from app.models.tag_model import Tag
from app.core.exceptions import BookNotFound, NotAuthorized

async def _process_tags(db: AsyncSession, tag_names: List[str]) -> List[Tag]:
    """
    A helper function to handle the "get-or-create" logic for tags.
    It takes a list of strings and returns a list of Tag model objects.
    """
    tags_to_assign = []
    for tag_name in tag_names:
        normalized_name = tag_name.strip().lower()
        if not normalized_name:
            continue

        tag = await tag_crud.get_tag_by_name(db=db, name=normalized_name)
        if not tag:
            tag_data = {"name": normalized_name}
            tag = await tag_crud.create_tag(db=db, tag_data=tag_data)
        tags_to_assign.append(tag)
    return tags_to_assign

# --- READ ---
async def get_all_books(db: AsyncSession) -> List[Book]:
    """Service layer to fetch all books."""
    return await book_crud.get_all_books(db=db)

async def get_book_by_id(book_id: int, db: AsyncSession) -> Book:
    """Service layer to fetch a single book by its ID."""
    book = await book_crud.get_book_by_id(db=db, book_id=book_id)
    if not book:
        raise BookNotFound(f"Book not found")
    return book

# --- CREATE ---
async def create_book(db: AsyncSession, book_data: BookCreate, user: User) -> Book:
    """Service to create a book and assign it to a user, with tag handling."""
    book_data_dict = book_data.model_dump(exclude={"tags"})
    book_to_create = Book(**book_data_dict, user_id=user.id)

    if book_data.tags:
        tag_objects = await _process_tags(db=db, tag_names=book_data.tags)
        book_to_create.tags = tag_objects

    return await book_crud.create_book(book=book_to_create, db=db)

# --- UPDATE ---
async def update_book(
    db: AsyncSession, book_id: int, book_data: BookUpdate, user: User
) -> Book:
    """Service to update a book, with authorization and tag handling."""
    book_to_update = await book_crud.get_book_by_id(db=db, book_id=book_id)
    if not book_to_update:
        raise BookNotFound(f"Book not found")

    if book_to_update.user_id != user.id and user.role != UserRole.ADMIN:
        raise NotAuthorized("You are not authorized to perform this action")

    if book_data.tags is not None:
        book_to_update.tags = await _process_tags(db=db, tag_names=book_data.tags)

    return await book_crud.update_book(
        db=db, book_to_update=book_to_update, book_data=book_data
    )

# --- DELETE ---
async def delete_book(db: AsyncSession, book_id: int, user: User) -> None:
    """
    Service to delete a book, ensuring the user is the owner or an admin.
    """
    book_to_delete = await book_crud.get_book_by_id(db=db, book_id=book_id)
    if not book_to_delete:
        raise BookNotFound(f"Book not found")

    # --- THIS IS THE FIX ---
    # The authorization check must also allow admins to delete books.
    if book_to_delete.user_id != user.id and user.role != UserRole.ADMIN:
        raise NotAuthorized("You are not authorized to perform this action")

    await book_crud.delete_book(db=db, book_id=book_id)
