"""
Test to demonstrate the Swagger UI token format issue.

This test shows what happens when a JWT token is surrounded by quotes,
which can occur if the user pastes the token incorrectly in Swagger UI.
"""
import pytest
from fastapi import status


class TestSwaggerTokenFormat:
    """Test cases for token format issues that can occur with Swagger UI."""

    def test_token_with_quotes_fails(self, client):
        """
        Test that a valid token surrounded by quotes fails authentication.

        This demonstrates the issue when users paste tokens incorrectly in Swagger UI.
        """
        # Register and login to get a valid token
        client.post(
            "/auth/register",
            json={
                "email": "tokentest@example.com",
                "password": "password123",
                "full_name": "Token Test User"
            }
        )

        login_response = client.post(
            "/auth/login",
            json={
                "email": "tokentest@example.com",
                "password": "password123"
            }
        )
        valid_token = login_response.json()["access_token"]

        # Correct usage: token without quotes
        response_correct = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert response_correct.status_code == status.HTTP_200_OK

        # Incorrect usage: token surrounded by quotes (Swagger UI mistake)
        response_with_quotes = client.get(
            "/auth/me",
            headers={"Authorization": f'Bearer "{valid_token}"'}
        )
        assert response_with_quotes.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_with_quotes.json()["detail"] == "Could not validate credentials"

    def test_admin_endpoint_correct_token_student_role(self, client):
        """
        Test that a correctly formatted token with student role returns 403, not 401.

        This verifies the authentication flow:
        - 401: token is invalid/malformed
        - 403: token is valid but user lacks permissions
        """
        # Register and login as student
        client.post(
            "/auth/register",
            json={
                "email": "student_test@example.com",
                "password": "password123",
                "full_name": "Student Test"
            }
        )

        login_response = client.post(
            "/auth/login",
            json={
                "email": "student_test@example.com",
                "password": "password123"
            }
        )
        student_token = login_response.json()["access_token"]

        # Try to access admin endpoint with student token
        response = client.get(
            "/admin/health",
            headers={"Authorization": f"Bearer {student_token}"}
        )

        # Should get 403 FORBIDDEN (not 401) because token is valid but user is not admin
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]

    def test_admin_endpoint_quoted_token(self, client, db_session):
        """
        Test that an admin token with quotes returns 401, not 403.

        This shows that even with an admin user, quoted tokens fail at authentication level.
        """
        from app.db.models.user import User, UserRole

        # Register and make user admin
        client.post(
            "/auth/register",
            json={
                "email": "admin_test@example.com",
                "password": "password123",
                "full_name": "Admin Test"
            }
        )

        user = db_session.query(User).filter(User.email == "admin_test@example.com").first()
        user.role = UserRole.ADMIN
        db_session.commit()

        # Login to get token
        login_response = client.post(
            "/auth/login",
            json={
                "email": "admin_test@example.com",
                "password": "password123"
            }
        )
        admin_token = login_response.json()["access_token"]

        # Correct token format should work
        response_correct = client.get(
            "/admin/health",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response_correct.status_code == status.HTTP_200_OK

        # Token with quotes should fail at authentication level (401, not 403)
        response_quoted = client.get(
            "/admin/health",
            headers={"Authorization": f'Bearer "{admin_token}"'}
        )
        assert response_quoted.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_quoted.json()["detail"] == "Could not validate credentials"
