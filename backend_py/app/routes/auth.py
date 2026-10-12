from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from ..database import get_db
from ..models.user import User
from ..schemas.auth import UserCreate, UserLogin, UserResponse, TokenResponse
from ..security import hash_password, verify_password, create_access_token, get_current_user
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(
    user_in: UserCreate,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Register a new user:
    1. Validates and normalizes email.
    2. Checks for duplicate email.
    3. Hashes password using Argon2id.
    4. Inserts record into PostgreSQL.
    5. Returns safe user data and session token.
    """
    normalized_email = user_in.email.strip().lower()

    # 1. Check duplicate email
    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists"
        )

    # 2. Hash password with Argon2id
    hashed_pwd = hash_password(user_in.password)

    # 3. Create User object
    new_user = User(
        name=user_in.name.strip(),
        email=normalized_email,
        password_hash=hashed_pwd,
        auth_provider="local",
        is_active=True
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError during signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not complete registration. Please try again."
        )

    # 4. Generate JWT Token
    token_payload = {
        "sub": str(new_user.id),
        "email": new_user.email,
        "name": new_user.name,
        "provider": new_user.auth_provider
    }
    token = create_access_token(token_payload)

    # 5. Set HttpOnly session cookie
    is_secure = settings.ENVIRONMENT == "production"
    response.set_cookie(
        key="storytelling_token",
        value=token,
        httponly=True,
        max_age=settings.JWT_EXPIRE_DAYS * 24 * 3600,
        samesite="lax",
        secure=is_secure
    )

    return TokenResponse(
        success=True,
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )

@router.post("/login", response_model=TokenResponse)
def login(
    credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Authenticate user:
    1. Retrieves user by normalized email.
    2. Verifies submitted password against Argon2id hash.
    3. Generates JWT session token and cookie.
    4. Returns safe profile.
    """
    normalized_email = credentials.email.strip().lower()

    user = db.query(User).filter(User.email == normalized_email).first()
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    # Generate JWT Token
    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "provider": user.auth_provider or "local"
    }
    token = create_access_token(token_payload)

    # Set HttpOnly session cookie
    is_secure = settings.ENVIRONMENT == "production"
    response.set_cookie(
        key="storytelling_token",
        value=token,
        httponly=True,
        max_age=settings.JWT_EXPIRE_DAYS * 24 * 3600,
        samesite="lax",
        secure=is_secure
    )

    return TokenResponse(
        success=True,
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Retrieve authenticated user's safe profile.
    Requires valid JWT in Authorization header or session cookie.
    """
    return UserResponse.model_validate(current_user)

@router.post("/logout")
def logout(response: Response):
    """
    Invalidate user session by clearing authentication cookies.
    """
    response.delete_cookie(key="storytelling_token", path="/")
    response.delete_cookie(key="sivacine_token", path="/")
    return {"success": True, "message": "Logged out successfully"}
