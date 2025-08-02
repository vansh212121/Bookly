# from app.crud import user_crud
# from app.schemas.user_schema import UserUpdate
# from app.models.user_model import User
# from app.models.review_model import Review
# from sqlmodel.ext.asyncio.session import AsyncSession
# from typing import List
# from app.core.exceptions import NotAuthorized, UserNotFound


# async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
#     """Service to get a user by ID, handling not found errors."""
#     user = await user_crud.get_user_by_id(db=db, user_id=user_id)
#     if not user:
#         raise UserNotFound(f"User does not exist with user_id:{user_id}")
#     return user


# async def get_reviews_by_user(db: AsyncSession, user_id: int) -> List[Review]:
#     """
#     Service to get all reviews written by a specific user.
#     """
#     # 1. First, check if the user we want to see reviews for actually exists.
#     #    UPDATED: We now call a more specific CRUD function that eagerly loads the reviews.
#     user = await user_crud.get_user_with_reviews(db=db, user_id=user_id)
#     if not user:
#         raise UserNotFound(f"User does not exist with user_id:{user_id}")

#     # 2. If the user exists, return their list of reviews.
#     #    The reviews are now pre-loaded, so accessing this list will not cause an error.
#     return user.reviews


# async def update_user(
#     db: AsyncSession, user_id: int, user_data: UserUpdate, current_user: User
# ) -> User:
#     """
#     Service to update a user, ensuring the requesting user is authorized.
#     """
#     # 1. First, get the user that is being targeted for the update.
#     user_to_update = await user_crud.get_user_by_id(db=db, user_id=user_id)
#     if not user_to_update:
#         raise UserNotFound(f"User does not exist with user_id:{user_id}")

#     # 2. --- AUTHORIZATION CHECK ---
#     #    Allow the action if the current user is the user they are trying to update,
#     #    OR if the current user is a superuser.
#     if current_user.id != user_to_update.id and not current_user.is_superuser:
#         raise NotAuthorized("You are not authorized to perform thsi action")

#     # 3. If authorized, proceed with the update.
#     return await user_crud.update_user(db=db, user_id=user_id, user_data=user_data)


# async def deactivate_user(db: AsyncSession, user_id: int, current_user: User) -> dict:
#     """
#     Service to deactivate a user, ensuring the requesting user is authorized.
#     """
#     # 1. Get the user that is being targeted for deactivation.
#     user_to_deactivate = await user_crud.get_user_by_id(db=db, user_id=user_id)
#     if not user_to_deactivate:
#         raise UserNotFound(f"User does not exist with user_id:{user_id}")

#     # 2. --- AUTHORIZATION CHECK ---
#     if current_user.id != user_to_deactivate.id and not current_user.is_superuser:
#         raise NotAuthorized("You are not authorized to perform thsi action")

#     # 3. If authorized, proceed with deactivation.
#     deactivated_user = await user_crud.deactivate_user(db=db, user_id=user_id)
#     # This check is technically redundant now but safe to keep.
#     if not deactivated_user:
#         raise UserNotFound(f"User does not exist with user_id:{user_id}")

#     return {"message": "User deactivated successfully"}
from app.crud import user_crud
from app.schemas.user_schema import UserUpdate
from app.models.user_model import User, UserRole  # <-- Import UserRole
from app.models.review_model import Review
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from app.core.exceptions import NotAuthorized, UserNotFound


async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    """Service to get a user by ID, handling not found errors."""
    user = await user_crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise UserNotFound(f"User not found")
    return user


async def get_reviews_by_user(db: AsyncSession, user_id: int) -> List[Review]:
    """Service to get all reviews written by a specific user."""
    user = await user_crud.get_user_with_reviews(db=db, user_id=user_id)
    if not user:
        raise UserNotFound(f"User not found")
    return user.reviews


async def update_user(
    db: AsyncSession, user_id: int, user_data: UserUpdate, current_user: User
) -> User:
    """Service to update a user, ensuring the requesting user is authorized."""
    user_to_update = await user_crud.get_user_by_id(db=db, user_id=user_id)
    if not user_to_update:
        raise UserNotFound(f"User not found")

    # --- THIS IS THE FIX ---
    # We now check against the UserRole enum instead of the old is_superuser flag.
    if current_user.id != user_to_update.id and current_user.role != UserRole.ADMIN:
        raise NotAuthorized("You are not authorized to perform this action")

    # The CRUD function now expects the user object to update, not just the ID.
    return await user_crud.update_user(
        db=db, user_to_update=user_to_update, user_data=user_data
    )


async def deactivate_user(db: AsyncSession, user_id: int, current_user: User) -> dict:
    """Service to deactivate a user, ensuring the requesting user is authorized."""
    user_to_deactivate = await user_crud.get_user_by_id(db=db, user_id=user_id)
    if not user_to_deactivate:
        raise UserNotFound(f"User not found")

    # --- THIS IS THE FIX ---
    if current_user.id != user_to_deactivate.id and current_user.role != UserRole.ADMIN:
        raise NotAuthorized("You are not authorized to perform this action")

    # If authorized, proceed with deactivation.
    # The redundant check has been removed for clarity.
    await user_crud.deactivate_user(db=db, user_id=user_id)

    return {"message": "User deactivated successfully"}
