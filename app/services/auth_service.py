from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

# --- Core Application Imports ---
from app.core import security
from app.core.config import settings
from app.crud import user_crud
from app.db.redis_conn import redis_client
from app.models.user_model import User, UserRole
from app.schemas.user_schema import UserCreate

# --- Custom Exception Imports ---
from app.core.exceptions import (
    InvalidCredentials,
    InactiveUser,
    UnverifiedUser,
    NotAuthorized,
    UserAlreadyExists,
    InvalidToken,
    AppException,
)
from app.core import email, security
from app.celery_tasks import send_verification_email_task, send_password_reset_email_task


async def login_user(db: AsyncSession, form_data: OAuth2PasswordRequestForm) -> dict:
    """
    Service to handle a regular user's login, using custom exceptions for business logic.
    """
    user = await user_crud.get_user_by_email(db=db, email=form_data.username)

    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        raise InvalidCredentials("Incorrect Email or Password")

    # if user.role == UserRole.ADMIN:
    #     raise NotAuthorized("Administrators cannot log in here. Please use the admin portal.")

    # if not user.is_verified:
    #     raise UnverifiedUser("Please verify your account")

    if not user.is_active:
        raise InactiveUser("Your account is inactive")

    access_token = security.create_access_token(subject=user.email)
    refresh_token = security.create_refresh_token(subject=user.email)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
    
async def login_admin(db: AsyncSession, form_data: OAuth2PasswordRequestForm) -> dict:
    """
    Service to handle a regular user's login, using custom exceptions for business logic.
    """
    user = await user_crud.get_user_by_email(db=db, email=form_data.username)

    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        raise InvalidCredentials("Incorrect Email or Password")

    if user.role == UserRole.USER:
        raise NotAuthorized("Users cannot log in here. Please use the user portal.")

    if not user.is_verified:
        raise UnverifiedUser("Please verify your account")

    if not user.is_active:
        raise InactiveUser("Your account is inactive")

    access_token = security.create_access_token(subject=user.email)
    refresh_token = security.create_refresh_token(subject=user.email)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }



async def create_user_and_send_verification(db: AsyncSession, user_data: UserCreate) -> User:
    """Service to create a user, hash the password, and dispatch a verification email task."""
    db_user = await user_crud.get_user_by_email(email=user_data.email, db=db)
    if db_user:
        raise UserAlreadyExists()

    hashed_pass = security.hash_password(user_data.password)
    user_to_create = User.model_validate(user_data, update={"hashed_password": hashed_pass})
    new_user = await user_crud.create_user(user=user_to_create, db=db)
    
    token = security.generate_email_verification_token(email=new_user.email)
    # Dispatch the task to the Celery worker
    send_verification_email_task.delay(email_to=new_user.email, token=token)
    
    return new_user


async def logout_user(token: str) -> None:
    """Adds a token to the blocklist to revoke it."""
    payload = security.verify_token(token)
    if payload:
        token_id = payload.get("jti")
        if token_id:
            await redis_client.setex(
                token_id,
                timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
                "revoked",
            )


async def refresh_access_token(refresh_token: str, db: AsyncSession) -> dict:
    """Verifies a refresh token and issues a new pair of tokens (rotation)."""
    payload = security.verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise InvalidToken("Could not validate refresh token")

    token_id = payload.get("jti")
    if not token_id or await redis_client.get(token_id):
        raise InvalidToken("Refresh token has been revoked or is invalid")

    user = await user_crud.get_user_by_email(db=db, email=payload.get("sub"))
    if not user or not user.is_active:
        raise InvalidToken("User not found or inactive")

    await redis_client.setex(
        token_id, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), "revoked"
    )

    new_access_token = security.create_access_token(subject=user.email)
    new_refresh_token = security.create_refresh_token(subject=user.email)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


async def request_verification_email(db: AsyncSession, user: User):
    """Service to dispatch a new verification email task for an existing user."""
    if user.is_verified:
        raise AppException(status_code=400, detail="Account is already verified.")
        
    token = security.generate_email_verification_token(email=user.email)
    send_verification_email_task.delay(email_to=user.email, token=token)



async def verify_user_account(db: AsyncSession, token: str) -> User:
    # --- THIS IS THE FIX ---
    # We now call the correct verification function for email tokens.
    payload = security.verify_email_verification_token(token)
    if not payload:
        raise InvalidToken("Verification token is invalid or has expired.")
    # --- END OF FIX ---
        
    user = await user_crud.get_user_by_email(db=db, email=payload.get("email"))
    if not user:
        raise InvalidToken("User associated with this token not found.")
        
    if user.is_verified:
        return user
        
    user.is_verified = True
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def request_password_reset(db: AsyncSession, email_address: str) -> None:
    """Service to dispatch a password reset email task."""
    user = await user_crud.get_user_by_email(db=db, email=email_address)
    if user and user.is_active:
        token = security.generate_password_reset_token(email=user.email)
        send_password_reset_email_task.delay(email_to=user.email, token=token)


async def reset_password_with_token(db: AsyncSession, token: str, new_password: str) -> None:
    payload = security.verify_password_reset_token(token)
    if not payload:
        raise InvalidToken("Password reset token is invalid or has expired.")
        
    user = await user_crud.get_user_by_email(db=db, email=payload.get("email"))
    if not user:
        raise InvalidToken("User associated with this token not found.")
        
    hashed_password = security.hash_password(new_password)
    
    # Call the dedicated CRUD function with the correct arguments
    await user_crud.update_user_password(
        db=db, user_to_update=user, hashed_password=hashed_password
    )
