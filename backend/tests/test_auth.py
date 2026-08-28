import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.db.models.user import User, UserRole
from app.core.security import get_password_hash, create_access_token, create_refresh_token
from datetime import timedelta


class TestUserRegistration:
    """Tests for user registration endpoint."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "securepassword123",
                "full_name": "Test User"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert data["role"] == "student"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "hashed_password" not in data
        assert "password" not in data

    def test_register_duplicate_email(self, client):
        """Test registration with already registered email."""
        # First registration
        client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "password123",
                "full_name": "First User"
            }
        )

        # Second registration with same email
        response = client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "different_password",
                "full_name": "Second User"
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Email already registered"

    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        response = client.post(
            "/auth/register",
            json={
                "email": "not-an-email",
                "password": "password123",
                "full_name": "Test User"
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_short_password(self, client):
        """Test registration with password less than 8 characters."""
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "short",
                "full_name": "Test User"
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_password_is_hashed(self, client, db_session):
        """Test that passwords are hashed in the database."""
        plain_password = "mypassword123"
        client.post(
            "/auth/register",
            json={
                "email": "hash_test@example.com",
                "password": plain_password,
                "full_name": "Hash Test"
            }
        )

        # Check database directly
        user = db_session.query(User).filter(User.email == "hash_test@example.com").first()
        assert user is not None
        assert user.hashed_password != plain_password
        assert user.hashed_password.startswith("$2b$")  # bcrypt hash


class TestUserLogin:
    """Tests for user login endpoint."""

    def test_login_success(self, client):
        """Test successful login."""
        # Register user
        client.post(
            "/auth/register",
            json={
                "email": "login@example.com",
                "password": "password123",
                "full_name": "Login User"
            }
        )

        # Login
        response = client.post(
            "/auth/login",
            json={
                "email": "login@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0

    def test_login_incorrect_password(self, client):
        """Test login with incorrect password."""
        # Register user
        client.post(
            "/auth/register",
            json={
                "email": "wrongpass@example.com",
                "password": "correctpassword",
                "full_name": "Test User"
            }
        )

        # Login with wrong password
        response = client.post(
            "/auth/login",
            json={
                "email": "wrongpass@example.com",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Incorrect email or password"

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email."""
        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "somepassword"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Incorrect email or password"

    def test_login_inactive_user(self, client, db_session):
        """Test login with inactive user account."""
        # Register user
        client.post(
            "/auth/register",
            json={
                "email": "inactive@example.com",
                "password": "password123",
                "full_name": "Inactive User"
            }
        )

        # Deactivate user
        user = db_session.query(User).filter(User.email == "inactive@example.com").first()
        user.is_active = False
        db_session.commit()

        # Try to login
        response = client.post(
            "/auth/login",
            json={
                "email": "inactive@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Account is inactive"


class TestGetCurrentUser:
    """Tests for /auth/me endpoint."""

    def test_get_me_with_valid_token(self, client):
        """Test getting current user with valid token."""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "email": "me@example.com",
                "password": "password123",
                "full_name": "Me User"
            }
        )

        login_response = client.post(
            "/auth/login",
            json={
                "email": "me@example.com",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]

        # Get current user
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "me@example.com"
        assert data["full_name"] == "Me User"
        assert "hashed_password" not in data
        assert "password" not in data

    def test_get_me_without_token(self, client):
        """Test getting current user without authentication."""
        response = client.get("/auth/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_me_with_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token_xyz"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Could not validate credentials"

    def test_get_me_with_expired_token(self, client, db_session):
        """Test getting current user with expired token."""
        # Register user
        client.post(
            "/auth/register",
            json={
                "email": "expired@example.com",
                "password": "password123",
                "full_name": "Expired User"
            }
        )

        # Get user from DB
        user = db_session.query(User).filter(User.email == "expired@example.com").first()

        # Create expired token (negative expiration)
        expired_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=-1)
        )

        # Try to access with expired token
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRefreshToken:
    """Tests for token refresh endpoint."""

    def test_refresh_token_success(self, client):
        """Test successful token refresh."""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "email": "refresh@example.com",
                "password": "password123",
                "full_name": "Refresh User"
            }
        )

        login_response = client.post(
            "/auth/login",
            json={
                "email": "refresh@example.com",
                "password": "password123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh token
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_with_invalid_token(self, client):
        """Test token refresh with invalid token."""
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "invalid_refresh_token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_with_access_token(self, client):
        """Test that access tokens cannot be used to refresh."""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "email": "wrongtype@example.com",
                "password": "password123",
                "full_name": "Wrong Type User"
            }
        )

        login_response = client.post(
            "/auth/login",
            json={
                "email": "wrongtype@example.com",
                "password": "password123"
            }
        )
        access_token = login_response.json()["access_token"]

        # Try to refresh with access token
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": access_token}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid token type"


class TestLogout:
    """Tests for logout endpoint."""

    def test_logout_success(self, client):
        """Test successful logout."""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "email": "logout@example.com",
                "password": "password123",
                "full_name": "Logout User"
            }
        )

        login_response = client.post(
            "/auth/login",
            json={
                "email": "logout@example.com",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]

        # Logout
        response = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_logout_without_token(self, client):
        """Test logout without authentication."""
        response = client.post("/auth/logout")

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAdminAuthorization:
    """Tests for admin authorization."""

    def test_admin_endpoint_with_admin_user(self, client, db_session):
        """Test admin endpoint access with admin user."""
        # Register user
        client.post(
            "/auth/register",
            json={
                "email": "admin@example.com",
                "password": "password123",
                "full_name": "Admin User"
            }
        )

        # Make user admin
        user = db_session.query(User).filter(User.email == "admin@example.com").first()
        user.role = UserRole.ADMIN
        db_session.commit()

        # Login
        login_response = client.post(
            "/auth/login",
            json={
                "email": "admin@example.com",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]

        # Access admin endpoint
        response = client.get(
            "/admin/health",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["router"] == "admin"
        assert data["admin_user"] == "admin@example.com"

    def test_admin_endpoint_with_student_user(self, client):
        """Test admin endpoint access with non-admin user."""
        # Register normal student user
        client.post(
            "/auth/register",
            json={
                "email": "student@example.com",
                "password": "password123",
                "full_name": "Student User"
            }
        )

        # Login
        login_response = client.post(
            "/auth/login",
            json={
                "email": "student@example.com",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]

        # Try to access admin endpoint
        response = client.get(
            "/admin/health",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]


class TestPasswordSecurity:
    """Tests to ensure passwords are never exposed."""

    def test_password_not_in_register_response(self, client):
        """Test that password is not in registration response."""
        response = client.post(
            "/auth/register",
            json={
                "email": "secure@example.com",
                "password": "mysecretpassword",
                "full_name": "Secure User"
            }
        )

        data = response.json()
        assert "password" not in data
        assert "hashed_password" not in data

    def test_password_not_in_me_response(self, client):
        """Test that password is not in /auth/me response."""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "email": "noleak@example.com",
                "password": "password123",
                "full_name": "No Leak User"
            }
        )

        login_response = client.post(
            "/auth/login",
            json={
                "email": "noleak@example.com",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]

        # Get current user
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        data = response.json()
        assert "password" not in data
        assert "hashed_password" not in data
