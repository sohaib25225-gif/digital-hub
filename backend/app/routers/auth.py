from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    RefreshTokenRequest,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Annotated[Session, Depends(get_db)]):
    """
    Register a new user.

    Creates a new user account with the provided email, password, and full name.
    Passwords are securely hashed before storage.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        The created user data (without password)

    Raises:
        HTTPException: If email is already registered
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user with hashed password
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=UserRole.STUDENT,  # Default role is student
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(
    user_credentials: UserLogin,
    response: Response,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Authenticate user and return access and refresh tokens.

    Validates user credentials and returns JWT tokens for authentication.
    The refresh token is also set as an HttpOnly cookie for security.

    Args:
        user_credentials: User login credentials
        response: FastAPI response object
        db: Database session

    Returns:
        Access token, refresh token, and token type

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()

    # Verify user exists and password is correct
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Create access and refresh tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Set refresh token as HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Requires HTTPS in production
        samesite="none",  # Required for cross-origin requests
        max_age=7 * 24 * 60 * 60,  # 7 days in seconds
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get current authenticated user's information.

    Returns the profile data of the currently authenticated user.

    Args:
        current_user: The authenticated user (injected by dependency)

    Returns:
        Current user's data (without password)
    """
    return current_user


@router.post("/refresh", response_model=Token)
def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    response: Response,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Refresh access token using a valid refresh token.

    Generates a new access token and refresh token pair using a valid refresh token.

    Args:
        refresh_data: Refresh token
        response: FastAPI response object
        db: Database session

    Returns:
        New access token and refresh token

    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode refresh token
    payload = decode_token(refresh_data.refresh_token)
    if payload is None:
        raise credentials_exception

    # Verify token type
    token_type = payload.get("type")
    if token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    # Extract user ID
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    # Convert string UUID to proper UUID object for comparison
    import uuid
    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, AttributeError):
        raise credentials_exception

    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception

    # Create new tokens
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Set new refresh token as HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Logout current user.

    Clears the refresh token cookie to log out the user.
    Client should also discard the access token.

    Args:
        response: FastAPI response object
        current_user: The authenticated user (injected by dependency)

    Returns:
        No content (204 status code)
    """
    # Clear the refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="none"
    )
    return None
