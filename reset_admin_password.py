import sqlite3
from auth_utils import verify_password

conn = sqlite3.connect("walter_users.db")
cursor = conn.cursor()

email = "walter@example.com"
entered_password = "admin123"

cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
result = cursor.fetchone()

if result:
    password_hash = result[0]
    if verify_password(entered_password, password_hash):
        print("✅ Password is correct.")
    else:
        print("❌ Password does NOT match.")
else:
    print("❌ User not found.")
