from fastapi import APIRouter, status, Depends
from app.core.config import settings
from app.models.user_model import User
from app.schemas.book_schema import (
    BookCreate,
    BookResponse,
    BookUpdate,
    BookResponseWithTags,
)
from typing import List, Dict
from sqlmodel.ext.asyncio.session import AsyncSession
from app.services import book_service
from app.db.session import get_session
from app.utils.deps import get_current_verified_user

router = APIRouter(tags=["Books"], prefix=f"{settings.API_V1_STR}/books")


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=List[BookResponseWithTags]
)
async def get_all_books(*, db: AsyncSession = Depends(get_session)):
    return await book_service.get_all_books(
        db=db,
    )


@router.get(
    "/{book_id}", status_code=status.HTTP_200_OK, response_model=BookResponseWithTags
)
async def get_book_by_id(*, db: AsyncSession = Depends(get_session), book_id: int):
    return await book_service.get_book_by_id(db=db, book_id=book_id)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=BookResponseWithTags
)
async def create_book(
    *,
    book_data: BookCreate,
    db: AsyncSession = Depends(get_session),
    curent_user: User = Depends(get_current_verified_user),
):
    return await book_service.create_book(db=db, book_data=book_data, user=curent_user)


@router.patch(
    "/{book_id}", response_model=BookResponseWithTags, status_code=status.HTTP_200_OK
)
async def update_book(
    *,
    book_id: int,
    book_data: BookUpdate,
    db: AsyncSession = Depends(get_session),
    # Corrected typo and now passing this user down
    current_user: User = Depends(get_current_verified_user),
):
    """
    Updates a book owned by the current user.
    """
    return await book_service.update_book(
        db=db, book_id=book_id, book_data=book_data, user=current_user
    )


@router.delete(
    "/{book_id}", status_code=status.HTTP_200_OK, response_model=Dict[str, str]
)
async def delete_book(
    *,
    book_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    """
    Deletes a book owned by the current user.
    """
    await book_service.delete_book(db=db, book_id=book_id, user=current_user)
    return {"message": "Book deleted successfully"}
