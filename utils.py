import os
import json
from datetime import datetime

REQUESTS_FILE = "pending_requests.json"
APPROVED_USERS_FILE = "access_logs/approved_users.csv"

def load_pending_requests():
    if not os.path.exists(REQUESTS_FILE):
        return []
    try:
        with open(REQUESTS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_pending_requests(requests):
    with open(REQUESTS_FILE, "w") as f:
        json.dump(requests, f, indent=2)

def log_approved_user(name, email, goals, password):
    os.makedirs("access_logs", exist_ok=True)
    with open(APPROVED_USERS_FILE, "a") as f:
        f.write(f"{name},{email},{goals},{password},{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
