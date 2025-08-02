from fastapi import APIRouter, status, Depends
from app.models.user_model import User, UserRole
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.user_schema import UserUpdate, UserResponse
from app.services import user_service
from app.core.config import settings
from app.db.session import get_session
from app.utils.deps import get_current_verified_user, RoleChecker
from typing import Dict

router = APIRouter(tags=["User"], prefix=f"{settings.API_V1_STR}/user")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_my_profile_for_admin_test(
    current_user: User = Depends(get_current_verified_user),
):

    return current_user


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_by_id(*, user_id: int, db: AsyncSession = Depends(get_session)):

    return await user_service.get_user_by_id(db=db, user_id=user_id)


@router.patch("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    *,
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):

    return await user_service.update_user(
        db=db, user_id=user_id, user_data=user_data, current_user=current_user
    )


@router.delete(
    "/{user_id}", response_model=Dict[str, str], status_code=status.HTTP_200_OK
)
async def deactivate_user(
    *,
    user_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    """
    Deactivates a user.
    A user can only deactivate their own account, unless they are a superuser.
    """
    # Pass the user_id and the current_user to the service for authorization
    return await user_service.deactivate_user(
        user_id=user_id, db=db, current_user=current_user
    )
