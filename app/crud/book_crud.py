from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.book_schema import BookCreate, BookUpdate
from app.models.book_model import Book
from sqlmodel import select
from typing import List, Optional
from sqlalchemy.orm import selectinload


async def get_all_books(db: AsyncSession) -> List[Book]:
    """Retrieves all book records from the database using the modern `db.scalars`."""
    statement = select(Book).options(selectinload(Book.tags))
    # The modern approach combines execute and scalars into one step.
    results = await db.scalars(statement)
    return results.all()


async def get_book_by_id(book_id: int, db: AsyncSession) -> Optional[Book]:
    """Retrieves a single book by its primary key using the most direct method."""
    # db.get() is the most efficient way to fetch an object by its primary key.
    statement = select(Book).where(Book.id == book_id).options(selectinload(Book.tags))
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def create_book(book: Book, db: AsyncSession) -> Book:
    """
    Creates a new book record and returns it with its tags pre-loaded.
    """
    db.add(book)
    await db.commit()
    # After committing, the 'book' object is expired. We need to get it again.
    # We use our helper function to get the newly created book with its tags.
    new_book = await get_book_by_id(db=db, book_id=book.id)
    return new_book


async def update_book(
    db: AsyncSession, book_to_update: Book, book_data: BookUpdate
) -> Optional[Book]:
    """
    Updates an existing book record and returns it with its tags pre-loaded.
    """
    # Get the scalar update data (excluding tags, which are handled in the service)
    update_data = book_data.model_dump(exclude={"tags"}, exclude_unset=True)
    for key, value in update_data.items():
        setattr(book_to_update, key, value)

    db.add(book_to_update)
    await db.commit()
    # We use our fixed helper function to get the updated book with its tags.
    updated_book = await get_book_by_id(db=db, book_id=book_to_update.id)
    return updated_book


async def delete_book(book_id: int, db: AsyncSession) -> Optional[Book]:
    """Deletes a book record from the database."""
    book_to_delete = await db.get(Book, book_id)
    if not book_to_delete:
        return None

    await db.delete(book_to_delete)
    await db.commit()
    return book_to_delete
