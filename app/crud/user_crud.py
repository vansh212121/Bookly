from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.user_schema import UserUpdate
from app.models.user_model import User
from typing import Optional
from sqlmodel import select
from sqlalchemy.orm import selectinload  # <-- Import the eager loading tool


async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    """Helper function to get a user by their email."""
    statement = select(User).where(User.email == email)
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def create_user(user: User, db: AsyncSession) -> User:
    """
    Creates a new user object in the database.
    This function now correctly expects a complete User model object.
    """
    # The user object is already created and validated in the service layer.
    # We just need to add it to the database.
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_id(user_id: int, db: AsyncSession) -> User:

    return await db.get(User, user_id)


async def update_user(user_id: int, user_data: UserUpdate, db: AsyncSession) -> User:

    user = await db.get(User, user_id)

    if not user:
        return None

    updated_data = user_data.model_dump(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(user, key, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def deactivate_user(user_id: int, db: AsyncSession) -> Optional[User]:
    user = await db.get(User, user_id)

    if not user:
        return None

    user.is_active = False

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def get_user_with_reviews(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Gets a single user by ID, but also pre-loads their reviews in the same query
    to prevent lazy loading errors.
    """
    # 1. Create the base query for the User.
    statement = select(User).where(User.id == user_id)

    # 2. Add an option to "eagerly load" the 'reviews' relationship.
    #    'selectinload' is the most efficient strategy for one-to-many relationships.
    statement = statement.options(selectinload(User.reviews))

    # 3. Execute the query.
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def update_user_password(db: AsyncSession, user_to_update: User, hashed_password: str) -> User:
    """
    Specifically updates a user's hashed password.
    """
    user_to_update.hashed_password = hashed_password
    db.add(user_to_update)
    await db.commit()
    await db.refresh(user_to_update)
    return user_to_update