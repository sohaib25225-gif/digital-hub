#!/usr/bin/env python3
"""
Script to create an admin user for testing purposes.

Usage:
    python scripts/create_admin_user.py

This creates a test admin user with these credentials:
    Email: admin@test.com
    Password: admin123456
    Role: ADMIN
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.models.user import User, UserRole


def create_admin_user():
    """Create a test admin user in the database."""

    # Create database engine
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.email == "admin@test.com").first()

        if existing_admin:
            print("[OK] Admin user 'admin@test.com' already exists")
            print(f"  ID: {existing_admin.id}")
            print(f"  Role: {existing_admin.role}")

            # Update to admin if not already
            if existing_admin.role != UserRole.ADMIN:
                existing_admin.role = UserRole.ADMIN
                db.commit()
                print("  -> Updated role to ADMIN")
        else:
            # Create new admin user
            admin_user = User(
                email="admin@test.com",
                hashed_password=get_password_hash("admin123456"),
                full_name="Test Admin User",
                role=UserRole.ADMIN,
                is_active=True,
            )

            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            print("[OK] Admin user created successfully!")
            print(f"  Email: admin@test.com")
            print(f"  Password: admin123456")
            print(f"  ID: {admin_user.id}")
            print(f"  Role: {admin_user.role}")

        print("\nTo get an admin JWT token:")
        print("  1. POST to /auth/login with:")
        print('     {"email": "admin@test.com", "password": "admin123456"}')
        print("  2. Copy the 'access_token' from the response")
        print("  3. In Swagger UI, click 'Authorize' and paste ONLY the token")
        print("     (without quotes, without 'Bearer' prefix)")

    except Exception as e:
        print(f"[ERROR] Error creating admin user: {e}")
        db.rollback()
        return 1
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(create_admin_user())
