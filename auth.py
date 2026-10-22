# auth.py
import hashlib
from database import get_connection
from models import Lecturer, CampusAdmin, SystemOperator


def hash_password(password):
    """
    Hash a password using SHA-256.
    (In production, use bcrypt or passlib — but this is fine for the assignment.)
    """
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password, role, campus_id=None):
    """
    Register a new user.
    Returns (success: bool, message: str).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role, campus_id) VALUES (?, ?, ?, ?)",
            (username, hash_password(password), role, campus_id),
        )
        conn.commit()
        return True, "Registration successful."
    except Exception as e:
        return False, f"Registration failed: {e}"
    finally:
        conn.close()


def login_user(username, password):
    """
    Authenticate a user.
    Returns a User object (Lecturer / CampusAdmin / SystemOperator) or None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, hash_password(password)),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    role = row["role"]
    if role == "lecturer":
        return Lecturer(row["id"], row["username"], row["campus_id"])
    elif role == "admin":
        return CampusAdmin(row["id"], row["username"], row["campus_id"])
    elif role == "operator":
        return SystemOperator(row["id"], row["username"])
    return None