# In app/core/security.py
import uuid
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import settings
from itsdangerous import URLSafeTimedSerializer

# --- Password Hashing (No changes here) ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- Token Creation & Verification ---
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

def create_access_token(subject: str) -> str:
    """Creates a short-lived access token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "jti": str(uuid.uuid4()),
        "type": "access"  # NEW: Add a 'type' claim
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)

# --- NEW FUNCTION ---
def create_refresh_token(subject: str) -> str:
    """Creates a long-lived refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "jti": str(uuid.uuid4()),
        "type": "refresh" # NEW: Add a 'type' claim
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)

def verify_token(token: str) -> dict | None:
    """
    Verifies any JWT token. Returns the payload if valid, otherwise None.
    This function doesn't care about the token type, just its validity.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# --- URL-Safe Timed Tokens (for emails) ---
email_verification_serializer = URLSafeTimedSerializer(settings.JWT_SECRET, salt="email-verification-salt")
password_reset_serializer = URLSafeTimedSerializer(settings.JWT_SECRET, salt="password-reset-salt")

def generate_email_verification_token(email: str) -> str:
    """Generates a secure, timed token specifically for verifying an email."""
    return email_verification_serializer.dumps({"email": email})

def verify_email_verification_token(token: str, max_age_seconds: int = 3600) -> dict | None:
    """Verifies an email verification token."""
    try:
        return email_verification_serializer.loads(token, max_age=max_age_seconds)
    except Exception:
        return None

def generate_password_reset_token(email: str) -> str:
    """Generates a secure, timed token specifically for resetting a password."""
    return password_reset_serializer.dumps({"email": email})

def verify_password_reset_token(token: str, max_age_seconds: int = 3600) -> dict | None:
    """Verifies a password reset token."""
    try:
        return password_reset_serializer.loads(token, max_age=max_age_seconds)
    except Exception:
        return None