from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.config import settings
from app.core import security
from app.crud import user_crud
from app.db.session import get_session
from app.models.user_model import User, UserRole
from app.db.redis_conn import redis_client
from typing import List
from app.core.exceptions import InactiveUser, UnverifiedUser

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    db: AsyncSession = Depends(get_session), token: str = Depends(reusable_oauth2)
) -> User:
    """
    Dependency to get the user from an access token.
    Performs all necessary validation and checks.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Verify the token is generally valid (signature, expiration)
    #    and get its payload in a single step.
    payload = security.verify_token(token)
    if not payload or payload.get("type") != "access":
        raise credentials_exception

    # 2. Check if the token has been revoked (is on the blocklist).
    token_id = payload.get("jti")
    if not token_id or await redis_client.get(token_id):
        raise credentials_exception

    # 3. Get the user's email from the token's subject.
    email = payload.get("sub")
    if not email:
        raise credentials_exception

    # 4. Fetch the user from the database.
    user = await user_crud.get_user_by_email(email=email, db=db)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:

    if not current_user.is_active:
        raise InactiveUser("Your account is inactive")
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user),
) -> User:

    if not current_user.is_verified:
        raise UnverifiedUser("Please verify your account")
    return current_user


class RoleChecker:
    """
    A dependency class that checks if the current user has one of the
    allowed roles.
    """
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(get_current_verified_user)):

        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges",
            )




