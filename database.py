# database.py
import sqlite3
import hashlib


DB_NAME = "campus_booking.db"


def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def initialize_database():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Campuses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            location TEXT
        )
    """)

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            campus_id INTEGER,
            FOREIGN KEY (campus_id) REFERENCES campuses(id)
        )
    """)

    # Resources table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            campus_id INTEGER NOT NULL,
            capacity INTEGER,
            UNIQUE(name, campus_id),
            FOREIGN KEY (campus_id) REFERENCES campuses(id)
        )
    """)

    # Bookings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resource_id INTEGER NOT NULL,
            campus_id INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            duration INTEGER NOT NULL,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (resource_id) REFERENCES resources(id),
            FOREIGN KEY (campus_id) REFERENCES campuses(id)
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialised successfully.")


def seed_data():
    """Insert default campuses and default accounts (with hashed passwords)."""
    def _hash(p):
        return hashlib.sha256(p.encode()).hexdigest()

    conn = get_connection()
    cursor = conn.cursor()


    # --- Campuses ---
    campuses = [
        ("Centurion Campus", "Centurion, Gauteng"),
        ("Pretoria Campus", "Pretoria Central, Gauteng"),
        ("Musgrave Campus", "Musgrave, Durban"),
        ("Bryanston Campus", "Bryanston, Johannesburg"),
        ("Cape Town Campus", "Cape Town CBD"),
    ]
    for name, location in campuses:
        try:
            cursor.execute(
                "INSERT INTO campuses (name, location) VALUES (?, ?)",
                (name, location),
            )
        except sqlite3.IntegrityError:
            pass

    # --- Default system operator ---
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role, campus_id) VALUES (?, ?, ?, ?)",
            ("operator", _hash("admin123"), "operator", None),
        )
    except sqlite3.IntegrityError:
        pass

    # --- Default campus admin for JHB ---
    cursor.execute("SELECT id FROM campuses WHERE name = ?", ("Bryanston Campus",))
    row = cursor.fetchone()
    if row:
        try:
            cursor.execute(
                "INSERT INTO users (username, password, role, campus_id) VALUES (?, ?, ?, ?)",
            ("admin_bry", _hash("admin123"), "admin", row["id"]),
            )
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
    print("Seed data inserted.")


if __name__ == "__main__":
    initialize_database()
    seed_data()