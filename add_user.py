import sqlite3
import bcrypt
import getpass

DB_PATH = "walter_users.db"

def reset_and_add_user(email, name, plain_password):
    hashed_pw = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # 💥 Drop old table (if schema mismatch)
        cursor.execute("DROP TABLE IF EXISTS users")

        # ✅ Recreate the correct table
        cursor.execute("""
            CREATE TABLE users (
                email TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL

            )
        """)

        # ✅ Insert new user
        cursor.execute(
            "INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)",
            (email, name, hashed_pw),
        )

        conn.commit()
    print(f"\n✅ User '{name}' ({email}) added successfully.\n")

if __name__ == "__main__":
    print("🔐 Add a New User")
    email = input("Email: ").strip()
    name = input("Name: ").strip()
    password = getpass.getpass("Password (input hidden): ").strip()
    confirm = getpass.getpass("Confirm Password: ").strip()

    if password != confirm:
        print("❌ Passwords do not match. Please try again.")
    elif not email or not name or not password:
        print("❌ All fields are required.")
    else:
        reset_and_add_user(email, name, password)
