# from app.crud import review_crud, book_crud
# from sqlmodel.ext.asyncio.session import AsyncSession
# from fastapi import HTTPException, status
# from app.schemas.review_schema import ReviewCreate, ReviewUpdate
# from app.models.review_model import Review
# from app.models.user_model import User, UserRole
# from typing import List
# from app.core.exceptions import ReviewNotFound, NotAuthorized, BookNotFound


# async def get_all_reviews(db: AsyncSession) -> List[Review]:

#     return await review_crud.get_all_reviews(db=db)


# async def get_review_by_id(review_id: int, db: AsyncSession) -> Review | None:

#     review = await review_crud.get_review_by_id(db=db, review_id=review_id)

#     if not review:
#         raise ReviewNotFound(f"No review exists with this review_id{review_id}")
#     return review


# async def create_review(
#     db: AsyncSession, review_data: ReviewCreate, user: User, book_id: int
# ) -> Review:
#     # 1. Check if the book the user wants to review actually exists.
#     book = await book_crud.get_book_by_id(db=db, book_id=book_id)
#     if not book:
#         raise BookNotFound(f"Book with id {book_id} not found")

#     review_to_create = Review(
#         **review_data.model_dump(), user_id=user.id, book_id=book_id
#     )

#     return await review_crud.create_review(db=db, review=review_to_create)


# async def update_review(
#     review_id: int, db: AsyncSession, review_data: ReviewUpdate, user: User
# ) -> Review:
#     review_to_update = await review_crud.get_review_by_id(db=db, review_id=review_id)
#     if not review_to_update:
#         raise ReviewNotFound(f"No review exists with this review_id{review_id}")

#     if review_to_update.user_id != user.id and user.role != UserRole.ADMIN:
#         raise NotAuthorized("You are not authorized to perform this action")

#     return await review_crud.update_review(
#         db=db, review_data=review_data, review_id=review_id
#     )


# async def delete_review(review_id: int, db: AsyncSession, user: User) -> None:
#     review_to_delete = await review_crud.get_review_by_id(db=db, review_id=review_id)
#     if not review_to_delete:
#         raise ReviewNotFound(f"No review exists with this review_id{review_id}")

#     # BUG FIX: The authorization logic was inverted.
#     if review_to_delete.user_id != user.id and user.role != UserRole.ADMIN:
#         raise NotAuthorized("You are not authorized to perform this action")

#     await review_crud.delete_review(review_id=review_id, db=db)
from app.crud import review_crud, book_crud
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.review_schema import ReviewCreate, ReviewUpdate
from app.models.review_model import Review
from app.models.user_model import User, UserRole
from typing import List
from app.core.exceptions import (
    ReviewNotFound,
    NotAuthorized,
    BookNotFound,
)


# --- READ ---
async def get_all_reviews(db: AsyncSession) -> List[Review]:
    """Service to get all reviews."""
    return await review_crud.get_all_reviews(db=db)


async def get_review_by_id(review_id: int, db: AsyncSession) -> Review:
    """Service to get a single review by its ID."""
    review = await review_crud.get_review_by_id(db=db, review_id=review_id)
    if not review:
        raise ReviewNotFound(f"Review not found")
    return review


# --- CREATE ---
async def create_review(
    db: AsyncSession, review_data: ReviewCreate, user: User, book_id: int
) -> Review:
    """Service to create a review, with business logic and validation."""
    book = await book_crud.get_book_by_id(db=db, book_id=book_id)
    if not book:
        raise BookNotFound(f"Book not found")

    review_to_create = Review(
        **review_data.model_dump(), user_id=user.id, book_id=book_id
    )
    return await review_crud.create_review(db=db, review=review_to_create)


# --- UPDATE ---
async def update_review(
    review_id: int, db: AsyncSession, review_data: ReviewUpdate, user: User
) -> Review:
    """Service to update a review, with authorization."""
    review_to_update = await review_crud.get_review_by_id(db=db, review_id=review_id)
    if not review_to_update:
        raise ReviewNotFound(f"Review not found")

    if review_to_update.user_id != user.id and user.role != UserRole.ADMIN:
        raise NotAuthorized("You are not authorized to perform this action")

    return await review_crud.update_review(
        db=db, review_data=review_data, review_id=review_id
    )


# --- DELETE ---
async def delete_review(review_id: int, db: AsyncSession, user: User) -> None:
    """Service to delete a review, with authorization."""
    review_to_delete = await review_crud.get_review_by_id(db=db, review_id=review_id)
    if not review_to_delete:
        raise ReviewNotFound(f"Review not found")

    if review_to_delete.user_id != user.id and user.role != UserRole.ADMIN:
        raise NotAuthorized("You are not authorized to perform this action")

    await review_crud.delete_review(review_id=review_id, db=db)
