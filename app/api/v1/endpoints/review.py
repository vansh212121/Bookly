from fastapi import APIRouter, status, Depends
from app.core.config import settings
from app.models.user_model import User
from app.models.book_model import Book
from app.schemas.review_schema import ReviewCreate, ReviewResponse, ReviewUpdate
from typing import List, Dict
from sqlmodel.ext.asyncio.session import AsyncSession
from app.services import review_service, user_service
from app.db.session import get_session
from app.utils.deps import get_current_verified_user


router = APIRouter(tags=["Reviews"], prefix=f"{settings.API_V1_STR}/reviews")


@router.get("/", response_model=List[ReviewResponse], status_code=status.HTTP_200_OK)
async def get_all_reviews(*, db: AsyncSession = Depends(get_session)):

    return await review_service.get_all_reviews(db=db)


@router.get(
    "/{review_id}", status_code=status.HTTP_200_OK, response_model=ReviewResponse
)
async def get_review_by_id(*, review_id: int, db: AsyncSession = Depends(get_session)):

    return await review_service.get_review_by_id(review_id=review_id, db=db)


@router.post(
    "/books/{book_id}/reviews",  # This is the correct, RESTful path
    status_code=status.HTTP_201_CREATED,
    response_model=ReviewResponse,
)
async def create_a_review_for_a_book(
    *,
    book_id: int,  # Get the book_id from the URL path
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    # Pass all the necessary info to the service layer
    return await review_service.create_review(
        db=db, review_data=review_data, user=current_user, book_id=book_id
    )


@router.get(
    "/{user_id}/reviews",
    response_model=List[ReviewResponse],
    status_code=status.HTTP_200_OK,
)
async def get_user_reviews(
    *,
    user_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    """
    Gets all reviews written by a specific user.
    """
    return await user_service.get_reviews_by_user(user_id=user_id, db=db)


@router.patch(
    "/{review_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReviewResponse,
)
async def update_a_review(
    *,
    review_id: int,
    review_data: ReviewUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    return await review_service.update_review(
        db=db, review_id=review_id, review_data=review_data, user=current_user
    )


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, str],
)
async def delete_review(
    *,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
    review_id: int,
):
    await review_service.delete_review(db=db, review_id=review_id, user=current_user)

    return {"message": "Your review was deleted"}
