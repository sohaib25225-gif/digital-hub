from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.schemas.user import TokenData

# HTTP Bearer token security scheme
security = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        The authenticated User object

    Raises:
        HTTPException: If token is invalid, expired, or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Extract token from credentials
    token = credentials.credentials

    # Decode token
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    # Verify token type
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user identifier from token
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    # Get user from database
    # Convert string UUID to proper UUID object for comparison
    import uuid
    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, AttributeError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency to verify the current user has admin role.

    Args:
        current_user: The currently authenticated user

    Returns:
        The authenticated User object (guaranteed to be admin)

    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )

    return current_user
