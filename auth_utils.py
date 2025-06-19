import sqlite3
import bcrypt

def hash_password(password):
    """Hash a password for storing."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def add_user(email, name, password_hash):
    """Add a new user to the existing database schema using 'password' column."""
    conn = sqlite3.connect("walter_users.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)",
        (email, name, password_hash),
    )

    conn.commit()
    conn.close()

def get_users():
    """Fetch users from the database and format them for Streamlit Authenticator."""
    conn = sqlite3.connect("walter_users.db")
    rows = conn.execute("SELECT email, name, password_hash FROM users").fetchall()
    conn.close()
    return {
        email: {"name": name, "password": password_hash}
        for email, name, password_hash in rows
    }

def delete_user(email):
    """Delete a user by email."""
    conn = sqlite3.connect("walter_users.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.commit()
    conn.close()

def update_password(email, new_password_hash):
    """Update the password hash for an existing user."""
    conn = sqlite3.connect("walter_users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_password_hash, email))
    conn.commit()
    conn.close()



def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

import os
from datetime import datetime

def log_temp_password(email, password):
    os.makedirs("access_logs", exist_ok=True)
    filepath = "access_logs/temp_passwords.csv"
    lines = []

    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            lines = [line for line in f.readlines() if not line.startswith(email + ",")]

    lines.append(f"{email},{password}\n")

    with open(filepath, "w") as f:
        f.writelines(lines)

def update_approved_user_password(email, new_password):
    filepath = "access_logs/approved_users.csv"
    if not os.path.exists(filepath):
        return

    updated_lines = []
    with open(filepath, "r") as f:
        for line in f:
            parts = line.strip().split(",", 4)
            if len(parts) == 5 and parts[1] == email:
                parts[3] = new_password
                parts[4] = datetime.now().strftime('%Y-%m-%d %H:%M')
            updated_lines.append(",".join(parts))

    with open(filepath, "w") as f:
        f.write("\n".join(updated_lines) + "\n")
