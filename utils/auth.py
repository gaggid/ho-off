# app/utils/auth.py

import hashlib
from models.user import User
from config import ADMIN_USERNAME, ADMIN_PASSWORD

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin_user() -> User:
    """Create default admin user"""
    return User(
        username=ADMIN_USERNAME,
        password=hash_password(ADMIN_PASSWORD),
        email="admin@company.com",
        department="Administration",
        is_admin=True
    )

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify if provided password matches stored password"""
    return stored_password == hash_password(provided_password)