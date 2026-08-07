import os
import sqlite3
from fastapi import  Request, Form, Depends, HTTPException, status
from passlib.context import CryptContext


# Secret key for signing session cookies
DB_FILE = "users.db"

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    """Connects to SQLite database and returns a database connection."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    """Creates the users table if it doesn't exist and seeds a default admin."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                is_active INTEGER NOT NULL DEFAULT 1
            )
        """)
        
        # Check if default admin exists; if not, create one
        cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
        if not cursor.fetchone():
            hashed_pw = pwd_context.hash("admin123")
            cursor.execute(
                "INSERT INTO users (username, hashed_password, role) VALUES (?, ?, ?)",
                ("admin", hashed_pw, "admin")
            )
            print("--> Seeded default admin user: 'admin' / password: 'admin123'")
        conn.commit()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hashes a password string using bcrypt."""
    return pwd_context.hash(password)

def get_user_by_id(user_id: int):
    """Retrieves a user row from the database by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, is_active FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()

def get_user_by_username(username: str):
    """Retrieves a user row from the database by username."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()

async def get_current_user(request: Request):
    """
    Dependency that retrieves the currently logged-in user from session cookie.
    Redirects unauthenticated users to the /login page.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"}
        )
    
    user = get_user_by_id(user_id)
    if not user or not user["is_active"]:
        # Clear invalid session and redirect
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"}
        )
    return user

async def require_admin(current_user=Depends(get_current_user)):
    """Dependency ensuring the authenticated user has an 'admin' role."""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Admin privileges required."
        )
    return current_user
