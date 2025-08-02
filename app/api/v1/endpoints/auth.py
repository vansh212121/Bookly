from fastapi import APIRouter, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.user_schema import (
    UserCreate,
    UserResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
)
from app.services import auth_service
from app.core.config import settings
from app.db.session import get_session
from app.schemas.token_schema import Token, RefreshTokenRequest
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.deps import get_current_user, reusable_oauth2, RoleChecker
from app.models.user_model import User, UserRole

router = APIRouter(tags=["Auth"], prefix=f"{settings.API_V1_STR}/auth")


@router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponse
)
async def signup_user(user_data: UserCreate, db: AsyncSession = Depends(get_session)):
    return await auth_service.create_user_and_send_verification(
        db=db, user_data=user_data
    )


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    return await auth_service.login_user(db=db, form_data=form_data)


@router.post("/admin/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    return await auth_service.login_admin(db=db, form_data=form_data)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(
    token: str = Depends(reusable_oauth2),
    # We depend on get_current_user to ensure only authenticated users can log out
    current_user: User = Depends(get_current_user),
):
    await auth_service.logout_user(token=token)
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: RefreshTokenRequest, db: AsyncSession = Depends(get_session)
):
    """
    Takes a refresh token and returns a new access and refresh token pair.
    """
    return await auth_service.refresh_access_token(
        refresh_token=token_data.refresh_token, db=db
    )


@router.post("/request-verification-email", status_code=status.HTTP_202_ACCEPTED)
async def request_new_verification_email(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Endpoint for a logged-in user to request a new verification email."""
    await auth_service.request_verification_email(db=db, user=current_user)
    return {"message": "A new verification email has been sent."}


@router.get("/verify-account", status_code=status.HTTP_200_OK)
async def verify_account(token: str, db: AsyncSession = Depends(get_session)):
    await auth_service.verify_user_account(db=db, token=token)
    return {"message": "Your account has been successfully verified."}


@router.post("/password-reset-request", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset_email(
    request_data: PasswordResetRequest, db: AsyncSession = Depends(get_session)
):
    await auth_service.request_password_reset(db=db, email_address=request_data.email)
    return {
        "message": "If an account with that email exists, a password reset link has been sent."
    }


@router.post("/password-reset-confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    request_data: PasswordResetConfirm, db: AsyncSession = Depends(get_session)
):
    await auth_service.reset_password_with_token(
        db=db, token=request_data.token, new_password=request_data.new_password
    )
    return {"message": "Your password has been reset successfully."}
